import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { useReferences, useSelsovets, useReasons } from '@/hooks/useReferences'
import { useFire, updateFire } from '@/hooks/useFires'
import { useToastStore } from '@/store/toast'
import api from '@/lib/api'
import { DateStepWidget } from '@/components/fire/DateStepWidget'
import { FireParticipantRow } from '@/components/fire/FireParticipantRow'
import type { FireParticipantEventIn } from '@/types/fire'

function normalizeTime(value: string | null | undefined): string {
  if (!value) return ''
  const timeMatch = value.match(/(\d{2}):(\d{2})/)
  return timeMatch ? `${timeMatch[1]}:${timeMatch[2]}` : value
}

function localDateString(date = new Date()): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function FireEditPage() {
  const { id } = useParams<{ id: string }>()
  const user = useAuthStore((s) => s.user)!
  const navigate = useNavigate()
  const { fire, loading: fireLoading } = useFire(id!)
  const refs = useReferences()
  const toast = useToastStore((s) => s.add)

  const [fireDate, setFireDate] = useState('')
  const [isForest, setIsForest] = useState(true)
  const [landTypeId, setLandTypeId] = useState<number | ''>('')
  const [area, setArea] = useState('')
  const [address, setAddress] = useState('')
  const [addressComment, setAddressComment] = useState('')
  const [municipalityId, setMunicipalityId] = useState<number | null>(null)
  const [selsovetId, setSelsovetId] = useState<number | null>(null)
  const [forestryId, setForestryId] = useState<number | null>(null)
  const [reasonGroupId, setReasonGroupId] = useState<number | null>(null)
  const [reasonId, setReasonId] = useState<number | null>(null)
  const [rightOfWay, setRightOfWay] = useState(false)
  const [rightOfWayType, setRightOfWayType] = useState('')
  const [owner, setOwner] = useState('')
  const [source, setSource] = useState('')
  const [extra, setExtra] = useState('')
  const [externalCardNumber, setExternalCardNumber] = useState('')
  const [endDate, setEndDate] = useState('')
  const [endTime, setEndTime] = useState('12:00')
  const [liquidationTouched, setLiquidationTouched] = useState(false)
  const [participants, setParticipants] = useState<FireParticipantEventIn[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const selsovets = useSelsovets(municipalityId)
  const reasons = useReasons(reasonGroupId)

  useEffect(() => {
    if (!fire) return
    setFireDate(fire.fire_date)
    setIsForest(fire.is_forest)
    setLandTypeId(fire.land_type_id ?? '')
    setArea(fire.area != null ? String(fire.area) : '')
    setAddress(fire.address)
    setAddressComment(fire.address_comment || '')
    setMunicipalityId(fire.municipality_id || null)
    setSelsovetId(fire.selsovet_id || null)
    setForestryId(fire.forestry_id || null)
    setReasonId(fire.reason_id || null)
    if (fire.reason_id) {
      api
        .get('/references/reasons')
        .then((r) => {
          const reason = r.data.find((x: { id: number; group_id: number | null }) => x.id === fire.reason_id)
          setReasonGroupId(reason?.group_id ?? null)
        })
        .catch(() => setReasonGroupId(null))
    } else {
      setReasonGroupId(null)
    }
    setRightOfWay(fire.right_of_way || false)
    setRightOfWayType(fire.right_of_way_type || '')
    setOwner(fire.owner || '')
    setSource(fire.source || '')
    setExtra(fire.extra || '')
    setExternalCardNumber(fire.external_card_number || '')
    if (fire.end_time) {
      const d = new Date(fire.end_time)
      if (Number.isNaN(d.getTime())) {
        setEndDate(localDateString())
        setEndTime('12:00')
      } else {
        setEndDate(localDateString(d))
        setEndTime(`${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`)
      }
    } else {
      setEndDate(localDateString())
      setEndTime('12:00')
    }
    setLiquidationTouched(false)
    if (fire.participant_events) {
      setParticipants(
        fire.participant_events.map((pe) => ({
          participant_id: pe.participant_id,
          arrival_time: normalizeTime(pe.arrival_time),
          tech_type_id: pe.tech_type_id || null,
          comment: pe.comment || '',
        }))
      )
    }
  }, [fire])

  const addParticipant = () => {
    setParticipants([...participants, { participant_id: 0, arrival_time: '', tech_type_id: null }])
  }

  const removeParticipant = (idx: number) => {
    setParticipants(participants.filter((_, i) => i !== idx))
  }

  const updateParticipant = (idx: number, p: FireParticipantEventIn) => {
    setParticipants(participants.map((cur, i) => (i === idx ? p : cur)))
  }

  const buildPayload = () => ({
    fire_date: fireDate,
    is_forest: isForest,
    land_type_id: landTypeId ? Number(landTypeId) : null,
    area: area ? parseFloat(area.replace(',', '.')) : null,
    address: address.trim(),
    address_comment: addressComment || undefined,
    municipality_id: municipalityId,
    selsovet_id: selsovetId,
    forestry_id: forestryId,
    reason_id: reasonId,
    right_of_way: rightOfWay,
    right_of_way_type: rightOfWay ? rightOfWayType : undefined,
    owner: owner || undefined,
    source: source || undefined,
    extra: extra || undefined,
    external_card_number: externalCardNumber || undefined,
    reviewer_id: user.id,
    end_time: endDate ? `${endDate}T${endTime || '12:00'}:00` : undefined,
    participants: participants.filter((p) => p.participant_id > 0),
  })

  const handleSave = async () => {
    setError('')

    // При оформлении — все поля обязательны
    if (fire!.status === 'IN_REVIEW') {
      if (!landTypeId) { setError('Для оформления укажите состав земли'); return }
      if (!area) { setError('Для оформления укажите площадь'); return }
      if (isForest && !forestryId) { setError('Для оформления укажите лесничество'); return }
      if (!reasonGroupId) { setError('Для оформления укажите причину пожара'); return }
      if (!reasonId) { setError('Для оформления укажите подпричину пожара'); return }
      if (!source) { setError('Для оформления укажите источник информации'); return }
      if (!owner) { setError('Для оформления укажите собственника'); return }
      if (!externalCardNumber) { setError('Для оформления укажите номер карточки ААС КНД'); return }
    }

    setSaving(true)
    try {
      const payload = buildPayload()
      if (fire!.status === 'IN_REVIEW') {
        (payload as Record<string, unknown>).status = 'COMPLETED'
      }
      await updateFire(Number(id), payload)
      toast(fire!.status === 'IN_REVIEW' ? 'КУЛП оформлен' : 'Сохранено', 'success')
      navigate('/fires')
    } catch {
      setError('Ошибка при сохранении')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Удалить карту пожара? Это действие необратимо.')) return
    setSaving(true)
    try {
      await api.delete(`/fires/${id}`)
      toast('Карта пожара удалена', 'success')
      navigate('/fires')
    } catch {
      setError('Ошибка при удалении')
    } finally {
      setSaving(false)
    }
  }

  if (fireLoading || refs.loading || (fire && !fireDate)) {
    return (
      <div className="p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-surface rounded-xl p-6 animate-pulse-soft">
              <div className="w-32 h-5 bg-border rounded mb-4" />
              <div className="space-y-3">
                <div className="w-full h-10 bg-border rounded-lg" />
                <div className="w-2/3 h-10 bg-border rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!fire) {
    return <div className="p-6 text-primary">Пожар не найден</div>
  }

  const isCompleted = fire.status === 'COMPLETED'
  const needsAttention = !isCompleted
  const isLiquidationDefault = needsAttention && !fire.end_time && !liquidationTouched && endTime === '12:00'
  const missingLandType = needsAttention && !landTypeId
  const missingArea = needsAttention && !area
  const missingForestry = needsAttention && isForest && !forestryId
  const missingReasonGroup = needsAttention && !reasonGroupId
  const missingReason = needsAttention && !reasonId
  const missingOwner = needsAttention && !owner.trim()
  const missingSource = needsAttention && !source.trim()
  const missingExternalCard = needsAttention && !externalCardNumber.trim()

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Пожар #{fire.id}</h1>
          <p className="text-text-muted text-sm mt-1">
            {isCompleted ? 'Просмотр оформленного КУЛП' : 'Редактирование карточки учёта'}
          </p>
        </div>

        <div className="space-y-5">
          {/* Событие */}
          <Section icon="M12 2c1 3 2.5 3.5 3.5 4.5A5 5 0 0 1 17 10a5 5 0 0 1-5 5 5 5 0 0 1-5-5c0-1.5.5-2 1-3 .5 1.5 1.5 2 2 2a2 2 0 0 0 2-2c0-1.5-1-2-1-4z" title="Событие">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Дата пожара">
                <DateStepWidget value={fireDate} onChange={setFireDate} />
              </Field>
              <Field label="Тип пожара">
                <div className="flex gap-2">
                  <TypeButton active={isForest} onClick={() => setIsForest(true)} label="Лесной" icon="M12 2L2 22h20L12 2z" />
                  <TypeButton active={!isForest} onClick={() => { setIsForest(false); setForestryId(null) }} label="Ландшафтный" icon="M2 22h20M4 22V8l4-2v16M12 22V6l4-2v18M20 22V4" />
                </div>
              </Field>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Состав земли" attention={missingLandType}>
                <Select value={landTypeId} onChange={(v) => setLandTypeId(v ? Number(v) : '')} options={refs.landTypes} placeholder="Состав земли" attention={missingLandType} />
              </Field>
              <Field label="Причина (краткая)" attention={missingReasonGroup}>
                <Select value={reasonGroupId || ''} onChange={(v) => { setReasonGroupId(v ? Number(v) : null); setReasonId(null) }} options={refs.reasonGroups} placeholder="Причина" attention={missingReasonGroup} />
              </Field>
              <Field label="Площадь (га)" attention={missingArea}>
                <Input value={area} onChange={setArea} placeholder="0.5" attention={missingArea} />
              </Field>
            </div>
            {reasons.length > 0 && (
              <Field label="Подпричина" attention={missingReason}>
                <Select value={reasonId || ''} onChange={(v) => setReasonId(v ? Number(v) : null)} options={reasons} placeholder="Подпричина" attention={missingReason} />
              </Field>
            )}
          </Section>

          {/* Местоположение */}
          <Section icon="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0zM12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" title="Местоположение">
            <Field label="Адрес">
              <Input value={address} onChange={setAddress} placeholder="Населённый пункт, ориентир..." />
            </Field>
            <Field label="Комментарий к адресу">
              <Input value={addressComment} onChange={setAddressComment} />
            </Field>
            <div className={`grid grid-cols-1 ${selsovets.length > 0 ? 'md:grid-cols-2' : ''} gap-4`}>
              <Field label="Муниципальное образование">
                <Select value={municipalityId || ''} onChange={(v) => { setMunicipalityId(v ? Number(v) : null); setSelsovetId(null) }} options={refs.municipalities} placeholder="МО" />
              </Field>
              {selsovets.length > 0 && (
                <Field label="Сельсовет">
                  <Select value={selsovetId || ''} onChange={(v) => setSelsovetId(v ? Number(v) : null)} options={selsovets} placeholder="Сельсовет" />
                </Field>
              )}
            </div>
          </Section>

          {/* Дополнительно */}
          <Section icon="M9 12h6M9 16h6M13 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-5-5zM13 4v5h5" title="Дополнительно">
            {isForest && (
              <Field label="Лесничество" attention={missingForestry}>
                <Select value={forestryId || ''} onChange={(v) => setForestryId(v ? Number(v) : null)} options={refs.forestries} placeholder="Лесничество" attention={missingForestry} />
              </Field>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Полоса отвода">
                <div className="flex items-center gap-3 h-10">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" checked={rightOfWay} onChange={(e) => { setRightOfWay(e.target.checked); if (!e.target.checked) setRightOfWayType('') }} className="sr-only peer" />
                    <div className="w-9 h-5 bg-border rounded-full peer peer-checked:bg-primary transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-transform peer-checked:after:translate-x-4" />
                  </label>
                  <span className="text-sm text-text-muted">{rightOfWay ? 'Да' : 'Нет'}</span>
                </div>
              </Field>
              {rightOfWay && (
                <Field label="Тип полосы отвода">
                  <Select value={rightOfWayType} onChange={(v) => setRightOfWayType(v)} options={[{ id: 'railway' as unknown as number, name: 'Ж/Д' }, { id: 'road' as unknown as number, name: 'Автодорога' }, { id: 'powerline' as unknown as number, name: 'ЛЭП' }]} placeholder="Тип полосы" />
                </Field>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Собственник" attention={missingOwner}>
                <Input value={owner} onChange={setOwner} placeholder="ФИО или организация" attention={missingOwner} />
              </Field>
              <Field label="Источник информации" attention={missingSource}>
                <Input value={source} onChange={setSource} placeholder="Откуда поступила информация" attention={missingSource} />
              </Field>
            </div>
            <Field label="Примечание">
              <textarea value={extra} onChange={(e) => setExtra(e.target.value)} rows={2} className="w-full rounded-lg bg-background border border-border px-3 py-2.5 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all resize-none" />
            </Field>
            <Field label="Номер карточки ААС КНД" attention={missingExternalCard}>
              <Input value={externalCardNumber} onChange={setExternalCardNumber} placeholder="Номер карточки" attention={missingExternalCard} />
            </Field>
          </Section>

          {/* Ликвидация */}
          {!isCompleted && (
            <Section icon="M9 12l2 2 4-4M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" title="Ликвидация">
              <div className="flex gap-4 items-end">
                <div className="flex-1">
                  <Field label="Дата ликвидации" attention={isLiquidationDefault}>
                    <DateStepWidget value={endDate} onChange={(v) => { setLiquidationTouched(true); setEndDate(v) }} attention={isLiquidationDefault} />
                  </Field>
                </div>
                <div className="w-28">
                  <Field label="Время" attention={isLiquidationDefault}>
                    <TimeInput value={endTime} onChange={(v) => { setLiquidationTouched(true); setEndTime(v) }} attention={isLiquidationDefault} />
                  </Field>
                </div>
              </div>
            </Section>
          )}

          {/* Участники тушения */}
          <Section icon="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" title="Участники тушения">
            {participants.length > 0 && (
              <div className="space-y-2">
                {participants.map((p, idx) => (
                  <FireParticipantRow
                    key={idx}
                    value={p}
                    onChange={(v) => updateParticipant(idx, v)}
                    onRemove={() => removeParticipant(idx)}
                    participants={refs.participants}
                    techTypes={refs.techTypes}
                  />
                ))}
              </div>
            )}
            <button type="button" onClick={addParticipant} className="flex items-center gap-2 text-sm text-accent hover:text-primary-hover transition-colors cursor-pointer group">
              <span className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
              </span>
              Добавить участника
            </button>
          </Section>

          {/* Служебная информация */}
          <Section icon="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" title="Служебная информация">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Info label="Создал" value={fire.creator_name || '—'} />
              <Info label="Проверяющий" value={fire.reviewer_name || '—'} />
              <Info label="Время сообщения" value={fire.time_msg ? new Date(fire.time_msg).toLocaleString('ru-RU') : '—'} />
              <Info label="Статус" value={fire.status === 'OPEN' ? 'Открыт' : fire.status === 'IN_REVIEW' ? 'На проверке' : 'Оформлен'} />
            </div>
          </Section>

          {/* Error & Actions */}
          {error && (
            <div className="bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 text-sm text-accent">
              {error}
            </div>
          )}

          {!isCompleted && (
            <div className="flex gap-3 pt-2">
              <button onClick={handleDelete} disabled={saving} className="px-5 py-3 rounded-lg bg-surface text-text-muted font-medium hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer">
                Удалить
              </button>
              <button onClick={() => navigate('/fires')} className="px-5 py-3 rounded-lg bg-surface text-text-muted font-medium hover:bg-surface-hover transition-colors cursor-pointer">
                Назад
              </button>
              <button onClick={handleSave} disabled={saving} className="flex-1 rounded-lg bg-primary py-3 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-all active:scale-[0.99] cursor-pointer shadow-lg shadow-primary/20">
                {saving ? 'Сохранение...' : fire.status === 'IN_REVIEW' ? 'Оформить КУЛП' : 'Сохранить'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// --- Sub-components ---

function Section({ icon, title, children }: { icon: string; title: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface rounded-xl border border-border p-5 md:p-6 space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
            <path d={icon} />
          </svg>
        </div>
        <h2 className="font-semibold text-base">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function Field({ label, children, attention = false }: { label: string; children: React.ReactNode; attention?: boolean }) {
  return (
    <div className={`space-y-1.5 rounded-lg transition-colors ${attention ? 'bg-warning/5' : ''}`}>
      <label className={`text-xs font-medium uppercase tracking-wide ${attention ? 'text-warning' : 'text-text-muted'}`}>
        {label}
      </label>
      {children}
    </div>
  )
}

function attentionClasses(attention: boolean): string {
  return attention ? 'border-warning bg-warning/10 ring-1 ring-warning/40' : 'border-border bg-background'
}

function Input({ value, onChange, placeholder, attention = false }: { value: string; onChange: (v: string) => void; placeholder?: string; attention?: boolean }) {
  return (
    <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={`w-full rounded-lg border px-3 py-2.5 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all ${attentionClasses(attention)}`} />
  )
}

function Select({ value, onChange, options, placeholder, attention = false }: { value: number | string; onChange: (v: string) => void; options: { id: number; name: string }[]; placeholder?: string; attention?: boolean }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className={`w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all appearance-none styled-select ${attentionClasses(attention)} ${value === '' || value === 0 ? 'text-text-muted' : 'text-text'}`}>
      <option value="" disabled hidden>{placeholder || ''}</option>
      <option value=""></option>
      {options.map((o) => (<option key={o.id} value={o.id}>{o.name}</option>))}
    </select>
  )
}

function TypeButton({ active, onClick, label, icon }: { active: boolean; onClick: () => void; label: string; icon?: string }) {
  return (
    <button type="button" onClick={onClick} className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer border ${active ? 'bg-primary/10 border-primary text-accent' : 'bg-background border-border text-text-muted hover:border-text-muted'}`}>
      {icon && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d={icon} /></svg>}
      {label}
    </button>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-background rounded-lg px-4 py-3">
      <p className="text-xs text-text-muted uppercase tracking-wide mb-0.5">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  )
}

function TimeInput({ value, onChange, attention = false }: { value: string; onChange: (v: string) => void; attention?: boolean }) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let raw = e.target.value.replace(/[^\d]/g, '').slice(0, 4)
    if (raw.length >= 3) {
      let h = raw.slice(0, 2)
      let m = raw.slice(2)
      if (Number(h) > 23) h = '23'
      if (m.length === 2 && Number(m) > 59) m = '59'
      onChange(`${h}:${m}`)
    } else if (raw.length === 2) {
      let h = raw
      if (Number(h) > 23) h = '23'
      onChange(`${h}:`)
    } else {
      onChange(raw)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && value.endsWith(':')) {
      e.preventDefault()
      onChange(value.slice(0, -1))
    }
  }

  return (
    <input type="text" inputMode="numeric" value={value} onChange={handleChange} onKeyDown={handleKeyDown} placeholder="00:00" className={`w-full rounded-lg border px-3 py-2.5 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all tabular-nums ${attentionClasses(attention)}`} />
  )
}
