import type { FireParticipantEventIn, ParticipantEquipment } from '@/types/fire'
import type { FireParticipant, TechType } from '@/types/references'
import { SearchableSelect } from '@/components/shared/SearchableSelect'
import { TimeInput } from './TimeInput'

const OPTIONAL_RESPONSE_PARTICIPANTS = new Set([
  'Население',
  'Участники тушения пожара отсутствовали',
])

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
  const participantName = participants.find((item) => item.id === value.participant_id)?.name
  const optionalResponse = participantName ? OPTIONAL_RESPONSE_PARTICIPANTS.has(participantName) : false
  const equipment = value.equipment || []

  const updateEquipment = (index: number, next: ParticipantEquipment) => {
    onChange({
      ...value,
      tech_type_id: index === 0 ? next.tech_type_id || null : value.tech_type_id,
      equipment: equipment.map((item, itemIndex) => itemIndex === index ? next : item),
    })
  }

  const removeEquipment = (index: number) => {
    const next = equipment.filter((_, itemIndex) => itemIndex !== index)
    onChange({ ...value, tech_type_id: next[0]?.tech_type_id || null, equipment: next })
  }

  return (
    <div className="flex items-start gap-2 rounded-md border border-border bg-background p-3">
      <div className="min-w-0 flex-1 space-y-3">
        <div className="grid grid-cols-1 gap-2 md:grid-cols-[minmax(0,1fr)_110px]">
          <SearchableSelect
            value={value.participant_id || ''}
            onChange={(selected) => onChange({ ...value, participant_id: selected ? Number(selected) : 0 })}
            options={participants}
            placeholder="Участник тушения"
          />
          <TimeInput
            value={value.arrival_time || ''}
            onChange={(arrivalTime) => onChange({ ...value, arrival_time: arrivalTime || null })}
            className="w-full px-2.5 py-2"
          />
        </div>

        {equipment.map((item, index) => (
          <div key={`${item.tech_type_id}-${index}`} className="grid grid-cols-[minmax(0,1fr)_90px_32px] gap-2">
            <SearchableSelect
              value={item.tech_type_id || ''}
              onChange={(selected) => updateEquipment(index, {
                ...item,
                tech_type_id: selected ? Number(selected) : 0,
              })}
              options={techTypes}
              placeholder="Техника"
            />
            <input
              type="number"
              min={1}
              max={9999}
              value={item.quantity}
              onChange={(event) => updateEquipment(index, {
                ...item,
                quantity: Math.max(1, Number(event.target.value) || 1),
              })}
              aria-label="Количество техники"
              title="Количество"
              className="form-input px-2"
            />
            <button
              type="button"
              onClick={() => removeEquipment(index)}
              title="Убрать технику"
              aria-label="Убрать технику"
              className="grid h-10 w-8 place-items-center rounded-md text-text-muted transition-colors hover:bg-primary/10 hover:text-primary cursor-pointer"
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
        ))}

        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => onChange({
              ...value,
              equipment: [...equipment, { tech_type_id: 0, quantity: 1 }],
            })}
            className="text-sm text-accent transition-colors hover:text-primary-hover cursor-pointer"
          >
            + Добавить технику
          </button>
          {optionalResponse && (
            <span className="text-xs text-text-muted">Время и техника необязательны</span>
          )}
        </div>
      </div>

      <button
        type="button"
        onClick={onRemove}
        title="Удалить участника"
        aria-label="Удалить участника"
        className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-md text-text-muted transition-colors hover:bg-primary/10 hover:text-primary cursor-pointer"
      >
        <span aria-hidden="true">×</span>
      </button>
    </div>
  )
}
