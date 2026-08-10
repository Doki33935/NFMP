import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '@/lib/api'
import { useReferences } from '@/hooks/useReferences'
import type { FireResponse } from '@/types/fire'
import type { Reason, Selsovet } from '@/types/references'

const STATUS_LABELS: Record<string, string> = {
  OPEN: 'Открыт',
  IN_REVIEW: 'На проверке',
  COMPLETED: 'Оформлен',
}

export function FireViewPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const refs = useReferences()
  const [fire, setFire] = useState<FireResponse | null>(null)
  const [reasons, setReasons] = useState<Reason[]>([])
  const [selsovets, setSelsovets] = useState<Selsovet[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      try {
        const [fireRes, reasonsRes, selsovetsRes] = await Promise.all([
          api.get<FireResponse>(`/fires/${id}/view`),
          api.get<Reason[]>('/references/reasons').catch(() => ({ data: [] as Reason[] })),
          api.get<Selsovet[]>('/references/selsovets').catch(() => ({ data: [] as Selsovet[] })),
        ])

        if (!cancelled) {
          setFire(fireRes.data)
          setReasons(reasonsRes.data)
          setSelsovets(selsovetsRes.data)
        }
      } catch {
        if (!cancelled) setFire(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [id])

  const dictionaries = useMemo(() => {
    const mapById = <T extends { id: number; name: string }>(items: T[]) =>
      new Map(items.map((item) => [item.id, item.name]))

    return {
      municipalities: mapById(refs.municipalities),
      selsovets: mapById(selsovets),
      landTypes: mapById(refs.landTypes),
      forestries: mapById(refs.forestries),
      participants: mapById(refs.participants),
      techTypes: mapById(refs.techTypes),
      reasons: mapById(reasons),
    }
  }, [refs, reasons, selsovets])

  if (loading || refs.loading) {
    return (
      <div className="p-6">
        <div className="max-w-5xl mx-auto space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-surface rounded-xl border border-border p-6 animate-pulse-soft">
              <div className="w-40 h-5 bg-border rounded mb-5" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
                <div className="h-14 border-b border-border" />
                <div className="h-14 border-b border-border" />
                <div className="h-14 border-b border-border" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!fire) {
    return (
      <div className="p-6">
        <div className="max-w-5xl mx-auto text-primary">Пожар не найден или нет доступа к просмотру</div>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-5xl mx-auto space-y-5">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold">Пожар #{fire.id}</h1>
            <p className="text-sm text-text-muted mt-1">Просмотр карточки из мониторинга</p>
          </div>
          <button
            onClick={() => navigate('/monitoring')}
            className="px-4 py-2 rounded-lg bg-surface text-text-muted font-medium hover:bg-surface-hover hover:text-text transition-colors cursor-pointer"
          >
            Назад к мониторингу
          </button>
        </div>

        <Section title="Событие">
          <Info label="Дата пожара" value={formatDate(fire.fire_date)} />
          <Info label="Время сообщения" value={formatDateTime(fire.time_msg)} />
          <Info label="Статус" value={STATUS_LABELS[fire.status] || fire.status} />
          <Info label="Тип пожара" value={fire.is_forest ? 'Лесной' : 'Ландшафтный'} />
          <Info label="Дата ликвидации" value={fire.end_time ? formatDateTime(fire.end_time) : '—'} />
          <Info label="Время обслуживания" value={formatDuration(serviceDurationMinutes(fire))} />
        </Section>

        <Section title="Местоположение">
          <Info label="Адрес" value={fire.address} wide />
          <Info label="Карта" value={mapLink(fire)} />
          <Info label="Муниципальное образование" value={dictionaries.municipalities.get(fire.municipality_id || 0) || '—'} />
          <Info label="Сельсовет" value={dictionaries.selsovets.get(fire.selsovet_id || 0) || '—'} />
          <Info label="Состав земли" value={dictionaries.landTypes.get(fire.land_type_id || 0) || '—'} />
        </Section>

        <Section title="Обстоятельства">
          <Info label="Лесничество" value={dictionaries.forestries.get(fire.forestry_id || 0) || '—'} />
          <Info label="Причина" value={dictionaries.reasons.get(fire.reason_id || 0) || '—'} wide />
          <Info label="Площадь" value={fire.area != null ? `${fire.area} га` : '—'} />
          <Info label="Наличие ЗОУИТ" value={fire.right_of_way ? 'Да' : 'Нет'} />
          <Info label="Тип ЗОУИТ" value={fire.right_of_way_type || '—'} />
          <Info label="Собственник" value={fire.owner || '—'} />
          <Info label="Детальная информация о собственнике" value={fire.source || '—'} />
          <Info label="Номер карточки ААС КНД" value={fire.external_card_number || '—'} />
          <Info label="Примечание" value={fire.extra || '—'} wide />
        </Section>

        <Section title="Участники тушения">
          {fire.participant_events?.length ? (
            <div className="md:col-span-2 overflow-x-auto border-y border-border">
              <table className="w-full min-w-[620px] text-sm">
                <thead className="text-text-muted">
                  <tr>
                    <th className="text-left font-medium py-2">Участник</th>
                    <th className="text-left font-medium py-2">Время прибытия</th>
                    <th className="text-left font-medium py-2">Техника</th>
                    <th className="text-left font-medium py-2">Комментарий</th>
                  </tr>
                </thead>
                <tbody>
                  {fire.participant_events.map((event) => (
                    <tr key={event.id} className="border-t border-border">
                      <td className="py-2 pr-3">{dictionaries.participants.get(event.participant_id) || '—'}</td>
                      <td className="py-2 pr-3">{event.arrival_time || '—'}</td>
                      <td className="py-2 pr-3">{event.tech_type_id ? dictionaries.techTypes.get(event.tech_type_id) || '—' : '—'}</td>
                      <td className="py-2 pr-3">{event.comment || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Info label="Участники" value="—" wide />
          )}
        </Section>

        <Section title="Служебная информация">
          <Info label="Создал" value={fire.creator_name || '—'} />
          <Info label="Проверил" value={fire.reviewer_name || '—'} />
        </Section>
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="bg-surface rounded-xl border border-border p-5">
      <h2 className="font-semibold text-base pb-3 border-b border-border">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
        {children}
      </div>
    </section>
  )
}

function Info({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  const isLink = value.startsWith('http')

  return (
    <div className={`py-3 border-b border-border/70 ${wide ? 'md:col-span-2' : ''}`}>
      <p className="text-xs text-text-muted uppercase tracking-wide">{label}</p>
      {isLink ? (
        <a href={value} target="_blank" rel="noreferrer" className="mt-1 inline-flex text-sm font-medium text-accent hover:text-primary-hover">
          Открыть на карте
        </a>
      ) : (
        <p className="mt-1 text-sm font-medium text-text whitespace-pre-wrap break-words leading-relaxed">{value || '—'}</p>
      )}
    </div>
  )
}

function serviceDurationMinutes(fire: FireResponse): number | null {
  if (!fire.time_msg || !fire.end_time) return null

  const start = new Date(fire.time_msg).getTime()
  const end = new Date(fire.end_time).getTime()
  if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) return null

  return Math.round((end - start) / 60000)
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
  return dateStr
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value || '—'
  return date.toLocaleString('ru-RU')
}

function formatDuration(minutes: number | null): string {
  if (minutes === null) return '—'
  if (minutes < 60) return `${minutes} мин`

  const days = Math.floor(minutes / 1440)
  const hours = Math.floor((minutes % 1440) / 60)
  const restMinutes = minutes % 60
  const parts: string[] = []

  if (days > 0) parts.push(`${days} д`)
  if (hours > 0) parts.push(`${hours} ч`)
  if (restMinutes > 0 || parts.length === 0) parts.push(`${restMinutes} мин`)

  return parts.join(' ')
}

function mapLink(fire: FireResponse): string {
  if (fire.latitude == null || fire.longitude == null) return '—'
  return `https://www.openstreetmap.org/?mlat=${fire.latitude}&mlon=${fire.longitude}#map=15/${fire.latitude}/${fire.longitude}`
}
