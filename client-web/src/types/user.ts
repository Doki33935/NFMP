export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  id: number
  username: string
  role: string
  full_name: string
}

export interface UserCreate {
  username: string
  password: string
  password_confirmation: string
  role: string
  full_name: string
}

export interface UserUpdate {
  username?: string
  password?: string
  password_confirmation?: string
  role?: string
  full_name?: string
}

export type User = {
  id: number
  username: string
  role: string
  full_name: string
  is_active?: boolean
}
