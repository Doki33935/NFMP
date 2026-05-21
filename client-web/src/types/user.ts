export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  id: number
  username: string
  role: string
  full_name: string
  access_token: string
}

export interface UserCreate {
  username: string
  password: string
  role: string
  full_name: string
}

export type User = {
  id: number
  username: string
  role: string
  full_name: string
}
