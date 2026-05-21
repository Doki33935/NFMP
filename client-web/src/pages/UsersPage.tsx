import { useState, useEffect, useCallback } from 'react'
import { useToastStore } from '@/store/toast'
import api from '@/lib/api'

const ROLES = [
  { value: 'dispatcher', label: 'Диспетчер' },
  { value: 'inspector', label: 'Инспектор' },
  { value: 'admin', label: 'Администратор' },
  { value: 'chief', label: 'Руководитель' },
]

const ROLE_LABELS: Record<string, string> = {
  dispatcher: 'Диспетчер',
  inspector: 'Инспектор',
  admin: 'Администратор',
  chief: 'Руководитель',
}

interface UserItem {
  id: number
  username: string
  role: string
  full_name: string
}

export function UsersPage() {
  const toast = useToastStore((s) => s.add)
  const [users, setUsers] = useState<UserItem[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('dispatcher')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)
  const [search, setSearch] = useState('')

  const loadUsers = useCallback(async () => {
    try {
      const res = await api.get<UserItem[]>('/users')
      setUsers(res.data)
    } catch (err) {
      console.error('Failed to load users:', err)
    } finally {
      setLoadingUsers(false)
    }
  }, [])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setSaving(true)
    try {
      await api.post('/users', {
        username,
        password,
        full_name: fullName,
        role,
      })
      setMessage('Пользователь создан')
      setIsError(false)
      setUsername('')
      setPassword('')
      setFullName('')
      toast('Пользователь создан', 'success')
      loadUsers()
    } catch (err) {
      console.error('Failed to create user:', err)
      setMessage('Ошибка при создании')
      setIsError(true)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (user: UserItem) => {
    if (!confirm(`Удалить пользователя "${user.full_name}"?`)) return
    try {
      await api.delete(`/users/${user.id}`)
      toast('Пользователь удалён', 'success')
      loadUsers()
    } catch (err) {
      console.error(`Failed to delete user id=${user.id}:`, err)
      toast(`Ошибка при удалении "${user.username}"`, 'error')
    }
  }

  const filteredUsers = users.filter((u) => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      u.full_name.toLowerCase().includes(q) ||
      u.username.toLowerCase().includes(q)
    )
  })

  return (
    <div className="p-4 md:p-6 animate-fade-in">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">Пользователи</h1>

        {/* Форма создания */}
        <form
          onSubmit={handleSubmit}
          className="space-y-4 bg-surface rounded-md p-6"
        >
          <h2 className="text-accent font-semibold text-base">Новый пользователь</h2>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Логин</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">ФИО</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Роль</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text focus:outline-none focus:border-primary"
            >
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {message && (
            <p className={`text-sm ${isError ? 'text-primary' : 'text-success'}`}>
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-md bg-primary py-2 font-medium text-white hover:bg-primary-hover disabled:opacity-50 transition-colors cursor-pointer"
          >
            {saving ? 'Создание...' : 'Создать'}
          </button>
        </form>

        {/* Удаление пользователей */}
        <div className="space-y-3 bg-surface rounded-md p-6">
          <h2 className="text-accent font-semibold text-base">Удаление пользователей</h2>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по имени или логину..."
            className="w-full rounded-md bg-background border border-border px-3 py-2 text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-primary"
          />
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {loadingUsers ? (
              <p className="text-text-muted text-sm">Загрузка...</p>
            ) : filteredUsers.length === 0 ? (
              <p className="text-text-muted text-sm">
                {search ? 'Ничего не найдено' : 'Нет пользователей'}
              </p>
            ) : (
              filteredUsers.map((u) => (
                <div
                  key={u.id}
                  className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-surface-hover"
                >
                  <div>
                    <span className="font-medium text-sm">{u.full_name}</span>
                    <span className="text-text-muted text-sm ml-2">
                      @{u.username}
                    </span>
                    <span className="text-text-muted text-xs ml-2">
                      {ROLE_LABELS[u.role] || u.role}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(u)}
                    className="text-text-muted hover:text-primary text-sm cursor-pointer"
                  >
                    Удалить
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
