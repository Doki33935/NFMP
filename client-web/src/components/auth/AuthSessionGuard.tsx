import { useEffect } from 'react'
import api from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import type { User } from '@/types/user'

export function AuthSessionGuard() {
  const setSession = useAuthStore((state) => state.setSession)

  useEffect(() => {
    let cancelled = false

    const checkSession = async () => {
      try {
        const response = await api.get<User>('/session')
        if (!cancelled) setSession(response.data)
      } catch {
        if (!cancelled) setSession(null)
      }
    }

    void checkSession()
    const interval = window.setInterval(() => void checkSession(), 5 * 60_000)
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') void checkSession()
    }
    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      cancelled = true
      window.clearInterval(interval)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [setSession])

  return null
}
