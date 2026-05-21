import { useState, useEffect, useCallback } from 'react'
import api from '@/lib/api'
import type { FireResponse, FireCreate, FireUpdate } from '@/types/fire'

export function useFireList(status?: string) {
  const [fires, setFires] = useState<FireResponse[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = status ? { status } : {}
      const res = await api.get<FireResponse[]>('/fires/', { params })
      setFires(res.data)
    } finally {
      setLoading(false)
    }
  }, [status])

  useEffect(() => {
    load()
  }, [load])

  return { fires, loading, reload: load }
}

export function useFire(id: number | string) {
  const [fire, setFire] = useState<FireResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get<FireResponse>(`/fires/${id}`)
        let fireData = res.data

        // Если пожар OPEN — инспектор берёт его в работу
        if (fireData.status === 'OPEN') {
          try {
            const takeRes = await api.post<FireResponse>(`/fires/${id}/take`)
            fireData = takeRes.data
          } catch {
            // Если не удалось взять — просто показываем как есть
          }
        }

        setFire(fireData)
      } finally {
        setLoading(false)
      }
    }
    load()
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
