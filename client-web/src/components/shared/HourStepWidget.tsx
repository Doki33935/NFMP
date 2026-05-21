interface Props {
  value: number
  onChange: (v: number) => void
}

export function HourStepWidget({ value, onChange }: Props) {
  const prev = () => {
    if (value > 1) onChange(value - 1)
  }

  const next = () => {
    if (value < 24) onChange(value + 1)
  }

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={prev}
        disabled={value <= 1}
        className="w-8 h-8 rounded bg-surface-hover text-text flex items-center justify-center hover:bg-border disabled:opacity-30 cursor-pointer"
      >
        &lt;
      </button>
      <span className="text-sm font-medium min-w-[60px] text-center">
        {String(value).padStart(2, '0')}:00
      </span>
      <button
        type="button"
        onClick={next}
        disabled={value >= 24}
        className="w-8 h-8 rounded bg-surface-hover text-text flex items-center justify-center hover:bg-border disabled:opacity-30 cursor-pointer"
      >
        &gt;
      </button>
    </div>
  )
}
