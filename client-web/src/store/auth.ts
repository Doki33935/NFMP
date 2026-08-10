import { create } from 'zustand'
import type { User } from '@/types/user'

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
  hydrated: boolean
  login: (user: User) => void
  updateUser: (user: User) => void
  setSession: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: getStoredUser(),
  hydrated: false,
  login: (user) => {
    sessionStorage.setItem('user', JSON.stringify(user))
    set({ user, hydrated: true })
  },
  updateUser: (user) => {
    sessionStorage.setItem('user', JSON.stringify(user))
    set({ user })
  },
  setSession: (user) => {
    if (user) sessionStorage.setItem('user', JSON.stringify(user))
    else sessionStorage.removeItem('user')
    set({ user, hydrated: true })
  },
  logout: () => {
    sessionStorage.removeItem('user')
    set({ user: null, hydrated: true })
  },
}))
