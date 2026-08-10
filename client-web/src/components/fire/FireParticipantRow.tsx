import type { FireParticipantEventIn } from '@/types/fire'
import type { FireParticipant, TechType } from '@/types/references'
import { SearchableSelect } from '@/components/shared/SearchableSelect'
import { TimeInput } from './TimeInput'

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
        <SearchableSelect
          value={value.participant_id || ''}
          onChange={(v) =>
            onChange({ ...value, participant_id: v ? Number(v) : 0 })
          }
          options={participants}
          placeholder="Участник тушения"
        />

        <div className="flex gap-2">
          <div className="flex-1">
            <SearchableSelect
            value={value.tech_type_id || ''}
            onChange={(v) =>
              onChange({
                ...value,
                tech_type_id: v ? Number(v) : null,
              })
            }
            options={techTypes}
            placeholder="Техника"
          />
          </div>

          <TimeInput
            value={value.arrival_time}
            onChange={(v) => onChange({ ...value, arrival_time: v })}
            className="w-[70px] px-2.5 py-2"
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
