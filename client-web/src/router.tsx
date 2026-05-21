import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { AppLayout } from '@/components/layout/AppLayout'
import { LoginPage } from '@/pages/LoginPage'
import { MainMenuPage } from '@/pages/MainMenuPage'
import { FireCreatePage } from '@/pages/FireCreatePage'
import { FireListPage } from '@/pages/FireListPage'
import { FireEditPage } from '@/pages/FireEditPage'
import { UsersPage } from '@/pages/UsersPage'
import { MonitoringPage } from '@/pages/MonitoringPage'
import { ProfilePage } from '@/pages/ProfilePage'

export function AppRouter() {
  const user = useAuthStore((s) => s.user)

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/" replace /> : <LoginPage />}
        />

        {/* All protected routes share AppLayout */}
        <Route element={user ? <AppLayout /> : <Navigate to="/login" replace />}>
          <Route path="/" element={<MainMenuPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/fires/create" element={<FireCreatePage />} />
          <Route path="/fires" element={<FireListPage />} />
          <Route path="/fires/:id" element={<FireEditPage />} />
          <Route path="/monitoring" element={<MonitoringPage />} />
          <Route path="/users" element={<UsersPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
