import L from 'leaflet'
import type { FeatureCollection, GeoJsonObject, Point } from 'geojson'

export type MapCoordinates = [number, number]

export const ORENBURG_CENTER: MapCoordinates = [51.7682, 55.0969]
export const ORENBURG_BOUNDS: [MapCoordinates, MapCoordinates] = [
  [50.45, 50.70],
  [54.40, 61.75],
]

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org'
const NOMINATIM_INTERVAL_MS = 1_100

type GeocodingResult = {
  coordinates: MapCoordinates
  address: string
}

type SettlementPlace = 'city' | 'town' | 'village' | 'hamlet'

type SettlementProperties = {
  name: string
  place: SettlementPlace
  population?: number
}

type SettlementCollection = FeatureCollection<Point, SettlementProperties>

export type BaseMapStatus = 'openstreetmap' | 'fallback' | 'unavailable'

let districtsPromise: Promise<GeoJsonObject> | null = null
let settlementsPromise: Promise<SettlementCollection> | null = null
let geocodingQueue: Promise<void> = Promise.resolve()
let lastGeocodingRequestAt = 0

class LocalBackgroundLayer extends L.GridLayer {
  public createTile(coordinates: L.Coords): HTMLElement {
    const tile = document.createElement('canvas')
    const size = this.getTileSize()
    tile.width = size.x
    tile.height = size.y
    const context = tile.getContext('2d')
    if (context) {
      context.fillStyle = (coordinates.x + coordinates.y) % 2 === 0 ? '#eef2f3' : '#edf1f2'
      context.fillRect(0, 0, tile.width, tile.height)
      context.strokeStyle = '#dbe2e5'
      context.lineWidth = 1
      for (let offset = 0; offset <= tile.width; offset += 64) {
        context.beginPath()
        context.moveTo(offset, 0)
        context.lineTo(offset, tile.height)
        context.stroke()
        context.beginPath()
        context.moveTo(0, offset)
        context.lineTo(tile.width, offset)
        context.stroke()
      }
    }
    return tile
  }
}

export function createOpenStreetMap(
  container: HTMLElement,
  onBaseMapStatus?: (status: BaseMapStatus) => void
): L.Map {
  const map = L.map(container, {
    center: ORENBURG_CENTER,
    zoom: 7,
    minZoom: 5,
    maxBounds: ORENBURG_BOUNDS,
    maxBoundsViscosity: 0.8,
    preferCanvas: true,
  })

  // Keep the required map data attribution, but remove Leaflet's flag-shaped logo.
  map.attributionControl.setPrefix(false)

  const localBaseLayer = new LocalBackgroundLayer({
    attribution: 'Населённые пункты: &copy; OpenStreetMap',
  })
  localBaseLayer.addTo(map)

  const primaryLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    crossOrigin: true,
  })
  let primaryErrors = 0
  let fallbackStarted = false

  const startFallback = () => {
    if (fallbackStarted) return
    fallbackStarted = true
    map.removeLayer(primaryLayer)

    const fallbackLayer = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      {
        subdomains: 'abcd',
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        crossOrigin: true,
      }
    )
    let fallbackErrors = 0
    fallbackLayer.on('load', () => onBaseMapStatus?.('fallback'))
    fallbackLayer.on('tileerror', () => {
      fallbackErrors += 1
      if (fallbackErrors === 4) onBaseMapStatus?.('unavailable')
    })
    fallbackLayer.addTo(map)
  }

  primaryLayer.on('load', () => onBaseMapStatus?.('openstreetmap'))
  primaryLayer.on('tileerror', () => {
    primaryErrors += 1
    if (primaryErrors === 4) startFallback()
  })
  primaryLayer.addTo(map)
  L.control.scale({ imperial: false, metric: true }).addTo(map)

  return map
}

export async function addOrenburgDistricts(
  map: L.Map,
  isCancelled: () => boolean = () => false
): Promise<L.GeoJSON | null> {
  const collection = await loadDistricts()
  if (isCancelled()) return null

  if (!map.getPane('districtLabels')) {
    const pane = map.createPane('districtLabels')
    pane.style.zIndex = '410'
    pane.style.pointerEvents = 'none'
  }

  const districtCenters: Array<{ coordinates: L.LatLng; name: string }> = []
  const districts = L.geoJSON(collection, {
    style: {
      color: '#c24141',
      weight: 1,
      opacity: 0.82,
      fillColor: '#dce8df',
      fillOpacity: 0.24,
    },
    onEachFeature: (feature, layer) => {
      const name = feature.properties?.name
      if (typeof name === 'string' && name) {
        layer.bindTooltip(name, { sticky: true })
        if (layer instanceof L.Polygon) {
          districtCenters.push({
            coordinates: layer.getBounds().getCenter(),
            name: normalizeDistrictName(name),
          })
        }
      }
    },
  }).addTo(map)

  const labels = L.layerGroup().addTo(map)
  const renderLabels = () => {
    if (isCancelled()) return
    labels.clearLayers()

    const zoom = map.getZoom()
    const bounds = map.getBounds().pad(0.1)
    const occupied: LabelBox[] = []
    const labelLimit = zoom <= 5 ? 18 : zoom === 6 ? 30 : districtCenters.length

    for (const district of districtCenters) {
      if (occupied.length >= labelLimit || !bounds.contains(district.coordinates)) continue

      const point = map.latLngToContainerPoint(district.coordinates)
      const width = Math.min(150, Math.max(70, 18 + [...district.name].length * 5.5))
      const box = {
        left: point.x - width / 2,
        top: point.y - 9,
        right: point.x + width / 2,
        bottom: point.y + 9,
      }
      if (occupied.some((item) => boxesOverlap(item, box))) continue
      occupied.push(box)

      const content = document.createElement('span')
      content.className = 'orenburg-district-label'
      content.textContent = district.name
      L.marker(district.coordinates, {
        pane: 'districtLabels',
        interactive: false,
        keyboard: false,
        icon: L.divIcon({
          className: 'orenburg-district-icon',
          html: content,
          iconAnchor: [0, 0],
        }),
      }).addTo(labels)
    }
  }

  map.on('moveend zoomend', renderLabels)
  renderLabels()
  return districts
}

export async function addOrenburgSettlements(
  map: L.Map,
  isCancelled: () => boolean = () => false
): Promise<L.LayerGroup | null> {
  const collection = await loadSettlements()
  if (isCancelled()) return null

  if (!map.getPane('settlementLabels')) {
    const pane = map.createPane('settlementLabels')
    pane.style.zIndex = '450'
    pane.style.pointerEvents = 'none'
  }

  const labels = L.layerGroup().addTo(map)
  const render = () => {
    if (isCancelled()) return
    labels.clearLayers()

    const zoom = map.getZoom()
    const bounds = map.getBounds().pad(0.15)
    const candidates = collection.features
      .filter((feature) => {
        const [longitude, latitude] = feature.geometry.coordinates
        return bounds.contains([latitude, longitude]) && settlementIsVisible(feature.properties, zoom)
      })
      .sort((first, second) => {
        const rankDifference = settlementRank(first.properties.place) - settlementRank(second.properties.place)
        if (rankDifference !== 0) return rankDifference
        return (second.properties.population || 0) - (first.properties.population || 0)
          || first.properties.name.localeCompare(second.properties.name, 'ru')
      })

    const occupied: LabelBox[] = []
    const labelLimit = zoom <= 7 ? 80 : zoom === 8 ? 120 : zoom === 9 ? 180 : 260

    for (const feature of candidates) {
      if (occupied.length >= labelLimit) break
      const [longitude, latitude] = feature.geometry.coordinates
      const point = map.latLngToContainerPoint([latitude, longitude])
      const width = Math.min(190, Math.max(52, 22 + [...feature.properties.name].length * 6.5))
      const box = { left: point.x - 6, top: point.y - 10, right: point.x + width, bottom: point.y + 11 }
      if (occupied.some((item) => boxesOverlap(item, box))) continue
      occupied.push(box)

      const content = document.createElement('span')
      content.className = `orenburg-place-label orenburg-place-label--${feature.properties.place}`
      const dot = document.createElement('span')
      dot.className = 'orenburg-place-dot'
      const name = document.createElement('span')
      name.textContent = feature.properties.name
      content.append(dot, name)

      L.marker([latitude, longitude], {
        pane: 'settlementLabels',
        interactive: false,
        keyboard: false,
        icon: L.divIcon({
          className: 'orenburg-place-icon',
          html: content,
          iconAnchor: [4, 4],
        }),
      }).addTo(labels)
    }
  }

  map.on('moveend zoomend', render)
  render()
  return labels
}

export async function findAddressInOrenburg(query: string): Promise<GeocodingResult | null> {
  const value = query.trim()
  if (!value) return null

  const request = value.toLocaleLowerCase('ru-RU').includes('оренбургская область')
    ? value
    : `Оренбургская область, ${value}`
  const params = new URLSearchParams({
    q: request,
    format: 'jsonv2',
    limit: '1',
    countrycodes: 'ru',
    viewbox: '50.70,54.40,61.75,50.45',
    bounded: '1',
    'accept-language': 'ru',
  })

  const results = await requestNominatim<NominatimSearchResult[]>(`/search?${params}`)
  const found = results[0]
  if (!found) return null

  const coordinates = parseNumericCoordinates(found.lat, found.lon)
  if (!coordinates || !isInsideOrenburgBounds(coordinates)) return null
  return { coordinates, address: found.display_name || value }
}

export async function findAddressByCoordinates(coordinates: MapCoordinates): Promise<string | null> {
  const params = new URLSearchParams({
    lat: String(coordinates[0]),
    lon: String(coordinates[1]),
    format: 'jsonv2',
    zoom: '18',
    addressdetails: '1',
    'accept-language': 'ru',
  })
  const result = await requestNominatim<NominatimReverseResult>(`/reverse?${params}`)
  return result.display_name || null
}

export function parseMapCoordinates(latitude: string, longitude: string): MapCoordinates | null {
  return parseNumericCoordinates(latitude.trim().replace(',', '.'), longitude.trim().replace(',', '.'))
}

export function formatCoordinate(value: number): string {
  return String(Math.round(value * 100_000) / 100_000)
}

function loadDistricts(): Promise<GeoJsonObject> {
  if (!districtsPromise) {
    const base = import.meta.env.BASE_URL.endsWith('/')
      ? import.meta.env.BASE_URL
      : `${import.meta.env.BASE_URL}/`
    districtsPromise = fetch(`${base}data/orenburg-municipalities.geojson`)
      .then((response) => {
        if (!response.ok) throw new Error('Не удалось загрузить границы районов')
        return response.json() as Promise<GeoJsonObject>
      })
  }
  return districtsPromise
}

function loadSettlements(): Promise<SettlementCollection> {
  if (!settlementsPromise) {
    const base = import.meta.env.BASE_URL.endsWith('/')
      ? import.meta.env.BASE_URL
      : `${import.meta.env.BASE_URL}/`
    settlementsPromise = fetch(`${base}data/orenburg-settlements.geojson`)
      .then((response) => {
        if (!response.ok) throw new Error('Не удалось загрузить населённые пункты')
        return response.json() as Promise<SettlementCollection>
      })
  }
  return settlementsPromise
}

function settlementRank(place: SettlementPlace): number {
  return { city: 0, town: 1, village: 2, hamlet: 3 }[place]
}

function normalizeDistrictName(name: string): string {
  return name
    .replace(/\s+муниципальный район$/i, ' район')
    .replace(/^городской округ город\s+/i, 'г. ')
}

function settlementIsVisible(properties: SettlementProperties, zoom: number): boolean {
  if (properties.place === 'city') return true
  if (properties.place === 'town') return zoom >= 7
  if (properties.place === 'village') return zoom >= 9 || (zoom >= 8 && (properties.population || 0) >= 1000)
  return zoom >= 11
}

type LabelBox = {
  left: number
  top: number
  right: number
  bottom: number
}

function boxesOverlap(first: LabelBox, second: LabelBox): boolean {
  const padding = 4
  return first.left - padding < second.right
    && first.right + padding > second.left
    && first.top - padding < second.bottom
    && first.bottom + padding > second.top
}

function requestNominatim<T>(path: string): Promise<T> {
  const result = geocodingQueue.then(async () => {
    const delay = Math.max(0, NOMINATIM_INTERVAL_MS - (Date.now() - lastGeocodingRequestAt))
    if (delay > 0) await new Promise((resolve) => window.setTimeout(resolve, delay))
    lastGeocodingRequestAt = Date.now()

    const response = await fetch(`${NOMINATIM_BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error('Сервис поиска адресов временно недоступен')
    return response.json() as Promise<T>
  })

  geocodingQueue = result.then(() => undefined, () => undefined)
  return result
}

function parseNumericCoordinates(latitude: string, longitude: string): MapCoordinates | null {
  if (!latitude.trim() || !longitude.trim()) return null
  const lat = Number(latitude)
  const lon = Number(longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null
  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return null
  return [lat, lon]
}

function isInsideOrenburgBounds([latitude, longitude]: MapCoordinates): boolean {
  return latitude >= ORENBURG_BOUNDS[0][0]
    && latitude <= ORENBURG_BOUNDS[1][0]
    && longitude >= ORENBURG_BOUNDS[0][1]
    && longitude <= ORENBURG_BOUNDS[1][1]
}

type NominatimSearchResult = {
  lat: string
  lon: string
  display_name?: string
}

type NominatimReverseResult = {
  display_name?: string
}
