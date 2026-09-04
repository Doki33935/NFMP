import L from 'leaflet'
import type { GeoJsonObject } from 'geojson'

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

let districtsPromise: Promise<GeoJsonObject> | null = null
let geocodingQueue: Promise<void> = Promise.resolve()
let lastGeocodingRequestAt = 0

export function createOpenStreetMap(container: HTMLElement): L.Map {
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

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map)
  L.control.scale({ imperial: false, metric: true }).addTo(map)

  return map
}

export async function addOrenburgDistricts(
  map: L.Map,
  isCancelled: () => boolean = () => false
): Promise<L.GeoJSON | null> {
  const collection = await loadDistricts()
  if (isCancelled()) return null
  return L.geoJSON(collection, {
    style: {
      color: '#f87171',
      weight: 1,
      opacity: 0.72,
      fillColor: '#dc2626',
      fillOpacity: 0.06,
    },
    onEachFeature: (feature, layer) => {
      const name = feature.properties?.name
      if (typeof name === 'string' && name) layer.bindTooltip(name, { sticky: true })
    },
  }).addTo(map)
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
