import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'

const ROLE_NAMES: Record<string, string> = {
  dispatcher: 'Диспетчер',
  inspector: 'Дознаватель',
  admin: 'Администратор',
  chief: 'Руководитель',
}

interface Action {
  label: string
  path: string
  description: string
  icon: string
}

const ROLE_ACTIONS: Record<string, Action[]> = {
  dispatcher: [
    { label: 'Регистрация пожара', path: '/fires/create', description: 'Зарегистрировать новый инцидент', icon: 'M12 4v16m-8-8h16' },
  ],
  inspector: [
    { label: 'Регистрация пожара', path: '/fires/create', description: 'Зарегистрировать новый инцидент', icon: 'M12 4v16m-8-8h16' },
    { label: 'Список пожаров', path: '/fires', description: 'Просмотр и редактирование', icon: 'M4 6h16M4 12h16M4 18h16' },
  ],
  admin: [
    { label: 'Регистрация пожара', path: '/fires/create', description: 'Зарегистрировать новый инцидент', icon: 'M12 4v16m-8-8h16' },
    { label: 'Список пожаров', path: '/fires', description: 'Просмотр и редактирование', icon: 'M4 6h16M4 12h16M4 18h16' },
    { label: 'Мониторинг', path: '/monitoring', description: 'Сводка и статистика', icon: 'M3 3v18h18M7 16l4-4 4 4 5-5' },
    { label: 'Пользователи', path: '/users', description: 'Управление аккаунтами', icon: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75' },
  ],
  chief: [
    { label: 'Мониторинг', path: '/monitoring', description: 'Сводка и статистика', icon: 'M3 3v18h18M7 16l4-4 4 4 5-5' },
  ],
}

export function MainMenuPage() {
  const user = useAuthStore((s) => s.user)!
  const navigate = useNavigate()

  const actions = ROLE_ACTIONS[user.role] || []
  const isSingle = actions.length === 1

  return (
    <div className="p-6 animate-fade-in flex items-center justify-center min-h-[calc(100svh-57px)]">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">
            Добро пожаловать, {user.full_name.split(' ')[0]}
          </h1>
          <p className="text-text-muted">
            {ROLE_NAMES[user.role] || user.role}
          </p>
        </div>

        <div className={`grid gap-4 ${isSingle ? 'grid-cols-1 max-w-sm mx-auto' : 'grid-cols-1 sm:grid-cols-2'}`}>
          {actions.map((a) => (
            <button
              key={a.path}
              onClick={() => navigate(a.path)}
              className={`group bg-surface rounded-xl p-8 text-center hover:bg-surface-hover transition-all hover:scale-[1.02] hover:shadow-lg cursor-pointer border border-transparent hover:border-border ${isSingle ? 'py-12' : ''}`}
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 mx-auto group-hover:bg-primary/20 transition-colors">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
                  <path d={a.icon} />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-1 group-hover:text-accent transition-colors">
                {a.label}
              </h3>
              <p className="text-text-muted text-sm">{a.description}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
