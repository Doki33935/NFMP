import { useEffect, useMemo, useRef, useState } from 'react'

export type SelectOption = {
  id: number | string
  name: string
}

type SearchableSelectProps = {
  value: number | string
  onChange: (value: string) => void
  options: SelectOption[]
  placeholder?: string
  emptyLabel?: string
  attention?: boolean
}

export function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = 'Выберите значение',
  emptyLabel = 'Не выбрано',
  attention = false,
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const rootRef = useRef<HTMLDivElement>(null)

  const selected = useMemo(
    () => options.find((option) => String(option.id) === String(value)),
    [options, value]
  )

  const normalizedQuery = query.trim().toLowerCase()
  const filteredOptions = useMemo(() => {
    if (!normalizedQuery) return options
    return options.filter((option) => option.name.toLowerCase().includes(normalizedQuery))
  }, [normalizedQuery, options])

  useEffect(() => {
    if (!open) return

    const handlePointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false)
        setQuery('')
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [open])

  return (
    <div ref={rootRef} className="relative">
      <input
        type="text"
        value={open ? query : selected?.name || ''}
        onChange={(event) => {
          setQuery(event.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(event) => {
          if (event.key === 'Escape') {
            setOpen(false)
            setQuery('')
          }
        }}
        placeholder={selected ? selected.name : placeholder}
        className={`w-full rounded-lg border px-3 py-2.5 pr-10 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all ${
          attention ? 'border-warning bg-warning/10 ring-1 ring-warning/40' : 'border-border bg-background'
        } ${value === '' || value === 0 ? 'text-text-muted' : 'text-text'}`}
        role="combobox"
        aria-expanded={open}
        aria-autocomplete="list"
      />
      <button
        type="button"
        onClick={() => {
          onChange('')
          setQuery('')
          setOpen(false)
        }}
        className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-text-muted hover:text-text"
        aria-label="Очистить выбор"
      >
        x
      </button>

      {open && (
        <div className="absolute z-30 mt-1 max-h-60 w-full overflow-y-auto rounded-lg border border-border bg-surface shadow-xl">
          <button
            type="button"
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => {
              onChange('')
              setOpen(false)
              setQuery('')
            }}
            className="block w-full px-3 py-2 text-left text-sm text-text-muted hover:bg-surface-hover"
          >
            {emptyLabel}
          </button>
          {filteredOptions.length > 0 ? (
            filteredOptions.map((option) => (
              <button
                key={String(option.id)}
                type="button"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => {
                  onChange(String(option.id))
                  setOpen(false)
                  setQuery('')
                }}
                className={`block w-full px-3 py-2 text-left text-sm hover:bg-surface-hover ${
                  String(option.id) === String(value) ? 'bg-primary/15 text-accent' : 'text-text'
                }`}
              >
                {option.name}
              </button>
            ))
          ) : (
            <div className="px-3 py-2 text-sm text-text-muted">Ничего не найдено</div>
          )}
        </div>
      )}
    </div>
  )
}
