import { useState, useEffect, useCallback } from 'react'
import api from '@/lib/api'
import type { FireResponse, FireCreate, FireUpdate } from '@/types/fire'

const takingRequests = new Map<string, Promise<FireResponse | null>>()

export function useFireList(status?: string) {
  const [fires, setFires] = useState<FireResponse[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = status ? { status } : {}
      const res = await api.get<FireResponse[]>('/fires/', { params })
      setFires(res.data)
    } catch {
      setFires([])
    } finally {
      setLoading(false)
    }
  }, [status])

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timer)
  }, [load])

  return { fires, loading, reload: load }
}

export function useFire(id: number | string) {
  const [fire, setFire] = useState<FireResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      try {
        const res = await api.get<FireResponse>(`/fires/${id}`)
        let fireData = res.data

        if (fireData.status === 'OPEN') {
          const takeKey = `taking-fire-${id}`
          let takeRequest = takingRequests.get(takeKey)

          if (!takeRequest) {
            takeRequest = api
              .post<FireResponse>(`/fires/${id}/take`)
              .then((r) => r.data)
              .catch(async () => {
                const fresh = await api.get<FireResponse>(`/fires/${id}`).catch(() => null)
                return fresh?.data ?? null
              })
              .finally(() => {
                takingRequests.delete(takeKey)
              })
            takingRequests.set(takeKey, takeRequest)
          }

          fireData = (await takeRequest) ?? fireData
        }

        if (!cancelled) setFire(fireData)
      } catch {
        if (!cancelled) setFire(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    const timer = window.setTimeout(() => void load(), 0)

    return () => {
      window.clearTimeout(timer)
      cancelled = true
    }
  }, [id])

  return { fire, loading }
}

export async function createFire(data: FireCreate): Promise<FireResponse> {
  const res = await api.post<FireResponse>('/fires/', data)
  return res.data
}

export async function updateFire(id: number, data: FireUpdate): Promise<FireResponse> {
  const res = await api.put<FireResponse>(`/fires/${id}`, data)
  return res.data
}

export async function takeFire(id: number): Promise<FireResponse> {
  const res = await api.post<FireResponse>(`/fires/${id}/take`)
  return res.data
}
