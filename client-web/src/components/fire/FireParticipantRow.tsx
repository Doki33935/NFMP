import type { FireParticipantEventIn } from '@/types/fire'
import type { FireParticipant, TechType } from '@/types/references'

interface Props {
  value: FireParticipantEventIn
  onChange: (v: FireParticipantEventIn) => void
  onRemove: () => void
  participants: FireParticipant[]
  techTypes: TechType[]
}

export function FireParticipantRow({
  value,
  onChange,
  onRemove,
  participants,
  techTypes,
}: Props) {
  return (
    <div className="flex items-start gap-2 bg-background rounded-lg border border-border p-3">
      <div className="flex-1 space-y-2">
        <select
          value={value.participant_id || ''}
          onChange={(e) =>
            onChange({ ...value, participant_id: Number(e.target.value) })
          }
          className={`w-full rounded-lg bg-surface border border-border px-3 py-2 text-sm focus:outline-none focus:border-primary appearance-none styled-select ${value.participant_id ? 'text-text' : 'text-text-muted'}`}
        >
          <option value="" disabled hidden>Участник тушения</option>
          <option value=""></option>
          {participants.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <div className="flex gap-2">
          <select
            value={value.tech_type_id || ''}
            onChange={(e) =>
              onChange({
                ...value,
                tech_type_id: e.target.value ? Number(e.target.value) : null,
              })
            }
            className={`flex-1 rounded-lg bg-surface border border-border px-3 py-2 text-sm focus:outline-none focus:border-primary appearance-none styled-select ${value.tech_type_id ? 'text-text' : 'text-text-muted'}`}
          >
            <option value="" disabled hidden>Техника</option>
            <option value=""></option>
            {techTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>

          <TimeInput
            value={value.arrival_time}
            onChange={(v) => onChange({ ...value, arrival_time: v })}
          />
        </div>
      </div>

      <button
        type="button"
        onClick={onRemove}
        className="mt-2 w-7 h-7 rounded-md flex items-center justify-center text-text-muted hover:text-primary hover:bg-primary/10 transition-colors cursor-pointer shrink-0"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </div>
  )
}

function TimeInput({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let raw = e.target.value.replace(/[^\d]/g, '').slice(0, 4)

    // Auto-insert colon after 2 digits
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
    // Allow backspace to work naturally
    if (e.key === 'Backspace' && value.endsWith(':')) {
      e.preventDefault()
      onChange(value.slice(0, -1))
    }
  }

  return (
    <input
      type="text"
      inputMode="numeric"
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      placeholder="00:00"
      className="w-[70px] rounded-lg bg-surface border border-border px-2.5 py-2 text-sm text-text text-center placeholder:text-text-muted focus:outline-none focus:border-primary tabular-nums"
    />
  )
}
