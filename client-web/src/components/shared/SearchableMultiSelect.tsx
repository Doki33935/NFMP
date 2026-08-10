import { useEffect, useMemo, useRef, useState } from 'react'

export type MultiSelectOption = {
  id: number | string
  name: string
}

type SearchableMultiSelectProps = {
  values: string[]
  onChange: (values: string[]) => void
  options: MultiSelectOption[]
  placeholder?: string
}

export function SearchableMultiSelect({
  values,
  onChange,
  options,
  placeholder = 'Все',
}: SearchableMultiSelectProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const rootRef = useRef<HTMLDivElement>(null)
  const selectedValues = useMemo(() => new Set(values.map(String)), [values])

  const filteredOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    if (!normalizedQuery) return options
    return options.filter((option) => option.name.toLowerCase().includes(normalizedQuery))
  }, [options, query])

  const selectedNames = useMemo(
    () => options.filter((option) => selectedValues.has(String(option.id))).map((option) => option.name),
    [options, selectedValues]
  )

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

  const toggleValue = (id: number | string) => {
    const value = String(id)
    onChange(
      selectedValues.has(value)
        ? values.filter((current) => current !== value)
        : [...values, value]
    )
  }

  const summary = selectedNames.length === 0
    ? placeholder
    : selectedNames.length === 1
      ? selectedNames[0]
      : `Выбрано: ${selectedNames.length}`

  return (
    <div ref={rootRef} className="relative">
      <div className="relative">
        <input
          type="text"
          value={open ? query : summary}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
          }}
          onFocus={() => {
            setQuery('')
            setOpen(true)
          }}
          onKeyDown={(event) => {
            if (event.key === 'Escape') {
              setOpen(false)
              setQuery('')
            }
          }}
          className={`w-full rounded-md border bg-background px-3 py-2 pr-10 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all ${
            values.length > 0 ? 'border-primary/60 text-text' : 'border-border text-text-muted'
          }`}
          role="combobox"
          aria-expanded={open}
          aria-autocomplete="list"
        />
        {values.length > 0 && (
          <button
            type="button"
            onClick={() => onChange([])}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-text-muted hover:text-text"
            aria-label="Очистить выбор"
          >
            x
          </button>
        )}
      </div>

      {open && (
        <div className="absolute z-50 mt-1 max-h-72 w-full min-w-[260px] overflow-y-auto rounded-md border border-border bg-surface shadow-xl" role="listbox" aria-multiselectable="true">
          <div className="sticky top-0 flex items-center justify-between gap-2 border-b border-border bg-surface px-3 py-2 text-xs">
            <span className="text-text-muted">Выбрано: {values.length}</span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onChange([...new Set([...values, ...filteredOptions.map((option) => String(option.id))])])}
                className="text-accent hover:text-primary-hover"
              >
                Выбрать найденные
              </button>
              <button type="button" onClick={() => onChange([])} className="text-text-muted hover:text-text">
                Снять все
              </button>
            </div>
          </div>
          {filteredOptions.length > 0 ? (
            filteredOptions.map((option) => {
              const value = String(option.id)
              const selected = selectedValues.has(value)
              return (
                <button
                  key={value}
                  type="button"
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => toggleValue(option.id)}
                  className={`flex w-full items-start gap-2 px-3 py-2 text-left text-sm hover:bg-surface-hover ${selected ? 'bg-primary/10 text-accent' : 'text-text'}`}
                  role="option"
                  aria-selected={selected}
                >
                  <span className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border text-[11px] ${selected ? 'border-primary bg-primary text-white' : 'border-border'}`}>
                    {selected ? '✓' : ''}
                  </span>
                  <span className="leading-5">{option.name}</span>
                </button>
              )
            })
          ) : (
            <div className="px-3 py-2 text-sm text-text-muted">Ничего не найдено</div>
          )}
        </div>
      )}
    </div>
  )
}
