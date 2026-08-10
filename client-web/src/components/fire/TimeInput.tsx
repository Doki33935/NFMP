interface Props {
  value: string
  onChange: (v: string) => void
  attention?: boolean
  className?: string
}

function attentionClasses(attention: boolean): string {
  return attention ? 'border-warning bg-warning/10 ring-1 ring-warning/40' : 'border-border bg-background'
}

export function TimeInput({ value, onChange, attention = false, className = 'w-full px-3 py-2.5' }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^\d]/g, '').slice(0, 4)

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
    <input
      type="text"
      inputMode="numeric"
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      placeholder="00:00"
      className={`${className} rounded-lg border text-sm text-text text-center placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all tabular-nums ${attentionClasses(attention)}`}
    />
  )
}
