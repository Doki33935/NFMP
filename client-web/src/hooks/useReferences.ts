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
    let cancelled = false

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
        if (cancelled) return

        setData({
          municipalities: municipalities.data,
          landTypes: landTypes.data,
          forestries: forestries.data,
          participants: participants.data,
          techTypes: techTypes.data,
          reasonGroups: reasonGroups.data,
        })
      } catch {
        if (!cancelled) {
          setData({
            municipalities: [],
            landTypes: [],
            forestries: [],
            participants: [],
            techTypes: [],
            reasonGroups: [],
          })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()

    return () => {
      cancelled = true
    }
  }, [])

  return { ...data, loading }
}

export function useSelsovets(municipalityId: number | null) {
  const [selsovets, setSelsovets] = useState<Selsovet[]>([])

  useEffect(() => {
    let cancelled = false

    if (!municipalityId) {
      setSelsovets([])
      return () => {
        cancelled = true
      }
    }

    api
      .get<Selsovet[]>('/references/selsovets', {
        params: { municipality_id: municipalityId },
      })
      .then((r) => {
        if (!cancelled) setSelsovets(r.data)
      })
      .catch(() => {
        if (!cancelled) setSelsovets([])
      })

    return () => {
      cancelled = true
    }
  }, [municipalityId])

  return selsovets
}

export function useReasons(groupId: number | null) {
  const [reasons, setReasons] = useState<Reason[]>([])

  useEffect(() => {
    let cancelled = false

    if (!groupId) {
      setReasons([])
      return () => {
        cancelled = true
      }
    }

    api
      .get<Reason[]>('/references/reasons', {
        params: { group_id: groupId },
      })
      .then((r) => {
        if (!cancelled) setReasons(r.data)
      })
      .catch(() => {
        if (!cancelled) setReasons([])
      })

    return () => {
      cancelled = true
    }
  }, [groupId])

  return reasons
}
