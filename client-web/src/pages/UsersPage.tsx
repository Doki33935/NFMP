import { useState, useEffect, useCallback } from 'react'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/store/toast'
import api from '@/lib/api'
import { SearchableSelect } from '@/components/shared/SearchableSelect'
import type { User, UserUpdate } from '@/types/user'

const ROLES = [
  { id: 'dispatcher', name: 'Диспетчер' },
  { id: 'inspector', name: 'Дознаватель' },
  { id: 'admin', name: 'Администратор' },
  { id: 'chief', name: 'Руководитель' },
]

const ROLE_LABELS: Record<string, string> = Object.fromEntries(ROLES.map((role) => [role.id, role.name]))

type UserItem = User

export function UsersPage() {
  const currentUser = useAuthStore((s) => s.user)!
  const updateCurrentUser = useAuthStore((s) => s.updateUser)
  const toast = useToastStore((s) => s.add)
  const [users, setUsers] = useState<UserItem[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirmation, setPasswordConfirmation] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('dispatcher')
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')
  const [editingUser, setEditingUser] = useState<UserItem | null>(null)
  const [editUsername, setEditUsername] = useState('')
  const [editFullName, setEditFullName] = useState('')
  const [editRole, setEditRole] = useState('dispatcher')
  const [editPassword, setEditPassword] = useState('')
  const [editPasswordConfirmation, setEditPasswordConfirmation] = useState('')
  const [savingEdit, setSavingEdit] = useState(false)

  const loadUsers = useCallback(async () => {
    try {
      const res = await api.get<UserItem[]>('/users')
      setUsers(res.data)
    } catch (err) {
      console.error('Failed to load users:', err)
      toast('Не удалось загрузить пользователей', 'error')
    } finally {
      setLoadingUsers(false)
    }
  }, [toast])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadUsers(), 0)
    return () => window.clearTimeout(timer)
  }, [loadUsers])

  const startEdit = (user: UserItem) => {
    setEditingUser(user)
    setEditUsername(user.username)
    setEditFullName(user.full_name)
    setEditRole(user.role)
    setEditPassword('')
    setEditPasswordConfirmation('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== passwordConfirmation) {
      toast('Пароли не совпадают', 'error')
      return
    }
    setSaving(true)
    try {
      await api.post('/users', {
        username: username.trim(),
        password,
        password_confirmation: passwordConfirmation,
        full_name: fullName.trim(),
        role,
      })
      setUsername('')
      setPassword('')
      setPasswordConfirmation('')
      setFullName('')
      setRole('dispatcher')
      toast('Пользователь создан', 'success')
      loadUsers()
    } catch (err) {
      console.error('Failed to create user:', err)
      toast('Ошибка при создании пользователя', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return
    if (editPassword && editPassword !== editPasswordConfirmation) {
      toast('Пароли не совпадают', 'error')
      return
    }

    const payload: UserUpdate = {
      username: editUsername.trim(),
      full_name: editFullName.trim(),
      role: editRole,
    }
    if (editPassword) {
      payload.password = editPassword
      payload.password_confirmation = editPasswordConfirmation
    }

    setSavingEdit(true)
    try {
      const res = await api.put<UserItem>(`/users/${editingUser.id}`, payload)
      toast('Пользователь обновлён', 'success')
      if (res.data.id === currentUser.id) updateCurrentUser(res.data)
      setEditingUser(null)
      loadUsers()
    } catch (err) {
      console.error(`Failed to update user id=${editingUser.id}:`, err)
      toast('Ошибка при сохранении пользователя', 'error')
    } finally {
      setSavingEdit(false)
    }
  }

  const handleDelete = async (user: UserItem) => {
    if (!confirm(`Отключить пользователя "${user.full_name}"?`)) return
    try {
      await api.delete(`/users/${user.id}`)
      toast('Пользователь отключён', 'success')
      if (editingUser?.id === user.id) setEditingUser(null)
      loadUsers()
    } catch (err) {
      console.error(`Failed to disable user id=${user.id}:`, err)
      toast(`Ошибка при отключении "${user.username}"`, 'error')
    }
  }

  const handleRestore = async (user: UserItem) => {
    try {
      await api.post(`/users/${user.id}/restore`)
      toast('Пользователь восстановлен', 'success')
      loadUsers()
    } catch (err) {
      console.error(`Failed to restore user id=${user.id}:`, err)
      toast(`Ошибка при восстановлении "${user.username}"`, 'error')
    }
  }

  const filteredUsers = users.filter((u) => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      u.full_name.toLowerCase().includes(q) ||
      u.username.toLowerCase().includes(q) ||
      (ROLE_LABELS[u.role] || u.role).toLowerCase().includes(q)
    )
  })

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Пользователи</h1>

        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,360px)_1fr] gap-6 items-start">
          <form onSubmit={handleSubmit} className="space-y-4 bg-surface rounded-md p-6">
            <h2 className="text-accent font-semibold text-base">Новый пользователь</h2>
            <Field label="Логин">
              <input value={username} onChange={(e) => setUsername(e.target.value)} className="form-input" required />
            </Field>
            <Field label="Пароль">
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="form-input" minLength={12} required />
            </Field>
            <Field label="Подтвердите пароль">
              <input type="password" value={passwordConfirmation} onChange={(e) => setPasswordConfirmation(e.target.value)} className="form-input" minLength={12} required />
            </Field>
            <Field label="ФИО">
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="form-input" required />
            </Field>
            <Field label="Права">
              <SearchableSelect value={role} onChange={(value) => setRole(value || 'dispatcher')} options={ROLES} placeholder="Права" />
            </Field>
            <button type="submit" disabled={saving} className="w-full rounded-md bg-primary py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer">
              {saving ? 'Создание...' : 'Создать'}
            </button>
          </form>

          <div className="space-y-4">
            <div className="space-y-3 bg-surface rounded-md p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h2 className="text-accent font-semibold text-base">Список пользователей</h2>
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Поиск..." className="form-input sm:max-w-xs" />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-sm">
                  <thead className="text-text-muted border-b border-border">
                    <tr>
                      <th className="text-left font-medium py-2 pr-3">ФИО</th>
                      <th className="text-left font-medium py-2 pr-3">Логин</th>
                      <th className="text-left font-medium py-2 pr-3">Права</th>
                      <th className="text-right font-medium py-2">Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loadingUsers ? (
                      <tr><td className="py-4 text-text-muted" colSpan={4}>Загрузка...</td></tr>
                    ) : filteredUsers.length === 0 ? (
                      <tr><td className="py-4 text-text-muted" colSpan={4}>Ничего не найдено</td></tr>
                    ) : (
                      filteredUsers.map((u) => (
                        <tr key={u.id} className="border-b border-border/60 last:border-0">
                          <td className="py-3 pr-3 font-medium">
                            {u.full_name}
                            {u.is_active === false && <span className="ml-2 text-xs text-text-muted">Отключён</span>}
                          </td>
                          <td className="py-3 pr-3 text-text-muted">@{u.username}</td>
                          <td className="py-3 pr-3">{ROLE_LABELS[u.role] || u.role}</td>
                          <td className="py-3">
                            <div className="flex justify-end gap-2">
                              <button onClick={() => startEdit(u)} disabled={u.is_active === false} className="px-3 py-1.5 rounded-md bg-background hover:bg-surface-hover text-sm cursor-pointer disabled:cursor-not-allowed disabled:opacity-40">
                                Изменить
                              </button>
                              {u.is_active === false ? (
                                <button onClick={() => handleRestore(u)} className="px-3 py-1.5 rounded-md text-accent hover:bg-surface-hover text-sm cursor-pointer">Восстановить</button>
                              ) : (
                                <button onClick={() => handleDelete(u)} className="px-3 py-1.5 rounded-md text-text-muted hover:text-primary hover:bg-surface-hover text-sm cursor-pointer">Отключить</button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {editingUser && (
              <form onSubmit={handleSaveEdit} className="space-y-4 bg-surface rounded-md p-6">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="text-accent font-semibold text-base">Редактирование пользователя</h2>
                  <button type="button" onClick={() => setEditingUser(null)} className="text-sm text-text-muted hover:text-text cursor-pointer">Закрыть</button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Field label="ФИО">
                    <input value={editFullName} onChange={(e) => setEditFullName(e.target.value)} className="form-input" required />
                  </Field>
                  <Field label="Логин">
                    <input value={editUsername} onChange={(e) => setEditUsername(e.target.value)} className="form-input" required />
                  </Field>
                  <Field label="Права">
                    <SearchableSelect value={editRole} onChange={(value) => setEditRole(value || 'dispatcher')} options={ROLES} placeholder="Права" />
                  </Field>
                  <Field label="Новый пароль">
                    <input type="password" value={editPassword} onChange={(e) => setEditPassword(e.target.value)} placeholder="Оставьте пустым без изменений" className="form-input" minLength={12} />
                  </Field>
                  <Field label="Подтвердите новый пароль">
                    <input type="password" value={editPasswordConfirmation} onChange={(e) => setEditPasswordConfirmation(e.target.value)} placeholder="Повторите новый пароль" className="form-input" minLength={12} required={Boolean(editPassword)} />
                  </Field>
                </div>
                <button type="submit" disabled={savingEdit} className="rounded-md bg-primary px-5 py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer">
                  {savingEdit ? 'Сохранение...' : 'Сохранить изменения'}
                </button>
              </form>
            )}
          </div>
        </div>
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
