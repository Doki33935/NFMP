import { useState, useEffect } from 'react'
import api from '@/lib/api'
import type {
  Municipality,
  Selsovet,
  LandType,
  Forestry,
  FireParticipant,
  TechType,
  ReasonGroup,
  Reason,
} from '@/types/references'

interface References {
  municipalities: Municipality[]
  landTypes: LandType[]
  forestries: Forestry[]
  participants: FireParticipant[]
  techTypes: TechType[]
  reasonGroups: ReasonGroup[]
}

export function useReferences() {
  const [data, setData] = useState<References>({
    municipalities: [],
    landTypes: [],
    forestries: [],
    participants: [],
    techTypes: [],
    reasonGroups: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [municipalities, landTypes, forestries, participants, techTypes, reasonGroups] =
          await Promise.all([
            api.get<Municipality[]>('/references/municipalities'),
            api.get<LandType[]>('/references/land-types'),
            api.get<Forestry[]>('/references/forestry'),
            api.get<FireParticipant[]>('/references/fire-participants'),
            api.get<TechType[]>('/references/tech-types'),
            api.get<ReasonGroup[]>('/references/reason-groups'),
          ])
        setData({
          municipalities: municipalities.data,
          landTypes: landTypes.data,
          forestries: forestries.data,
          participants: participants.data,
          techTypes: techTypes.data,
          reasonGroups: reasonGroups.data,
        })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return { ...data, loading }
}

export function useSelsovets(municipalityId: number | null) {
  const [selsovets, setSelsovets] = useState<Selsovet[]>([])

  useEffect(() => {
    if (!municipalityId) {
      setSelsovets([])
      return
    }
    api
      .get<Selsovet[]>('/references/selsovets', {
        params: { municipality_id: municipalityId },
      })
      .then((r) => setSelsovets(r.data))
  }, [municipalityId])

  return selsovets
}

export function useReasons(groupId: number | null) {
  const [reasons, setReasons] = useState<Reason[]>([])

  useEffect(() => {
    if (!groupId) {
      setReasons([])
      return
    }
    api
      .get<Reason[]>('/references/reasons', {
        params: { group_id: groupId },
      })
      .then((r) => setReasons(r.data))
  }, [groupId])

  return reasons
}
