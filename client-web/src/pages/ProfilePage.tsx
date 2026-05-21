import { useState } from 'react'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'
import api from '@/lib/api'

const ROLE_LABELS: Record<string, string> = {
  dispatcher: 'Диспетчер',
  inspector: 'Инспектор',
  admin: 'Администратор',
  chief: 'Руководитель',
}

export function ProfilePage() {
  const user = useAuthStore((s) => s.user)!
  const toast = useToastStore((s) => s.add)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword.length < 3) {
      toast('Пароль должен быть не менее 3 символов', 'error')
      return
    }
    if (newPassword !== confirmPassword) {
      toast('Пароли не совпадают', 'error')
      return
    }
    setSaving(true)
    try {
      await api.put(`/users/${user.id}/password`, { new_password: newPassword })
      toast('Пароль изменён', 'success')
      setNewPassword('')
      setConfirmPassword('')
    } catch {
      toast('Ошибка при смене пароля', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-lg mx-auto space-y-6">
        <h1 className="text-xl font-bold">Профиль</h1>

        <div className="bg-surface rounded-lg p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center">
              <span className="text-accent text-xl font-bold">
                {user.full_name.charAt(0)}
              </span>
            </div>
            <div>
              <p className="font-semibold text-lg">{user.full_name}</p>
              <p className="text-text-muted text-sm">@{user.username}</p>
            </div>
          </div>

          <div className="border-t border-border pt-4 space-y-2">
            <InfoRow label="Роль" value={ROLE_LABELS[user.role] || user.role} />
          </div>
        </div>

        <form onSubmit={handleChangePassword} className="bg-surface rounded-lg p-6 space-y-4">
          <h2 className="text-accent font-semibold text-base">Сменить пароль</h2>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Новый пароль</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Подтвердите пароль</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
              required
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-md bg-primary py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer"
          >
            {saving ? 'Сохранение...' : 'Сменить пароль'}
          </button>
        </form>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  )
}
