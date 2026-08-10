import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useFireList } from '@/hooks/useFires'

const STATUSES = [
  { value: 'OPEN', label: 'Открытые' },
  { value: 'IN_REVIEW', label: 'На проверке' },
  { value: 'COMPLETED', label: 'Оформленные' },
]

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
  return dateStr
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    OPEN: 'Открыт',
    IN_REVIEW: 'На проверке',
    COMPLETED: 'Оформлен',
  }
  return map[status] || status
}

export function FireListPage() {
  const [status, setStatus] = useState('OPEN')
  const { fires, loading } = useFireList(status)
  const navigate = useNavigate()

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h1 className="text-xl font-bold">Список пожаров</h1>
        </div>

        <div className="flex gap-2 flex-wrap">
          {STATUSES.map((s) => (
            <button
              key={s.value}
              onClick={() => setStatus(s.value)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all cursor-pointer ${
                status === s.value
                  ? 'bg-primary text-white shadow-lg shadow-primary/20'
                  : 'bg-surface text-text-muted hover:bg-surface-hover'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-surface rounded-md p-4 animate-pulse-soft">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-4 bg-border rounded" />
                  <div className="w-20 h-4 bg-border rounded" />
                  <div className="flex-1 h-4 bg-border rounded" />
                  <div className="w-16 h-4 bg-border rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : fires.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-text-muted">Нет пожаров с данным статусом</p>
          </div>
        ) : (
          <div className="space-y-2">
            {fires.map((fire) => (
              <div
                key={fire.id}
                onClick={() => navigate(`/fires/${fire.id}`)}
                className="flex items-center gap-4 bg-surface rounded-md p-4 hover:bg-surface-hover cursor-pointer transition-all hover:translate-x-1 group"
              >
                <span className="text-text-muted text-sm font-mono">
                  #{fire.id}
                </span>
                <span className="text-sm text-text-muted">{formatDate(fire.fire_date)}</span>
                <span className="flex-1 truncate group-hover:text-accent transition-colors">
                  {fire.address}
                </span>
                {fire.area && (
                  <span className="text-text-muted text-xs">{fire.area} га</span>
                )}
                <StatusBadge status={fire.status} />
              </div>
            ))}
          </div>
        )}

        <p className="text-text-muted text-xs text-right">
          Всего: {fires.length}
        </p>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    OPEN: 'bg-primary/20 text-accent',
    IN_REVIEW: 'bg-warning/20 text-warning',
    COMPLETED: 'bg-success/20 text-success',
  }
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || ''}`}>
      {statusLabel(status)}
    </span>
  )
}
