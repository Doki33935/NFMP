import { useState, useRef, useEffect } from 'react'
import {
  format,
  addDays,
  subDays,
  isToday,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addMonths,
  subMonths,
  isSameMonth,
  isSameDay,
  isAfter,
  isValid,
} from 'date-fns'
import { ru } from 'date-fns/locale'

interface Props {
  value: string
  onChange: (v: string) => void
  attention?: boolean
}

function parseDateValue(value: string): Date {
  const parsed = value ? new Date(value + 'T00:00:00') : new Date()
  if (isValid(parsed)) return parsed

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

export function DateStepWidget({ value, onChange, attention = false }: Props) {
  const [open, setOpen] = useState(false)
  const [viewDate, setViewDate] = useState(() => parseDateValue(value))
  const ref = useRef<HTMLDivElement>(null)
  const date = parseDateValue(value)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const prev = () => onChange(format(subDays(date, 1), 'yyyy-MM-dd'))
  const next = () => {
    if (!isToday(date)) onChange(format(addDays(date, 1), 'yyyy-MM-dd'))
  }

  const selectDay = (d: Date) => {
    if (isAfter(d, today)) return
    onChange(format(d, 'yyyy-MM-dd'))
    setOpen(false)
  }

  const renderCalendar = () => {
    const monthStart = startOfMonth(viewDate)
    const monthEnd = endOfMonth(viewDate)
    const calStart = startOfWeek(monthStart, { weekStartsOn: 1 })
    const calEnd = endOfWeek(monthEnd, { weekStartsOn: 1 })

    const days: Date[] = []
    let d = calStart
    while (d <= calEnd) {
      days.push(d)
      d = addDays(d, 1)
    }

    return days
  }

  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

  return (
    <div className="relative" ref={ref}>
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={prev}
          className="w-8 h-8 rounded-md bg-surface-hover text-text-muted flex items-center justify-center hover:bg-border hover:text-text transition-colors cursor-pointer"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>

        <button
          type="button"
          onClick={() => { setViewDate(date); setOpen(!open) }}
          className={`flex-1 min-w-[140px] h-8 rounded-md bg-background border px-3 text-sm font-medium text-text hover:border-primary transition-colors cursor-pointer text-center ${
            attention ? 'border-warning ring-1 ring-warning/40 bg-warning/10' : 'border-border'
          }`}
        >
          {format(date, 'd MMMM yyyy', { locale: ru })}
        </button>

        <button
          type="button"
          onClick={next}
          disabled={isToday(date)}
          className="w-8 h-8 rounded-md bg-surface-hover text-text-muted flex items-center justify-center hover:bg-border hover:text-text disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>

      {open && (
        <div className="absolute top-10 left-0 z-50 bg-surface border border-border rounded-xl shadow-2xl p-4 w-[280px] animate-fade-in">
          {/* Month navigation */}
          <div className="flex items-center justify-between mb-3">
            <button
              type="button"
              onClick={() => setViewDate(subMonths(viewDate, 1))}
              className="w-7 h-7 rounded-md hover:bg-surface-hover flex items-center justify-center text-text-muted hover:text-text cursor-pointer"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <span className="text-sm font-semibold capitalize">
              {format(viewDate, 'LLLL yyyy', { locale: ru })}
            </span>
            <button
              type="button"
              onClick={() => setViewDate(addMonths(viewDate, 1))}
              className="w-7 h-7 rounded-md hover:bg-surface-hover flex items-center justify-center text-text-muted hover:text-text cursor-pointer"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>

          {/* Week days header */}
          <div className="grid grid-cols-7 mb-1">
            {weekDays.map((wd) => (
              <div key={wd} className="text-center text-xs text-text-muted font-medium py-1">
                {wd}
              </div>
            ))}
          </div>

          {/* Days grid */}
          <div className="grid grid-cols-7 gap-0.5">
            {renderCalendar().map((d, i) => {
              const isSelected = isSameDay(d, date)
              const isCurrentMonth = isSameMonth(d, viewDate)
              const isFuture = isAfter(d, today)
              const isNow = isSameDay(d, today)

              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => selectDay(d)}
                  disabled={isFuture}
                  className={`w-8 h-8 rounded-md text-xs flex items-center justify-center transition-all cursor-pointer
                    ${isSelected ? 'bg-primary text-white font-bold' : ''}
                    ${!isSelected && isNow ? 'ring-1 ring-primary text-accent font-medium' : ''}
                    ${!isSelected && !isNow && isCurrentMonth ? 'text-text hover:bg-surface-hover' : ''}
                    ${!isCurrentMonth && !isSelected ? 'text-text-muted/40' : ''}
                    ${isFuture ? 'opacity-20 cursor-not-allowed' : ''}
                  `}
                >
                  {format(d, 'd')}
                </button>
              )
            })}
          </div>

          {/* Today button */}
          <button
            type="button"
            onClick={() => selectDay(today)}
            className="w-full mt-3 py-1.5 rounded-md text-xs font-medium text-accent hover:bg-primary/10 transition-colors cursor-pointer"
          >
            Сегодня
          </button>
        </div>
      )}
    </div>
  )
}
