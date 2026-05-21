import { useNavigate } from 'react-router-dom'
import { useFireList } from '@/hooks/useFires'

export function MonitoringPage() {
  const navigate = useNavigate()
  const { fires: openFires, loading: loadingOpen } = useFireList('OPEN')
  const { fires: reviewFires, loading: loadingReview } = useFireList('IN_REVIEW')
  const { fires: completedFires, loading: loadingCompleted } = useFireList('COMPLETED')

  const loading = loadingOpen || loadingReview || loadingCompleted
  const allActive = [...openFires, ...reviewFires]

  // Stats
  const totalArea = allActive.reduce((sum, f) => sum + (f.area || 0), 0)
  const forestFires = allActive.filter((f) => f.is_forest).length
  const landscapeFires = allActive.length - forestFires

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Мониторинг</h1>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-surface rounded-lg p-5 animate-pulse-soft">
                <div className="w-12 h-8 bg-border rounded mb-2" />
                <div className="w-20 h-4 bg-border rounded" />
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Stats cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Открытые" count={openFires.length} color="text-accent" bg="bg-primary/10" />
              <StatCard label="На проверке" count={reviewFires.length} color="text-warning" bg="bg-warning/10" />
              <StatCard label="Завершённые" count={completedFires.length} color="text-success" bg="bg-success/10" />
              <StatCard label="Общая площадь" count={totalArea} suffix=" га" color="text-text" bg="bg-surface" />
            </div>

            {/* Type breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-surface rounded-lg p-5">
                <h3 className="text-sm font-medium text-text-muted mb-3">По типу (активные)</h3>
                <div className="space-y-3">
                  <BarItem label="Лесные" value={forestFires} total={allActive.length} color="bg-success" />
                  <BarItem label="Ландшафтные" value={landscapeFires} total={allActive.length} color="bg-warning" />
                </div>
              </div>

              <div className="bg-surface rounded-lg p-5">
                <h3 className="text-sm font-medium text-text-muted mb-3">Статусы</h3>
                <div className="space-y-3">
                  <BarItem label="Открытые" value={openFires.length} total={openFires.length + reviewFires.length + completedFires.length} color="bg-primary" />
                  <BarItem label="На проверке" value={reviewFires.length} total={openFires.length + reviewFires.length + completedFires.length} color="bg-warning" />
                  <BarItem label="Завершённые" value={completedFires.length} total={openFires.length + reviewFires.length + completedFires.length} color="bg-success" />
                </div>
              </div>
            </div>

            {/* Active fires list */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-accent font-semibold text-base">
                  Активные пожары ({allActive.length})
                </h2>
              </div>
              {allActive.length === 0 ? (
                <div className="bg-surface rounded-lg p-8 text-center">
                  <p className="text-text-muted">Нет активных пожаров</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {allActive.map((fire) => (
                    <div
                      key={fire.id}
                      onClick={() => navigate(`/fires/${fire.id}`)}
                      className="flex items-center gap-4 bg-surface rounded-md p-4 hover:bg-surface-hover cursor-pointer transition-all hover:translate-x-1"
                    >
                      <span className="text-text-muted text-sm font-mono">
                        #{fire.id}
                      </span>
                      <span className="text-sm text-text-muted">{fire.fire_date}</span>
                      <span className="flex-1 truncate">{fire.address}</span>
                      {fire.area && (
                        <span className="text-text-muted text-xs">{fire.area} га</span>
                      )}
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          fire.status === 'OPEN'
                            ? 'bg-primary/20 text-accent'
                            : 'bg-warning/20 text-warning'
                        }`}
                      >
                        {fire.status === 'OPEN' ? 'Открыт' : 'На проверке'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function StatCard({
  label,
  count,
  color,
  bg,
  suffix = '',
}: {
  label: string
  count: number
  color: string
  bg: string
  suffix?: string
}) {
  return (
    <div className={`${bg} rounded-lg p-5 border border-border`}>
      <p className={`text-3xl font-bold ${color}`}>
        {Number.isInteger(count) ? count : count.toFixed(1)}{suffix}
      </p>
      <p className="text-text-muted text-sm mt-1">{label}</p>
    </div>
  )
}

function BarItem({
  label,
  value,
  total,
  color,
}: {
  label: string
  value: number
  total: number
  color: string
}) {
  const pct = total > 0 ? (value / total) * 100 : 0
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-text-muted">{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <div className="h-2 bg-border rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
