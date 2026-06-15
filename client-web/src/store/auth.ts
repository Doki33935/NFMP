import { create } from 'zustand'
import type { User } from '@/types/user'

function setCookie(name: string, value: string, days: number) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
}

function parseUserFromToken(token: string | null): User | null {
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { id: Number(payload.sub), username: '', role: payload.role, full_name: '' }
  } catch {
    return null
  }
}

function getStoredUser(): User | null {
  const stored = sessionStorage.getItem('user')
  if (!stored) return null

  try {
    return JSON.parse(stored)
  } catch {
    sessionStorage.removeItem('user')
    return null
  }
}

interface AuthState {
  user: User | null
  token: string | null
  login: (user: User, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => {
  const token = getCookie('token')
  const user = getStoredUser() ?? parseUserFromToken(token)

  return {
    user,
    token,
    login: (user, token) => {
      setCookie('token', token, 7)
      sessionStorage.setItem('user', JSON.stringify(user))
      set({ user, token })
    },
    logout: () => {
      deleteCookie('token')
      sessionStorage.removeItem('user')
      set({ user: null, token: null })
    },
  }
})
