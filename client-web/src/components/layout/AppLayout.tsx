import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import api from '@/lib/api'

const ROLE_NAV: Record<string, { label: string; path: string }[]> = {
  dispatcher: [
    { label: 'Регистрация пожара', path: '/fires/create' },
  ],
  inspector: [
    { label: 'Регистрация пожара', path: '/fires/create' },
    { label: 'Пожары', path: '/fires' },
  ],
  admin: [
    { label: 'Регистрация пожара', path: '/fires/create' },
    { label: 'Пожары', path: '/fires' },
    { label: 'Мониторинг', path: '/monitoring' },
    { label: 'Пользователи', path: '/users' },
  ],
  chief: [
    { label: 'Мониторинг', path: '/monitoring' },
  ],
}

export function AppLayout() {
  const user = useAuthStore((s) => s.user)!
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const navItems = ROLE_NAV[user.role] || []

  const handleLogout = async () => {
    await api.post('/logout').catch(() => {})
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-svh flex flex-col">
      {/* Header */}
      <header className="bg-surface border-b border-border px-4 md:px-6 py-3 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-6">
          <NavLink to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2c1 3 2.5 3.5 3.5 4.5A5 5 0 0 1 17 10a5 5 0 0 1-5 5 5 5 0 0 1-5-5c0-1.5.5-2 1-3 .5 1.5 1.5 2 2 2a2 2 0 0 0 2-2c0-1.5-1-2-1-4z"/>
                <path d="M12 15v7"/>
              </svg>
            </div>
            <span className="font-bold text-sm hidden sm:inline">NFMP</span>
          </NavLink>

          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm transition-colors ${
                    isActive
                      ? 'bg-primary/10 text-accent font-medium'
                      : 'text-text-muted hover:text-text hover:bg-surface-hover'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <NavLink
            to="/profile"
            className="text-sm text-text-muted hover:text-text transition-colors"
          >
            {user.full_name}
          </NavLink>
          <button
            onClick={handleLogout}
            className="text-xs text-text-muted hover:text-primary transition-colors cursor-pointer"
          >
            Выйти
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
