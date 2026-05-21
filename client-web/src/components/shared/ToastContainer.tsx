import { useToastStore } from '@/store/toast'

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts)
  const remove = useToastStore((s) => s.remove)

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          onClick={() => remove(toast.id)}
          className={`px-4 py-3 rounded-lg shadow-lg cursor-pointer animate-slide-in text-sm font-medium ${
            toast.type === 'success'
              ? 'bg-success/90 text-white'
              : toast.type === 'error'
              ? 'bg-primary/90 text-white'
              : 'bg-surface text-text border border-border'
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  )
}
