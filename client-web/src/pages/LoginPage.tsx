import { useState } from 'react'
import { useAuthStore } from '@/store/auth'
import api from '@/lib/api'
import type { LoginResponse } from '@/types/user'

export function LoginPage() {
  const login = useAuthStore((s) => s.login)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post<LoginResponse>('/login', { username, password })
      login(res.data)
    } catch {
      setError('Неверный логин или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-svh items-center justify-center overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.03]">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="fire-pattern" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
              <path d="M60 10c2 6 5 7 7 9a10 10 0 0 1 3 7 10 10 0 0 1-10 10 10 10 0 0 1-10-10c0-3 1-4 2-6 1 3 3 4 4 4a4 4 0 0 0 4-4c0-3-2-4-2-8z" fill="currentColor"/>
              <path d="M30 70c1 4 3 5 4 6a7 7 0 0 1 2 5 7 7 0 0 1-7 7 7 7 0 0 1-7-7c0-2 1-3 1-4 1 2 2 3 3 3a3 3 0 0 0 3-3c0-2-1-3-1-5z" fill="currentColor"/>
              <path d="M90 80c1 4 3 5 4 6a7 7 0 0 1 2 5 7 7 0 0 1-7 7 7 7 0 0 1-7-7c0-2 1-3 1-4 1 2 2 3 3 3a3 3 0 0 0 3-3c0-2-1-3-1-5z" fill="currentColor"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#fire-pattern)"/>
        </svg>
      </div>

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-sm rounded-xl bg-surface/80 backdrop-blur-sm border border-border p-8 space-y-5 shadow-2xl"
      >
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mx-auto">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
              <path d="M12 2c1 3 2.5 3.5 3.5 4.5A5 5 0 0 1 17 10a5 5 0 0 1-5 5 5 5 0 0 1-5-5c0-1.5.5-2 1-3 .5 1.5 1.5 2 2 2a2 2 0 0 0 2-2c0-1.5-1-2-1-4z"/>
              <path d="M12 15v7"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold">NFMP</h1>
          <p className="text-text-muted text-sm">Nature Fires Monitoring Program</p>
        </div>

        <div className="space-y-3">
          <input
            type="text"
            placeholder="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-lg bg-background border border-border px-4 py-2.5 text-text placeholder:text-text-muted focus:outline-none focus:border-primary transition-colors"
            autoFocus
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg bg-background border border-border px-4 py-2.5 text-text placeholder:text-text-muted focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {error && (
          <p className="text-primary text-sm text-center bg-primary/10 rounded-md py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-all active:scale-[0.98] cursor-pointer"
        >
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>
    </div>
  )
}
