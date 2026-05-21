import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useReferences, useSelsovets, useReasons } from '@/hooks/useReferences'
import { createFire } from '@/hooks/useFires'
import { useToastStore } from '@/store/toast'
import { DateStepWidget } from '@/components/fire/DateStepWidget'
import { FireParticipantRow } from '@/components/fire/FireParticipantRow'
import type { FireParticipantEventIn } from '@/types/fire'

export function FireCreatePage() {
  const navigate = useNavigate()
  const refs = useReferences()
  const toast = useToastStore((s) => s.add)

  const [fireDate, setFireDate] = useState<string>(
    new Date().toISOString().slice(0, 10)
  )
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
  const [participants, setParticipants] = useState<FireParticipantEventIn[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const selsovets = useSelsovets(municipalityId)
  const reasons = useReasons(reasonGroupId)

  const addParticipant = () => {
    setParticipants([
      ...participants,
      { participant_id: 0, arrival_time: '', tech_type_id: null },
    ])
  }

  const removeParticipant = (idx: number) => {
    setParticipants(participants.filter((_, i) => i !== idx))
  }

  const updateParticipant = (idx: number, p: FireParticipantEventIn) => {
    setParticipants(participants.map((cur, i) => (i === idx ? p : cur)))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!address.trim()) {
      setError('Укажите адрес')
      return
    }

    setSaving(true)
    try {
      await createFire({
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
        participants: participants.filter((p) => p.participant_id > 0),
      })
      toast('Пожар создан', 'success')
      navigate('/')
    } catch {
      setError('Ошибка при создании')
    } finally {
      setSaving(false)
    }
  }

  if (refs.loading) {
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

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Новый пожар</h1>
          <p className="text-text-muted text-sm mt-1">Заполните карточку учёта ландшафтного пожара</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Основная информация */}
          <Section
            icon="M12 2c1 3 2.5 3.5 3.5 4.5A5 5 0 0 1 17 10a5 5 0 0 1-5 5 5 5 0 0 1-5-5c0-1.5.5-2 1-3 .5 1.5 1.5 2 2 2a2 2 0 0 0 2-2c0-1.5-1-2-1-4z"
            title="Событие"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Дата пожара">
                <DateStepWidget value={fireDate} onChange={setFireDate} />
              </Field>
              <Field label="Тип пожара">
                <div className="flex gap-2">
                  <TypeButton
                    active={isForest}
                    onClick={() => setIsForest(true)}
                    label="Лесной"
                    icon="M12 2L2 22h20L12 2z"
                  />
                  <TypeButton
                    active={!isForest}
                    onClick={() => { setIsForest(false); setForestryId(null) }}
                    label="Ландшафтный"
                    icon="M2 22h20M4 22V8l4-2v16M12 22V6l4-2v18M20 22V4"
                  />
                </div>
              </Field>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Состав земли *">
                <Select
                  value={landTypeId}
                  onChange={(v) => setLandTypeId(v ? Number(v) : '')}
                  options={refs.landTypes}
                  placeholder="Состав земли"
                />
              </Field>
              <Field label="Причина (краткая)">
                <Select
                  value={reasonGroupId || ''}
                  onChange={(v) => {
                    setReasonGroupId(v ? Number(v) : null)
                    setReasonId(null)
                  }}
                  options={refs.reasonGroups}
                  placeholder="Причина пожара"
                />
              </Field>
              <Field label="Площадь (га)">
                <Input value={area} onChange={setArea} placeholder="0.5" />
              </Field>
            </div>
            {reasons.length > 0 && (
              <Field label="Подпричина">
                <Select
                  value={reasonId || ''}
                  onChange={(v) => setReasonId(v ? Number(v) : null)}
                  options={reasons}
                  placeholder="Подпричина пожара"
                />
              </Field>
            )}
          </Section>

          {/* Местоположение */}
          <Section
            icon="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0zM12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"
            title="Местоположение"
          >
            <Field label="Адрес *">
              <Input value={address} onChange={setAddress} placeholder="Населённый пункт, ориентир..." />
            </Field>
            <Field label="Комментарий к адресу">
              <Input value={addressComment} onChange={setAddressComment} placeholder="Дополнительные сведения..." />
            </Field>
            <div className={`grid grid-cols-1 ${selsovets.length > 0 ? 'md:grid-cols-2' : ''} gap-4`}>
              <Field label="Муниципальное образование">
                <Select
                  value={municipalityId || ''}
                  onChange={(v) => {
                    setMunicipalityId(v ? Number(v) : null)
                    setSelsovetId(null)
                  }}
                  options={refs.municipalities}
                  placeholder="Муниципальное образование"
                />
              </Field>
              {selsovets.length > 0 && (
                <Field label="Сельсовет">
                  <Select
                    value={selsovetId || ''}
                    onChange={(v) => setSelsovetId(v ? Number(v) : null)}
                    options={selsovets}
                    placeholder="Сельсовет"
                  />
                </Field>
              )}
            </div>
          </Section>

          {/* Контекст */}
          <Section
            icon="M9 12h6M9 16h6M13 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-5-5zM13 4v5h5"
            title="Дополнительно"
          >
            {isForest && (
              <Field label="Лесничество *">
                <Select
                  value={forestryId || ''}
                  onChange={(v) => setForestryId(v ? Number(v) : null)}
                  options={refs.forestries}
                  placeholder="Лесничество"
                />
              </Field>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Полоса отвода">
                <div className="flex items-center gap-3 h-10">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rightOfWay}
                      onChange={(e) => {
                        setRightOfWay(e.target.checked)
                        if (!e.target.checked) setRightOfWayType('')
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-border rounded-full peer peer-checked:bg-primary transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-transform peer-checked:after:translate-x-4" />
                  </label>
                  <span className="text-sm text-text-muted">{rightOfWay ? 'Да' : 'Нет'}</span>
                </div>
              </Field>
              {rightOfWay && (
                <Field label="Тип полосы отвода">
                  <Select
                    value={rightOfWayType}
                    onChange={(v) => setRightOfWayType(v)}
                    options={[
                      { id: 'railway' as unknown as number, name: 'Ж/Д' },
                      { id: 'road' as unknown as number, name: 'Автодорога' },
                      { id: 'powerline' as unknown as number, name: 'ЛЭП' },
                    ]}
                    placeholder="Тип полосы"
                  />
                </Field>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Собственник">
                <Input value={owner} onChange={setOwner} placeholder="ФИО или организация" />
              </Field>
              <Field label="Источник информации">
                <Input value={source} onChange={setSource} placeholder="Откуда поступила информация" />
              </Field>
            </div>
            <Field label="Примечание">
              <textarea
                value={extra}
                onChange={(e) => setExtra(e.target.value)}
                rows={2}
                className="w-full rounded-lg bg-background border border-border px-3 py-2.5 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all resize-none"
              />
            </Field>
          </Section>

          {/* Участники */}
          <Section
            icon="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"
            title="Участники тушения"
          >
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
            <button
              type="button"
              onClick={addParticipant}
              className="flex items-center gap-2 text-sm text-accent hover:text-primary-hover transition-colors cursor-pointer group"
            >
              <span className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
              </span>
              Добавить участника
            </button>
          </Section>

          {/* Error & Submit */}
          {error && (
            <div className="bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 text-sm text-accent">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-6 py-3 rounded-lg bg-surface text-text-muted font-medium hover:bg-surface-hover transition-colors cursor-pointer"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 rounded-lg bg-primary py-3 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-all active:scale-[0.99] cursor-pointer shadow-lg shadow-primary/20"
            >
              {saving ? 'Сохранение...' : 'Зарегистрировать пожар'}
            </button>
          </div>
        </form>
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

function Input({
  value,
  onChange,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full rounded-lg bg-background border border-border px-3 py-2.5 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all"
    />
  )
}

function Select({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: number | string
  onChange: (v: string) => void
  options: { id: number; name: string }[]
  placeholder?: string
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`w-full rounded-lg bg-background border border-border px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all appearance-none styled-select ${value === '' || value === 0 ? 'text-text-muted' : 'text-text'}`}
    >
      <option value="" disabled hidden>{placeholder || ''}</option>
      <option value=""></option>
      {options.map((o) => (
        <option key={o.id} value={o.id}>
          {o.name}
        </option>
      ))}
    </select>
  )
}

function TypeButton({
  active,
  onClick,
  label,
  icon,
}: {
  active: boolean
  onClick: () => void
  label: string
  icon: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer border ${
        active
          ? 'bg-primary/10 border-primary text-accent'
          : 'bg-background border-border text-text-muted hover:border-text-muted'
      }`}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d={icon} />
      </svg>
      {label}
    </button>
  )
}
