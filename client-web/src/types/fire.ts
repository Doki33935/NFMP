export interface FireParticipantEventIn {
  participant_id: number
  arrival_time: string
  tech_type_id?: number | null
  comment?: string
}

export interface FireParticipantEventOut {
  id: number
  fire_id: number
  participant_id: number
  arrival_time: string
  tech_type_id?: number | null
  comment?: string
}

export interface FireCreate {
  fire_date: string
  time_msg: string
  is_forest: boolean
  land_type_id?: number | null
  area?: number | null
  address: string
  municipality_id?: number | null
  selsovet_id?: number | null
  latitude?: number | null
  longitude?: number | null
  forestry_id?: number | null
  reason_id?: number | null
  right_of_way?: boolean
  right_of_way_type?: string
  owner?: string
  source?: string
  extra?: string
  external_card_number?: string
  participants?: FireParticipantEventIn[]
}

export interface FireUpdate {
  fire_date?: string
  time_msg?: string
  is_forest?: boolean
  land_type_id?: number | null
  area?: number | null
  address?: string
  municipality_id?: number | null
  selsovet_id?: number | null
  latitude?: number | null
  longitude?: number | null
  forestry_id?: number | null
  reason_id?: number | null
  right_of_way?: boolean
  right_of_way_type?: string
  owner?: string
  source?: string
  extra?: string
  end_time?: string | null
  external_card_number?: string
  participants?: FireParticipantEventIn[]
}

export interface FireResponse {
  id: number
  fire_date: string
  time_msg: string
  end_time?: string | null
  is_forest: boolean
  land_type_id?: number | null
  area?: number | null
  address: string
  municipality_id?: number | null
  selsovet_id?: number | null
  latitude?: number | null
  longitude?: number | null
  forestry_id?: number | null
  reason_id?: number | null
  right_of_way?: boolean
  right_of_way_type?: string
  owner?: string
  source?: string
  extra?: string
  creator_id: number
  reviewer_id?: number | null
  external_card_number?: string
  status: string
  creator_name?: string
  reviewer_name?: string
  participant_events?: FireParticipantEventOut[]
}
