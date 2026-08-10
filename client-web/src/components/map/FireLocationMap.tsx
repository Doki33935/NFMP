import { useEffect, useEffectEvent, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  addOrenburgDistricts,
  createOpenStreetMap,
  findAddressByCoordinates,
  findAddressInOrenburg,
  formatCoordinate,
  parseMapCoordinates,
  type MapCoordinates,
} from '@/lib/openStreetMap'

type FireLocationMapProps = {
  address: string
  latitude: string
  longitude: string
  onAddressChange: (value: string) => void
  onLatitudeChange: (value: string) => void
  onLongitudeChange: (value: string) => void
}

type MapStatus = 'loading' | 'ready' | 'error'

export function FireLocationMap({
  address,
  latitude,
  longitude,
  onAddressChange,
  onLatitudeChange,
  onLongitudeChange,
}: FireLocationMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markerRef = useRef<L.CircleMarker | null>(null)
  const requestNumberRef = useRef(0)
  const viewWasChangedRef = useRef(false)
  const placeMarkerRef = useRef<(coordinates: MapCoordinates, caption?: string) => void>(() => {})
  const [status, setStatus] = useState<MapStatus>('loading')
  const [searching, setSearching] = useState(false)
  const [message, setMessage] = useState('')

  const getInitialSelection = useEffectEvent(() => ({ address, latitude, longitude }))
  const setCoordinatesFromMap = useEffectEvent((coordinates: MapCoordinates) => {
    onLatitudeChange(formatCoordinate(coordinates[0]))
    onLongitudeChange(formatCoordinate(coordinates[1]))
  })
  const setResolvedAddress = useEffectEvent((value: string) => onAddressChange(value))

  useEffect(() => {
    if (!containerRef.current) return
    let disposed = false

    try {
      const map = createOpenStreetMap(containerRef.current)
      mapRef.current = map
      placeMarkerRef.current = (coordinates, caption = 'Место пожара') => {
        if (markerRef.current) {
          markerRef.current.setLatLng(coordinates)
          markerRef.current.unbindTooltip().bindTooltip(caption, { direction: 'top' })
          markerRef.current.bringToFront()
          return
        }

        markerRef.current = L.circleMarker(coordinates, {
          radius: 9,
          color: '#ffffff',
          weight: 3,
          fillColor: '#dc2626',
          fillOpacity: 1,
        }).bindTooltip(caption, { direction: 'top' }).addTo(map)
      }

      const initialSelection = getInitialSelection()
      const initialCoordinates = parseMapCoordinates(initialSelection.latitude, initialSelection.longitude)
      if (initialCoordinates) {
        viewWasChangedRef.current = true
        placeMarkerRef.current(initialCoordinates, initialSelection.address || 'Место пожара')
        map.setView(initialCoordinates, 14)
      }

      map.on('dragstart zoomstart', () => {
        viewWasChangedRef.current = true
      })

      map.on('click', ({ latlng }: L.LeafletMouseEvent) => {
        const coordinates: MapCoordinates = [latlng.lat, latlng.lng]
        const requestNumber = ++requestNumberRef.current
        viewWasChangedRef.current = true
        setCoordinatesFromMap(coordinates)
        placeMarkerRef.current(coordinates)
        setMessage('Точка выбрана, определяю адрес...')

        void findAddressByCoordinates(coordinates)
          .then((resolvedAddress) => {
            if (requestNumber !== requestNumberRef.current) return
            if (resolvedAddress) {
              setResolvedAddress(resolvedAddress)
              placeMarkerRef.current(coordinates, resolvedAddress)
              setMessage(resolvedAddress)
            } else {
              setMessage('Точка выбрана, адрес не определен')
            }
          })
          .catch(() => {
            if (requestNumber === requestNumberRef.current) {
              setMessage('Точка выбрана, сервис адресов временно недоступен')
            }
          })
      })

      void addOrenburgDistricts(map, () => disposed)
        .then((districts) => {
          if (districts && !viewWasChangedRef.current && districts.getBounds().isValid()) {
            map.fitBounds(districts.getBounds(), { padding: [16, 16], maxZoom: 7 })
          }
        })
        .catch(() => {
          if (!disposed) setMessage('Карта загружена без границ районов')
        })
      const readyFrame = window.requestAnimationFrame(() => setStatus('ready'))

      return () => {
        disposed = true
        window.cancelAnimationFrame(readyFrame)
        requestNumberRef.current += 1
        map.remove()
        mapRef.current = null
        markerRef.current = null
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
    const coordinates = parseMapCoordinates(latitude, longitude)
    if (!coordinates || !mapRef.current) return
    placeMarkerRef.current(coordinates, address || 'Место пожара')
  }, [address, latitude, longitude])

  const findAddress = async () => {
    const map = mapRef.current
    const query = address.trim()
    if (!map || !query) return

    const requestNumber = ++requestNumberRef.current
    setSearching(true)
    setMessage('Ищу адрес в Оренбургской области...')
    try {
      const found = await findAddressInOrenburg(query)
      if (requestNumber !== requestNumberRef.current) return
      if (!found) {
        setMessage('Адрес в Оренбургской области не найден')
        return
      }

      onLatitudeChange(formatCoordinate(found.coordinates[0]))
      onLongitudeChange(formatCoordinate(found.coordinates[1]))
      onAddressChange(found.address)
      placeMarkerRef.current(found.coordinates, found.address)
      viewWasChangedRef.current = true
      map.setView(found.coordinates, 15)
      setMessage(found.address)
    } catch (error) {
      if (requestNumber === requestNumberRef.current) {
        setMessage(error instanceof Error ? error.message : 'Не удалось выполнить поиск адреса')
      }
    } finally {
      if (requestNumber === requestNumberRef.current) setSearching(false)
    }
  }

  return (
    <div className="space-y-3 md:col-span-2">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="text-sm font-medium">Точка пожара</p>
          <p className="text-xs text-text-muted mt-0.5">Нажмите на карту или найдите введенный адрес</p>
        </div>
        <button
          type="button"
          onClick={findAddress}
          disabled={status !== 'ready' || searching || !address.trim()}
          className="px-3 py-2 rounded-md bg-primary text-sm text-white hover:bg-primary-hover disabled:opacity-45 disabled:cursor-not-allowed transition-colors cursor-pointer"
        >
          {searching ? 'Ищу...' : 'Найти адрес'}
        </button>
      </div>

      <div className="relative h-[360px] md:h-[430px] overflow-hidden rounded-md border border-border bg-background">
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

      <div className="min-h-5 text-xs text-text-muted leading-5">
        {message || 'Карта и поиск адресов: OpenStreetMap. Границы: НИУ ВШЭ / OpenStreetMap / Росстат'}
      </div>
    </div>
  )
}
