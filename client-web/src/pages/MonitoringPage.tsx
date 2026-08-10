import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  addDays,
  addMonths,
  endOfMonth,
  endOfWeek,
  format,
  isAfter,
  isBefore,
  isSameDay,
  isSameMonth,
  isValid,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns'
import { ru } from 'date-fns/locale'
import api from '@/lib/api'
import { useFireList } from '@/hooks/useFires'
import { useReferences } from '@/hooks/useReferences'
import { SearchableMultiSelect } from '@/components/shared/SearchableMultiSelect'
import { MonitoringMap } from '@/components/map/MonitoringMap'
import type { FireResponse } from '@/types/fire'
import type { Reason, Selsovet } from '@/types/references'

type Filters = {
  dateFrom: string
  dateTo: string
  statuses: string[]
  fireTypes: string[]
  municipalityIds: string[]
  selsovetIds: string[]
  landTypeIds: string[]
  forestryIds: string[]
  reasonGroupIds: string[]
  reasonIds: string[]
  participantIds: string[]
  techTypeIds: string[]
  rightOfWayValues: string[]
  zouitTypes: string[]
  ownerTypes: string[]
  completenessValues: string[]
  areaRanges: string[]
  query: string
}

type MultiFilterKey = Exclude<keyof Filters, 'dateFrom' | 'dateTo' | 'query'>

const EMPTY_FILTERS: Filters = {
  dateFrom: '',
  dateTo: '',
  statuses: [],
  fireTypes: [],
  municipalityIds: [],
  selsovetIds: [],
  landTypeIds: [],
  forestryIds: [],
  reasonGroupIds: [],
  reasonIds: [],
  participantIds: [],
  techTypeIds: [],
  rightOfWayValues: [],
  zouitTypes: [],
  ownerTypes: [],
  completenessValues: [],
  areaRanges: [],
  query: '',
}

const AREA_RANGES = [
  { id: '0-10', name: '0-10 га', from: 0, to: 10 },
  { id: '10-20', name: '10-20 га', from: 10, to: 20 },
  { id: '20-50', name: '20-50 га', from: 20, to: 50 },
  { id: '50-100', name: '50-100 га', from: 50, to: 100 },
  { id: '100-200', name: '100-200 га', from: 100, to: 200 },
  { id: '200-500', name: '200-500 га', from: 200, to: 500 },
  { id: '500+', name: '500+ га', from: 500, to: null },
]

const STATUS_LABELS: Record<string, string> = {
  OPEN: 'Открыт',
  IN_REVIEW: 'На проверке',
  COMPLETED: 'Оформлен',
}

const COMPLETENESS_OPTIONS = [
  { id: 'missing_required', name: 'Есть незаполненные важные поля' },
  { id: 'missing_reason', name: 'Не указана причина' },
  { id: 'missing_area', name: 'Не указана площадь' },
  { id: 'missing_owner', name: 'Не указан собственник' },
  { id: 'missing_card', name: 'Нет номера карточки ААС КНД' },
  { id: 'missing_end_time', name: 'Нет даты ликвидации' },
  { id: 'has_participants', name: 'Есть участники тушения' },
  { id: 'no_participants', name: 'Нет участников тушения' },
]

export function MonitoringPage() {
  const navigate = useNavigate()
  const { fires, loading } = useFireList()
  const refs = useReferences()
  const [reasons, setReasons] = useState<Reason[]>([])
  const [selsovets, setSelsovets] = useState<Selsovet[]>([])
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS)

  useEffect(() => {
    api.get<Reason[]>('/references/reasons').then((r) => setReasons(r.data)).catch(() => setReasons([]))
    api.get<Selsovet[]>('/references/selsovets').then((r) => setSelsovets(r.data)).catch(() => setSelsovets([]))
  }, [])

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
      reasonGroups: mapById(refs.reasonGroups),
      reasons: mapById(reasons),
    }
  }, [refs, reasons, selsovets])

  const reasonGroupByReason = useMemo(() => {
    const map = new Map<number, number>()
    reasons.forEach((reason) => map.set(reason.id, reason.group_id))
    return map
  }, [reasons])

  const visibleSelsovets = useMemo(() => {
    if (filters.municipalityIds.length === 0) return selsovets
    const selected = new Set(filters.municipalityIds.map(Number))
    return selsovets.filter((item) => selected.has(item.municipality_id))
  }, [filters.municipalityIds, selsovets])

  const visibleReasons = useMemo(() => {
    if (filters.reasonGroupIds.length === 0) return reasons
    const selected = new Set(filters.reasonGroupIds.map(Number))
    return reasons.filter((item) => selected.has(item.group_id))
  }, [filters.reasonGroupIds, reasons])

  const ownerFilterOptions = useMemo(
    () => mergeTextOptions(refs.ownerTypes, fires.map((fire) => fire.owner)),
    [fires, refs.ownerTypes]
  )
  const zouitFilterOptions = useMemo(
    () => mergeTextOptions(refs.zouitTypes, fires.map((fire) => fire.right_of_way_type)),
    [fires, refs.zouitTypes]
  )

  const filteredFires = useMemo(() => {
    return fires.filter((fire) => {
      if (filters.dateFrom && fire.fire_date < filters.dateFrom) return false
      if (filters.dateTo && fire.fire_date > filters.dateTo) return false
      if (!matchesTextSelection(filters.statuses, fire.status)) return false
      if (!matchesTextSelection(filters.fireTypes, fire.is_forest ? 'forest' : 'landscape')) return false
      if (!matchesNumberSelection(filters.municipalityIds, fire.municipality_id)) return false
      if (!matchesNumberSelection(filters.selsovetIds, fire.selsovet_id)) return false
      if (!matchesNumberSelection(filters.landTypeIds, fire.land_type_id)) return false
      if (!matchesNumberSelection(filters.forestryIds, fire.forestry_id)) return false
      if (!matchesNumberSelection(filters.reasonIds, fire.reason_id)) return false
      if (!matchesNumberSelection(filters.reasonGroupIds, reasonGroupByReason.get(fire.reason_id || 0))) return false
      if (filters.participantIds.length > 0 && !fire.participant_events?.some((p) => filters.participantIds.includes(String(p.participant_id)))) return false
      if (filters.techTypeIds.length > 0 && !fire.participant_events?.some((p) => p.tech_type_id != null && filters.techTypeIds.includes(String(p.tech_type_id)))) return false
      if (!matchesTextSelection(filters.rightOfWayValues, fire.right_of_way ? 'yes' : 'no')) return false
      if (!matchesTextSelection(filters.zouitTypes, fire.right_of_way_type || '')) return false
      if (!matchesTextSelection(filters.ownerTypes, fire.owner || '')) return false
      if (filters.areaRanges.length > 0 && !filters.areaRanges.some((rangeId) => matchesAreaRange(fire, rangeId))) return false
      if (filters.completenessValues.length > 0 && !filters.completenessValues.some((mode) => matchesCompleteness(fire, mode))) return false

      if (filters.query.trim()) {
        const q = filters.query.trim().toLowerCase()
        const text = [
          fire.id,
          fire.address,
          fire.owner,
          fire.source,
          fire.extra,
          fire.external_card_number,
          fire.creator_name,
          fire.reviewer_name,
          dictionaries.municipalities.get(fire.municipality_id || 0),
          dictionaries.selsovets.get(fire.selsovet_id || 0),
          dictionaries.forestries.get(fire.forestry_id || 0),
          dictionaries.reasons.get(fire.reason_id || 0),
        ].filter(Boolean).join(' ').toLowerCase()
        if (!text.includes(q)) return false
      }

      return true
    })
  }, [dictionaries, filters, fires, reasonGroupByReason])

  const stats = useMemo(() => buildStats(filteredFires), [filteredFires])
  const reasonBreakdown = useMemo(
    () => breakdownBy(filteredFires, (f) => dictionaries.reasons.get(f.reason_id || 0) || 'Не указано'),
    [dictionaries.reasons, filteredFires]
  )
  const topMunicipalities = useMemo(
    () => topBy(filteredFires, (f) => dictionaries.municipalities.get(f.municipality_id || 0) || 'Не указано'),
    [dictionaries.municipalities, filteredFires]
  )
  const participantBreakdown = useMemo(
    () => topParticipants(filteredFires, dictionaries.participants),
    [dictionaries.participants, filteredFires]
  )
  const ownerBreakdown = useMemo(
    () => topBy(filteredFires, (f) => f.owner || 'Не указано'),
    [filteredFires]
  )

  const setFilter = (key: 'dateFrom' | 'dateTo' | 'query', value: string) => {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  const setMultiFilter = (key: MultiFilterKey, values: string[]) => {
    setFilters((current) => {
      const next = { ...current, [key]: values }

      if (key === 'municipalityIds' && values.length > 0) {
        const municipalities = new Set(values.map(Number))
        const allowedSelsovets = new Set(
          selsovets.filter((item) => municipalities.has(item.municipality_id)).map((item) => String(item.id))
        )
        next.selsovetIds = current.selsovetIds.filter((id) => allowedSelsovets.has(id))
      }

      if (key === 'reasonGroupIds' && values.length > 0) {
        const groups = new Set(values.map(Number))
        const allowedReasons = new Set(
          reasons.filter((item) => groups.has(item.group_id)).map((item) => String(item.id))
        )
        next.reasonIds = current.reasonIds.filter((id) => allowedReasons.has(id))
      }

      return next
    })
  }

  const resetFilters = () => setFilters(EMPTY_FILTERS)
  const isLoading = loading || refs.loading

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-7xl mx-auto space-y-5">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-xl font-bold">Мониторинг</h1>
            <p className="text-sm text-text-muted mt-1">Сводка, фильтры и выгрузка по выбранному набору пожаров</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => exportCsv(filteredFires, dictionaries)} className="px-3 py-2 rounded-md bg-primary text-sm text-white hover:bg-primary-hover transition-colors cursor-pointer">
              Выгрузить CSV
            </button>
          </div>
        </div>

        {isLoading ? (
          <LoadingState />
        ) : (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
              <StatCard label="Всего" value={stats.total} />
              <StatCard label="Открытые" value={stats.open} tone="accent" />
              <StatCard label="На проверке" value={stats.review} tone="warning" />
              <StatCard label="Оформленные" value={stats.completed} tone="success" />
              <StatCard label="С ЗОУИТ" value={stats.zouit} tone="accent" />
              <StatCard label="Площадь" value={formatNumber(stats.totalArea)} suffix=" га" />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
              <SummaryPanel title="Статусы">
                <BarItem label="Открытые" value={stats.open} total={stats.total} color="bg-primary" />
                <BarItem label="На проверке" value={stats.review} total={stats.total} color="bg-warning" />
                <BarItem label="Оформленные" value={stats.completed} total={stats.total} color="bg-success" />
              </SummaryPanel>

              <SummaryPanel title="Типы пожаров">
                <BarItem label="Лесные" value={stats.forest} total={stats.total} color="bg-success" />
                <BarItem label="Ландшафтные" value={stats.landscape} total={stats.total} color="bg-warning" />
              </SummaryPanel>

              <SummaryPanel title="Собственники">
                {ownerBreakdown.length === 0 ? (
                  <p className="text-sm text-text-muted">Нет данных</p>
                ) : (
                  ownerBreakdown.map((item) => (
                    <BarItem key={item.label} label={item.label} value={item.value} total={stats.total} color="bg-primary" />
                  ))
                )}
              </SummaryPanel>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
              <TopList title="Зарегистрированные причины пожаров" items={reasonBreakdown} full />
              <TopList title="МО по количеству" items={topMunicipalities} />
              <TopList title="Участники тушения" items={participantBreakdown} />
            </div>

            <FilterPanel
              filters={filters}
              setFilter={setFilter}
              setMultiFilter={setMultiFilter}
              resetFilters={resetFilters}
              municipalities={refs.municipalities}
              selsovets={visibleSelsovets}
              landTypes={refs.landTypes}
              forestries={refs.forestries}
              reasonGroups={refs.reasonGroups}
              reasons={visibleReasons}
              participants={refs.participants}
              techTypes={refs.techTypes}
              zouitTypes={zouitFilterOptions}
              ownerTypes={ownerFilterOptions}
            />

            <MonitoringMap
              fires={filteredFires}
              onOpen={(id) => navigate(`/monitoring/fires/${id}`)}
            />

            <div className="bg-surface rounded-lg border border-border overflow-hidden">
              <div className="px-4 py-3 border-b border-border flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <h2 className="font-semibold">Результаты фильтрации</h2>
                  <p className="text-xs text-text-muted mt-0.5">Показано {filteredFires.length} из {fires.length}</p>
                </div>
                <button onClick={resetFilters} className="px-3 py-1.5 rounded-md bg-background text-xs text-text-muted hover:text-text hover:bg-surface-hover transition-colors cursor-pointer">
                  Сбросить фильтры
                </button>
              </div>
              <FireTable fires={filteredFires} dictionaries={dictionaries} onOpen={(id) => navigate(`/monitoring/fires/${id}`)} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function matchesCompleteness(fire: FireResponse, mode: string): boolean {
  const missingRequired =
    !fire.land_type_id ||
    !hasArea(fire) ||
    !fire.reason_id ||
    !fire.owner ||
    !fire.external_card_number ||
    !fire.end_time ||
    (fire.is_forest && !fire.forestry_id)

  const participantCount = fire.participant_events?.length || 0

  const checks: Record<string, boolean> = {
    missing_required: missingRequired,
    missing_reason: !fire.reason_id,
    missing_area: !hasArea(fire),
    missing_owner: !fire.owner,
    missing_card: !fire.external_card_number,
    missing_end_time: !fire.end_time,
    has_participants: participantCount > 0,
    no_participants: participantCount === 0,
  }

  return checks[mode] ?? true
}

function matchesTextSelection(selected: string[], value: string): boolean {
  return selected.length === 0 || selected.includes(value)
}

function matchesNumberSelection(selected: string[], value: number | null | undefined): boolean {
  return selected.length === 0 || (value != null && selected.includes(String(value)))
}

function matchesAreaRange(fire: FireResponse, rangeId: string): boolean {
  const range = AREA_RANGES.find((item) => item.id === rangeId)
  if (!range || !hasArea(fire)) return false

  const area = fire.area ?? 0
  return area >= range.from && (range.to === null || area < range.to)
}

function mergeTextOptions(
  referenceOptions: { id: number | string; name: string }[],
  values: Array<string | null | undefined>
) {
  const result = referenceOptions.map((option) => ({ id: String(option.id), name: option.name }))
  const known = new Set(result.map((option) => option.id))

  values.forEach((value) => {
    const normalized = value?.trim()
    if (normalized && !known.has(normalized)) {
      known.add(normalized)
      result.push({ id: normalized, name: `${normalized} (старое значение)` })
    }
  })

  return result
}

function buildStats(fires: FireResponse[]) {
  const total = fires.length
  const completedFields = fires.reduce((sum, fire) => sum + (matchesCompleteness(fire, 'missing_required') ? 0 : 1), 0)
  const totalArea = fires.reduce((sum, fire) => sum + (fire.area || 0), 0)

  return {
    total,
    open: fires.filter((f) => f.status === 'OPEN').length,
    review: fires.filter((f) => f.status === 'IN_REVIEW').length,
    completed: fires.filter((f) => f.status === 'COMPLETED').length,
    zouit: fires.filter((f) => f.right_of_way).length,
    forest: fires.filter((f) => f.is_forest).length,
    landscape: fires.filter((f) => !f.is_forest).length,
    totalArea,
    completenessPct: total > 0 ? Math.round((completedFields / total) * 100) : 0,
  }
}

function serviceDurationMinutes(fire: FireResponse): number | null {
  if (!fire.time_msg || !fire.end_time) return null

  const start = new Date(fire.time_msg).getTime()
  const end = new Date(fire.end_time).getTime()
  if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) return null

  return Math.round((end - start) / 60000)
}

function hasArea(fire: FireResponse): boolean {
  return fire.area !== null && fire.area !== undefined
}

function topBy(fires: FireResponse[], getter: (fire: FireResponse) => string) {
  return breakdownBy(fires, getter).slice(0, 6)
}

function breakdownBy(fires: FireResponse[], getter: (fire: FireResponse) => string) {
  const counts = new Map<string, number>()
  fires.forEach((fire) => {
    const key = getter(fire)
    counts.set(key, (counts.get(key) || 0) + 1)
  })
  return [...counts.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
}

function topParticipants(fires: FireResponse[], names: Map<number, string>) {
  const counts = new Map<string, number>()
  fires.forEach((fire) => {
    fire.participant_events?.forEach((event) => {
      const label = names.get(event.participant_id) || 'Не указано'
      counts.set(label, (counts.get(label) || 0) + 1)
    })
  })
  return [...counts.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6)
}

function FilterPanel({
  filters,
  setFilter,
  setMultiFilter,
  resetFilters,
  municipalities,
  selsovets,
  landTypes,
  forestries,
  reasonGroups,
  reasons,
  participants,
  techTypes,
  zouitTypes,
  ownerTypes,
}: {
  filters: Filters
  setFilter: (key: 'dateFrom' | 'dateTo' | 'query', value: string) => void
  setMultiFilter: (key: MultiFilterKey, values: string[]) => void
  resetFilters: () => void
  municipalities: { id: number; name: string }[]
  selsovets: { id: number; name: string }[]
  landTypes: { id: number; name: string }[]
  forestries: { id: number; name: string }[]
  reasonGroups: { id: number; name: string }[]
  reasons: { id: number; name: string }[]
  participants: { id: number; name: string }[]
  techTypes: { id: number; name: string }[]
  zouitTypes: { id: number | string; name: string }[]
  ownerTypes: { id: number | string; name: string }[]
}) {
  const activeCount =
    (filters.query.trim() ? 1 : 0) +
    (filters.dateFrom || filters.dateTo ? 1 : 0) +
    Object.entries(filters).filter(([, value]) => Array.isArray(value) && value.length > 0).length

  return (
    <div className="bg-surface rounded-lg border border-border p-4 space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold">Фильтры</h2>
          {activeCount > 0 && <span className="rounded bg-primary/15 px-2 py-0.5 text-xs font-medium text-accent">{activeCount}</span>}
        </div>
        <button onClick={resetFilters} className="text-xs text-text-muted hover:text-primary transition-colors cursor-pointer">
          Сбросить
        </button>
      </div>

      <Input label="Поиск" value={filters.query} onChange={(v) => setFilter('query', v)} placeholder="Адрес, номер, владелец, создал..." />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        <div className="sm:col-span-2">
          <DateRangePicker
            dateFrom={filters.dateFrom}
            dateTo={filters.dateTo}
            onChange={(dateFrom, dateTo) => {
              setFilter('dateFrom', dateFrom)
              setFilter('dateTo', dateTo)
            }}
          />
        </div>
        <MultiSelect label="Тип пожара" values={filters.fireTypes} onChange={(v) => setMultiFilter('fireTypes', v)} options={[
          { id: 'forest', name: 'Лесной' },
          { id: 'landscape', name: 'Ландшафтный' },
        ]} />
        <MultiSelect label="МО" values={filters.municipalityIds} onChange={(v) => setMultiFilter('municipalityIds', v)} options={municipalities} />
        <MultiSelect label="Причина" values={filters.reasonGroupIds} onChange={(v) => setMultiFilter('reasonGroupIds', v)} options={reasonGroups} />
        <MultiSelect label="Площадь" values={filters.areaRanges} onChange={(v) => setMultiFilter('areaRanges', v)} options={AREA_RANGES} />
      </div>

      <details className="rounded-md bg-background/60 border border-border">
        <summary className="px-3 py-2 text-sm text-text-muted hover:text-text cursor-pointer select-none">
          Дополнительные фильтры
        </summary>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3 p-3 border-t border-border">
          <MultiSelect label="Статус" values={filters.statuses} onChange={(v) => setMultiFilter('statuses', v)} options={[
            { id: 'OPEN', name: 'Открыт' },
            { id: 'IN_REVIEW', name: 'На проверке' },
            { id: 'COMPLETED', name: 'Оформлен' },
          ]} />
          <MultiSelect label="Сельсовет" values={filters.selsovetIds} onChange={(v) => setMultiFilter('selsovetIds', v)} options={selsovets} />
          <MultiSelect label="Состав земли" values={filters.landTypeIds} onChange={(v) => setMultiFilter('landTypeIds', v)} options={landTypes} />
          <MultiSelect label="Лесничество" values={filters.forestryIds} onChange={(v) => setMultiFilter('forestryIds', v)} options={forestries} />
          <MultiSelect label="Подпричина" values={filters.reasonIds} onChange={(v) => setMultiFilter('reasonIds', v)} options={reasons} />
          <MultiSelect label="Участник" values={filters.participantIds} onChange={(v) => setMultiFilter('participantIds', v)} options={participants} />
          <MultiSelect label="Техника" values={filters.techTypeIds} onChange={(v) => setMultiFilter('techTypeIds', v)} options={techTypes} />
          <MultiSelect label="Наличие ЗОУИТ" values={filters.rightOfWayValues} onChange={(v) => setMultiFilter('rightOfWayValues', v)} options={[
            { id: 'yes', name: 'Да' },
            { id: 'no', name: 'Нет' },
          ]} />
          <MultiSelect label="Тип ЗОУИТ" values={filters.zouitTypes} onChange={(v) => setMultiFilter('zouitTypes', v)} options={zouitTypes} />
          <MultiSelect label="Собственник" values={filters.ownerTypes} onChange={(v) => setMultiFilter('ownerTypes', v)} options={ownerTypes} />
          <MultiSelect label="Заполненность" values={filters.completenessValues} onChange={(v) => setMultiFilter('completenessValues', v)} options={COMPLETENESS_OPTIONS} />
        </div>
      </details>
    </div>
  )
}

function DateRangePicker({
  dateFrom,
  dateTo,
  onChange,
}: {
  dateFrom: string
  dateTo: string
  onChange: (dateFrom: string, dateTo: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [viewDate, setViewDate] = useState(() => parseDateValue(dateFrom || dateTo))
  const selectedFrom = dateFrom ? parseDateValue(dateFrom) : null
  const selectedTo = dateTo ? parseDateValue(dateTo) : null
  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

  const days = useMemo(() => {
    const monthStart = startOfMonth(viewDate)
    const monthEnd = endOfMonth(viewDate)
    const calStart = startOfWeek(monthStart, { weekStartsOn: 1 })
    const calEnd = endOfWeek(monthEnd, { weekStartsOn: 1 })
    const result: Date[] = []
    let day = calStart

    while (day <= calEnd) {
      result.push(day)
      day = addDays(day, 1)
    }

    return result
  }, [viewDate])

  const label = dateFrom && dateTo
    ? `${formatDate(dateFrom)} - ${formatDate(dateTo)}`
    : dateFrom
      ? `с ${formatDate(dateFrom)}`
      : 'Все даты'

  const selectDay = (day: Date) => {
    const value = format(day, 'yyyy-MM-dd')

    if (!dateFrom || dateTo) {
      onChange(value, '')
      return
    }

    const start = parseDateValue(dateFrom)
    if (isBefore(day, start)) {
      onChange(value, dateFrom)
    } else {
      onChange(dateFrom, value)
    }
    setOpen(false)
  }

  const clear = () => {
    onChange('', '')
    setOpen(false)
  }

  return (
    <div className="relative">
      <label className="space-y-1.5 block">
        <span className="text-xs font-medium text-text-muted uppercase tracking-wide">Период</span>
        <button
          type="button"
          onClick={() => {
            setViewDate(parseDateValue(dateFrom || dateTo))
            setOpen((current) => !current)
          }}
          className={`w-full rounded-md bg-background border px-3 py-2 text-left text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all cursor-pointer ${
            dateFrom || dateTo ? 'border-primary/60 text-text' : 'border-border text-text-muted'
          }`}
        >
          {label}
        </button>
      </label>

      {open && (
        <div className="absolute left-0 top-[68px] z-50 w-[300px] rounded-xl border border-border bg-surface p-4 shadow-2xl animate-fade-in">
          <div className="flex items-center justify-between mb-3">
            <button type="button" onClick={() => setViewDate(subMonths(viewDate, 1))} className="w-7 h-7 rounded-md hover:bg-surface-hover flex items-center justify-center text-text-muted hover:text-text cursor-pointer">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <span className="text-sm font-semibold capitalize">{format(viewDate, 'LLLL yyyy', { locale: ru })}</span>
            <button type="button" onClick={() => setViewDate(addMonths(viewDate, 1))} className="w-7 h-7 rounded-md hover:bg-surface-hover flex items-center justify-center text-text-muted hover:text-text cursor-pointer">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>

          <div className="grid grid-cols-7 mb-1">
            {weekDays.map((day) => (
              <div key={day} className="text-center text-xs text-text-muted font-medium py-1">{day}</div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-0.5">
            {days.map((day) => {
              const isCurrentMonth = isSameMonth(day, viewDate)
              const isStart = selectedFrom ? isSameDay(day, selectedFrom) : false
              const isEnd = selectedTo ? isSameDay(day, selectedTo) : false
              const inRange = selectedFrom && selectedTo && isAfter(day, selectedFrom) && isBefore(day, selectedTo)

              return (
                <button
                  key={day.toISOString()}
                  type="button"
                  onClick={() => selectDay(day)}
                  className={`h-8 rounded-md text-xs flex items-center justify-center transition-all cursor-pointer
                    ${isStart || isEnd ? 'bg-primary text-white font-bold' : ''}
                    ${inRange ? 'bg-primary/20 text-text' : ''}
                    ${!isStart && !isEnd && !inRange && isCurrentMonth ? 'text-text hover:bg-surface-hover' : ''}
                    ${!isCurrentMonth && !isStart && !isEnd ? 'text-text-muted/40' : ''}
                  `}
                >
                  {format(day, 'd')}
                </button>
              )
            })}
          </div>

          <div className="flex items-center justify-between gap-2 mt-3">
            <button type="button" onClick={clear} className="px-2 py-1.5 rounded-md text-xs text-text-muted hover:bg-surface-hover hover:text-text transition-colors cursor-pointer">
              Сбросить
            </button>
            <span className="text-xs text-text-muted">{dateFrom && !dateTo ? 'Выберите дату окончания' : 'Первый клик - начало, второй - конец'}</span>
          </div>
        </div>
      )}
    </div>
  )
}

function FireTable({ fires, dictionaries, onOpen }: { fires: FireResponse[]; dictionaries: DictionaryMaps; onOpen: (id: number) => void }) {
  const [page, setPage] = useState(1)
  const pageSize = 100
  const totalPages = Math.max(1, Math.ceil(fires.length / pageSize))
  const currentPage = Math.min(page, totalPages)
  const firstRow = (currentPage - 1) * pageSize
  const pageFires = fires.slice(firstRow, firstRow + pageSize)

  if (fires.length === 0) {
    return (
      <div className="p-10 text-center">
        <p className="text-text-muted">Нет пожаров по выбранным фильтрам</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1540px] text-sm">
        <thead className="bg-background text-text-muted">
          <tr>
            {['ID', 'Дата', 'Статус', 'Тип', 'Адрес', 'МО', 'Причина', 'Площадь', 'Собственник', 'Тип ЗОУИТ', 'Участники', 'Ликвидация', 'Обслуживание'].map((head) => (
              <th key={head} className="px-3 py-3 text-left font-medium">{head}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pageFires.map((fire) => (
            <tr key={fire.id} onClick={() => onOpen(fire.id)} className="border-t border-border hover:bg-surface-hover cursor-pointer transition-colors">
              <td className="px-3 py-3 font-mono text-text-muted">#{fire.id}</td>
              <td className="px-3 py-3 whitespace-nowrap">{formatDate(fire.fire_date)}</td>
              <td className="px-3 py-3"><StatusBadge status={fire.status} /></td>
              <td className="px-3 py-3">{fire.is_forest ? 'Лесной' : 'Ландшафтный'}</td>
              <td className="px-3 py-3 max-w-[260px] truncate">{fire.address}</td>
              <td className="px-3 py-3 max-w-[220px] truncate">{dictionaries.municipalities.get(fire.municipality_id || 0) || '—'}</td>
              <td className="px-3 py-3 max-w-[260px] truncate">{dictionaries.reasons.get(fire.reason_id || 0) || '—'}</td>
              <td className="px-3 py-3 whitespace-nowrap">{hasArea(fire) ? `${fire.area} га` : '—'}</td>
              <td className="px-3 py-3 max-w-[260px] truncate">{fire.owner || '—'}</td>
              <td className="px-3 py-3 max-w-[300px] truncate">{fire.right_of_way_type || '—'}</td>
              <td className="px-3 py-3">{fire.participant_events?.length || 0}</td>
              <td className="px-3 py-3 whitespace-nowrap">{fire.end_time ? formatDateTime(fire.end_time) : '—'}</td>
              <td className="px-3 py-3 whitespace-nowrap">{formatDuration(serviceDurationMinutes(fire))}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {totalPages > 1 && (
        <div className="sticky left-0 flex items-center justify-between gap-3 border-t border-border px-4 py-3 text-sm">
          <span className="text-text-muted">
            Строки {firstRow + 1}-{Math.min(firstRow + pageSize, fires.length)} из {fires.length}
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              title="Предыдущая страница"
              aria-label="Предыдущая страница"
              className="grid h-8 w-8 place-items-center rounded-md bg-background text-lg text-text hover:bg-surface-hover disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              ‹
            </button>
            <span className="min-w-24 text-center text-text-muted">
              {currentPage} из {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              title="Следующая страница"
              aria-label="Следующая страница"
              className="grid h-8 w-8 place-items-center rounded-md bg-background text-lg text-text hover:bg-surface-hover disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              ›
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

type DictionaryMaps = {
  municipalities: Map<number, string>
  selsovets: Map<number, string>
  landTypes: Map<number, string>
  forestries: Map<number, string>
  participants: Map<number, string>
  techTypes: Map<number, string>
  reasonGroups: Map<number, string>
  reasons: Map<number, string>
}

const EXPORT_HEADERS = [
  'ID',
  'Дата пожара',
  'Статус',
  'Тип',
  'Адрес',
  'МО',
  'Сельсовет',
  'Лесничество',
  'Состав земли',
  'Причина',
  'Площадь, га',
  'Наличие ЗОУИТ',
  'Тип ЗОУИТ',
  'Собственник',
  'Детальная информация о собственнике',
  'Примечание',
  'Номер карточки ААС КНД',
  'Время сообщения',
  'Дата ликвидации',
  'Время обслуживания',
  'Создал',
  'Проверил',
  'Участники тушения',
] as const

type ExportHeader = (typeof EXPORT_HEADERS)[number]
type ExportRow = Record<ExportHeader, string | number>

function exportRows(fires: FireResponse[], dictionaries: DictionaryMaps): ExportRow[] {
  return fires.map((fire) => ({
    ID: fire.id,
    'Дата пожара': formatDate(fire.fire_date),
    Статус: STATUS_LABELS[fire.status] || fire.status,
    Тип: fire.is_forest ? 'Лесной' : 'Ландшафтный',
    Адрес: fire.address || '',
    МО: dictionaries.municipalities.get(fire.municipality_id || 0) || '',
    Сельсовет: dictionaries.selsovets.get(fire.selsovet_id || 0) || '',
    Лесничество: dictionaries.forestries.get(fire.forestry_id || 0) || '',
    'Состав земли': dictionaries.landTypes.get(fire.land_type_id || 0) || '',
    Причина: dictionaries.reasons.get(fire.reason_id || 0) || '',
    'Площадь, га': fire.area ?? '',
    'Наличие ЗОУИТ': fire.right_of_way ? 'Да' : 'Нет',
    'Тип ЗОУИТ': fire.right_of_way_type || '',
    Собственник: fire.owner || '',
    'Детальная информация о собственнике': fire.source || '',
    Примечание: fire.extra || '',
    'Номер карточки ААС КНД': fire.external_card_number || '',
    'Время сообщения': fire.time_msg ? formatDateTime(fire.time_msg) : '',
    'Дата ликвидации': fire.end_time ? formatDateTime(fire.end_time) : '',
    'Время обслуживания': formatDuration(serviceDurationMinutes(fire)),
    Создал: fire.creator_name || '',
    Проверил: fire.reviewer_name || '',
    'Участники тушения': participantNames(fire, dictionaries),
  }))
}

function exportCsv(fires: FireResponse[], dictionaries: DictionaryMaps) {
  const rows = exportRows(fires, dictionaries)
  const csv = [
    EXPORT_HEADERS.map(csvCell).join(';'),
    ...rows.map((row) => EXPORT_HEADERS.map((header) => csvCell(row[header])).join(';')),
  ].join('\r\n')

  downloadBlob(`fires_${new Date().toISOString().slice(0, 10)}.csv`, new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' }))
}

function participantNames(fire: FireResponse, dictionaries: DictionaryMaps): string {
  return fire.participant_events
    ?.map((event) => {
      const participant = dictionaries.participants.get(event.participant_id) || 'Участник'
      const tech = event.tech_type_id ? dictionaries.techTypes.get(event.tech_type_id) : ''
      return [participant, event.arrival_time, tech].filter(Boolean).join(' / ')
    })
    .join(', ') || ''
}

function csvCell(value: unknown): string {
  let text = String(value ?? '')
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`
  return `"${text.replace(/"/g, '""')}"`
}

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function LoadingState() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-surface rounded-lg p-5 animate-pulse-soft">
          <div className="w-16 h-8 bg-border rounded mb-2" />
          <div className="w-24 h-4 bg-border rounded" />
        </div>
      ))}
    </div>
  )
}

function StatCard({ label, value, suffix = '', tone = 'default' }: { label: string; value: number | string; suffix?: string; tone?: 'default' | 'accent' | 'warning' | 'success' }) {
  const colors = {
    default: 'text-text',
    accent: 'text-accent',
    warning: 'text-warning',
    success: 'text-success',
  }
  return (
    <div className="bg-surface rounded-lg p-4 border border-border">
      <p className={`text-2xl font-bold ${colors[tone]}`}>{value}{suffix}</p>
      <p className="text-text-muted text-xs mt-1">{label}</p>
    </div>
  )
}

function SummaryPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
      <h3 className="text-sm font-semibold">{title}</h3>
      {children}
    </div>
  )
}

function TopList({ title, items, full = false }: { title: string; items: { label: string; value: number }[]; full?: boolean }) {
  const total = items.reduce((sum, item) => sum + item.value, 0)
  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <h3 className="text-sm font-semibold mb-3">{title}</h3>
      {items.length === 0 ? (
        <p className="text-sm text-text-muted">Нет данных</p>
      ) : (
        <div className={`space-y-2 ${full ? 'max-h-[360px] overflow-y-auto pr-1' : ''}`}>
          {items.map((item) => (
            <BarItem key={item.label} label={item.label} value={item.value} total={total} color="bg-primary" />
          ))}
        </div>
      )}
    </div>
  )
}

function BarItem({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  const pct = total > 0 ? (value / total) * 100 : 0
  return (
    <div>
      <div className="flex justify-between gap-3 text-sm mb-1">
        <span className="text-text-muted truncate">{label}</span>
        <span className="font-medium shrink-0">{value}</span>
      </div>
      <div className="h-2 bg-border rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function Input({ label, value, onChange, placeholder, type = 'text' }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string }) {
  return (
    <label className="space-y-1.5 block">
      <span className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</span>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all" />
    </label>
  )
}

function MultiSelect({ label, values, onChange, options }: { label: string; values: string[]; onChange: (values: string[]) => void; options: { id: number | string; name: string }[] }) {
  return (
    <label className="space-y-1.5 block">
      <span className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</span>
      <SearchableMultiSelect values={values} onChange={onChange} options={options} placeholder="Все" />
    </label>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    OPEN: 'bg-primary/20 text-accent',
    IN_REVIEW: 'bg-warning/20 text-warning',
    COMPLETED: 'bg-success/20 text-success',
  }
  return <span className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${styles[status] || 'bg-border text-text-muted'}`}>{STATUS_LABELS[status] || status}</span>
}

function parseDateValue(value: string): Date {
  const parsed = value ? new Date(value + 'T00:00:00') : new Date()
  if (isValid(parsed)) return parsed

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
  return dateStr
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
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

function formatNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}
