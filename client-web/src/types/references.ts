export interface Municipality {
  id: number
  name: string
}

export interface Selsovet {
  id: number
  name: string
  municipality_id: number
}

export interface LandType {
  id: number
  name: string
}

export interface Forestry {
  id: number
  name: string
}

export interface ZouitType {
  id: string
  name: string
}

export interface OwnerType {
  id: string
  name: string
}

export interface FireParticipant {
  id: number
  name: string
}

export interface TechType {
  id: number
  name: string
}

export interface ReasonGroup {
  id: number
  name: string
}

export interface Reason {
  id: number
  name: string
  group_id: number
}
