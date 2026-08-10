import { useState } from 'react'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'
import api from '@/lib/api'
import type { User } from '@/types/user'

const ROLE_LABELS: Record<string, string> = {
  dispatcher: 'Диспетчер',
  inspector: 'Дознаватель',
  admin: 'Администратор',
  chief: 'Руководитель',
}

export function ProfilePage() {
  const user = useAuthStore((s) => s.user)!
  const updateUser = useAuthStore((s) => s.updateUser)
  const toast = useToastStore((s) => s.add)
  const [fullName, setFullName] = useState(user.full_name)
  const [username, setUsername] = useState(user.username)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fullName.trim() || !username.trim()) {
      toast('Заполните ФИО и логин', 'error')
      return
    }

    setSavingProfile(true)
    try {
      const res = await api.put<User>(`/users/${user.id}`, {
        full_name: fullName.trim(),
        username: username.trim(),
      })
      updateUser(res.data)
      toast('Профиль обновлён', 'success')
    } catch {
      toast('Не удалось обновить профиль', 'error')
    } finally {
      setSavingProfile(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword.length < 12) {
      toast('Пароль должен быть не менее 12 символов', 'error')
      return
    }
    if (newPassword !== confirmPassword) {
      toast('Пароли не совпадают', 'error')
      return
    }
    setSavingPassword(true)
    try {
      await api.put(`/users/${user.id}/password`, {
        current_password: currentPassword,
        new_password: newPassword,
        password_confirmation: confirmPassword,
      })
      toast('Пароль изменён', 'success')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch {
      toast('Ошибка при смене пароля', 'error')
    } finally {
      setSavingPassword(false)
    }
  }

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Профиль</h1>

        <div className="bg-surface rounded-md p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
              <span className="text-accent text-xl font-bold">
                {(user.full_name || user.username || '?').charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-lg truncate">{user.full_name}</p>
              <p className="text-text-muted text-sm truncate">@{user.username}</p>
            </div>
          </div>

          <div className="border-t border-border pt-4 space-y-2">
            <InfoRow label="Роль" value={ROLE_LABELS[user.role] || user.role} />
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="bg-surface rounded-md p-6 space-y-4">
          <h2 className="text-accent font-semibold text-base">Данные профиля</h2>
          <Field label="ФИО">
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="form-input" required />
          </Field>
          <Field label="Логин">
            <input value={username} onChange={(e) => setUsername(e.target.value)} className="form-input" required />
          </Field>
          <button type="submit" disabled={savingProfile} className="w-full rounded-md bg-primary py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer">
            {savingProfile ? 'Сохранение...' : 'Сохранить профиль'}
          </button>
        </form>

        <form onSubmit={handleChangePassword} className="bg-surface rounded-md p-6 space-y-4">
          <h2 className="text-accent font-semibold text-base">Сменить пароль</h2>
          <Field label="Текущий пароль">
            <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} className="form-input" autoComplete="current-password" required />
          </Field>
          <Field label="Новый пароль">
            <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className="form-input" minLength={12} autoComplete="new-password" required />
          </Field>
          <Field label="Подтвердите пароль">
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="form-input" minLength={12} autoComplete="new-password" required />
          </Field>
          <button type="submit" disabled={savingPassword} className="w-full rounded-md bg-primary py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer">
            {savingPassword ? 'Сохранение...' : 'Сменить пароль'}
          </button>
        </form>
      </div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="space-y-1 block">
      <span className="text-sm font-medium text-text-muted">{label}</span>
      {children}
    </label>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 text-sm">
      <span className="text-text-muted">{label}</span>
      <span className="font-medium text-right">{value}</span>
    </div>
  )
}
