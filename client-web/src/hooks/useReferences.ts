import { useState, useEffect } from 'react'
import api from '@/lib/api'
import type {
  Municipality,
  Selsovet,
  LandType,
  Forestry,
  ZouitType,
  OwnerType,
  FireParticipant,
  TechType,
  ReasonGroup,
  Reason,
} from '@/types/references'

interface References {
  municipalities: Municipality[]
  landTypes: LandType[]
  forestries: Forestry[]
  zouitTypes: ZouitType[]
  ownerTypes: OwnerType[]
  participants: FireParticipant[]
  techTypes: TechType[]
  reasonGroups: ReasonGroup[]
}

export function useReferences() {
  const [data, setData] = useState<References>({
    municipalities: [],
    landTypes: [],
    forestries: [],
    zouitTypes: [],
    ownerTypes: [],
    participants: [],
    techTypes: [],
    reasonGroups: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [municipalities, landTypes, forestries, zouitTypes, ownerTypes, participants, techTypes, reasonGroups] =
          await Promise.all([
            api.get<Municipality[]>('/references/municipalities'),
            api.get<LandType[]>('/references/land-types'),
            api.get<Forestry[]>('/references/forestry'),
            api.get<ZouitType[]>('/references/zouit-types'),
            api.get<OwnerType[]>('/references/owners'),
            api.get<FireParticipant[]>('/references/fire-participants'),
            api.get<TechType[]>('/references/tech-types'),
            api.get<ReasonGroup[]>('/references/reason-groups'),
          ])
        if (cancelled) return

        setData({
          municipalities: municipalities.data,
          landTypes: landTypes.data,
          forestries: forestries.data,
          zouitTypes: zouitTypes.data,
          ownerTypes: ownerTypes.data,
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
            zouitTypes: [],
            ownerTypes: [],
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
  const [result, setResult] = useState<{ key: number; items: Selsovet[] } | null>(null)

  useEffect(() => {
    let cancelled = false

    if (!municipalityId) {
      return () => {
        cancelled = true
      }
    }

    api
      .get<Selsovet[]>('/references/selsovets', {
        params: { municipality_id: municipalityId },
      })
      .then((r) => {
        if (!cancelled) setResult({ key: municipalityId, items: r.data })
      })
      .catch(() => {
        if (!cancelled) setResult({ key: municipalityId, items: [] })
      })

    return () => {
      cancelled = true
    }
  }, [municipalityId])

  return result?.key === municipalityId ? result.items : []
}

export function useReasons(groupId: number | null) {
  const [result, setResult] = useState<{ key: number; items: Reason[] } | null>(null)

  useEffect(() => {
    let cancelled = false

    if (!groupId) {
      return () => {
        cancelled = true
      }
    }

    api
      .get<Reason[]>('/references/reasons', {
        params: { group_id: groupId },
      })
      .then((r) => {
        if (!cancelled) setResult({ key: groupId, items: r.data })
      })
      .catch(() => {
        if (!cancelled) setResult({ key: groupId, items: [] })
      })

    return () => {
      cancelled = true
    }
  }, [groupId])

  return result?.key === groupId ? result.items : []
}
