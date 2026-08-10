import { useEffect, useEffectEvent, useMemo, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import type { FireResponse } from '@/types/fire'
import {
  ORENBURG_CENTER,
  addOrenburgDistricts,
  createOpenStreetMap,
  type MapCoordinates,
} from '@/lib/openStreetMap'

type MonitoringMapProps = {
  fires: FireResponse[]
  onOpen: (id: number) => void
}

type MapStatus = 'loading' | 'ready' | 'error'

export function MonitoringMap({ fires, onOpen }: MonitoringMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.MarkerClusterGroup | null>(null)
  const [status, setStatus] = useState<MapStatus>('loading')
  const [message, setMessage] = useState('')

  const openFire = useEffectEvent((id: number) => onOpen(id))

  const firesWithCoordinates = useMemo(
    () => fires.filter((fire) => getFireCoordinates(fire) !== null),
    [fires]
  )

  useEffect(() => {
    if (!containerRef.current) return
    let disposed = false

    try {
      const map = createOpenStreetMap(containerRef.current)
      const markers = L.markerClusterGroup({
        showCoverageOnHover: false,
        maxClusterRadius: 64,
        spiderfyOnMaxZoom: true,
        animate: false,
        animateAddingMarkers: false,
        chunkedLoading: true,
        chunkInterval: 100,
        chunkDelay: 30,
        removeOutsideVisibleBounds: true,
      })
      markers.addTo(map)
      mapRef.current = map
      markersRef.current = markers

      void addOrenburgDistricts(map, () => disposed).catch(() => {
        if (!disposed) setMessage('Карта загружена без границ районов')
      })
      const readyFrame = window.requestAnimationFrame(() => setStatus('ready'))

      return () => {
        disposed = true
        window.cancelAnimationFrame(readyFrame)
        map.remove()
        mapRef.current = null
        markersRef.current = null
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Не удалось загрузить карту'
      const errorFrame = window.requestAnimationFrame(() => {
        setStatus('error')
        setMessage(errorMessage)
      })
      return () => window.cancelAnimationFrame(errorFrame)
    }
  }, [])

  useEffect(() => {
    const markers = markersRef.current
    const map = mapRef.current
    if (!markers || !map) return

    const timer = window.setTimeout(() => renderMarkers(markers, map, fires, openFire), 80)
    return () => window.clearTimeout(timer)
  }, [fires])

  return (
    <section className="bg-surface rounded-lg border border-border overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h2 className="font-semibold">Карта пожаров</h2>
          <p className="text-xs text-text-muted mt-0.5">
            На карте {firesWithCoordinates.length} из {fires.length}; без точки {fires.length - firesWithCoordinates.length}
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-text-muted">
          <Legend color="bg-primary" label="Открыт" />
          <Legend color="bg-warning" label="На проверке" />
          <Legend color="bg-success" label="Оформлен" />
        </div>
      </div>

      <div className="relative h-[430px] md:h-[560px] bg-background">
        <div ref={containerRef} className="absolute inset-0 z-0" />
        {status === 'loading' && (
          <div className="absolute inset-0 z-10 grid place-items-center bg-background text-sm text-text-muted">
            Загрузка карты...
          </div>
        )}
        {status === 'error' && (
          <div className="absolute inset-0 z-10 grid place-items-center bg-background p-6 text-center">
            <div>
              <p className="text-sm font-medium text-text">Карта недоступна</p>
              <p className="text-xs text-text-muted mt-2">{message}</p>
            </div>
          </div>
        )}
      </div>

      <div className="px-4 py-2 border-t border-border text-xs text-text-muted">
        {message || 'Карта: OpenStreetMap. Границы: НИУ ВШЭ / OpenStreetMap / Росстат, 2021'}
      </div>
    </section>
  )
}

function renderMarkers(
  markers: L.MarkerClusterGroup,
  map: L.Map,
  fires: FireResponse[],
  onOpen: (id: number) => void
) {
  markers.clearLayers()
  const mapMarkers: L.Marker[] = []
  const bounds = L.latLngBounds([])

  for (const fire of fires) {
    const coordinates = getFireCoordinates(fire)
    if (!coordinates) continue

    const marker = L.marker(coordinates, {
      icon: L.divIcon({
        className: `fire-map-marker fire-map-marker--${statusClass(fire.status)}`,
        html: '<span></span>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      }),
      title: `Пожар #${fire.id}`,
      keyboard: true,
    })
    marker.bindTooltip(() => createFireTooltip(fire), { direction: 'top' })
    marker.on('click', () => onOpen(fire.id))
    mapMarkers.push(marker)
    bounds.extend(coordinates)
  }

  markers.addLayers(mapMarkers)

  if (bounds.isValid()) {
    if (bounds.getNorthEast().equals(bounds.getSouthWest())) {
      map.setView(bounds.getCenter(), 13)
    } else {
      map.fitBounds(bounds, { padding: [44, 44], maxZoom: 15 })
    }
  } else {
    map.setView(ORENBURG_CENTER, 7)
  }
}

function createFireTooltip(fire: FireResponse): HTMLElement {
  const tooltip = document.createElement('div')
  const title = document.createElement('strong')
  title.textContent = `Пожар #${fire.id}`
  tooltip.append(title, document.createElement('br'))
  tooltip.append(document.createTextNode(fire.address || 'Адрес не указан'))
  tooltip.append(document.createElement('br'))
  tooltip.append(document.createTextNode(statusLabel(fire.status)))
  return tooltip
}

function getFireCoordinates(fire: FireResponse): MapCoordinates | null {
  const latitude = Number(fire.latitude)
  const longitude = Number(fire.longitude)
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null
  if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) return null
  return [latitude, longitude]
}

function statusClass(status: string): string {
  const classes: Record<string, string> = {
    OPEN: 'open',
    IN_REVIEW: 'review',
    COMPLETED: 'completed',
  }
  return classes[status] || 'unknown'
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    OPEN: 'Открыт',
    IN_REVIEW: 'На проверке',
    COMPLETED: 'Оформлен',
  }
  return labels[status] || status
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
      {label}
    </span>
  )
}
