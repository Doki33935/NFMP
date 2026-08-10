import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'

const LoginPage = lazy(async () => ({ default: (await import('@/pages/LoginPage')).LoginPage }))
const MainMenuPage = lazy(async () => ({ default: (await import('@/pages/MainMenuPage')).MainMenuPage }))
const FireCreatePage = lazy(async () => ({ default: (await import('@/pages/FireCreatePage')).FireCreatePage }))
const FireListPage = lazy(async () => ({ default: (await import('@/pages/FireListPage')).FireListPage }))
const FireEditPage = lazy(async () => ({ default: (await import('@/pages/FireEditPage')).FireEditPage }))
const FireViewPage = lazy(async () => ({ default: (await import('@/pages/FireViewPage')).FireViewPage }))
const UsersPage = lazy(async () => ({ default: (await import('@/pages/UsersPage')).UsersPage }))
const MonitoringPage = lazy(async () => ({ default: (await import('@/pages/MonitoringPage')).MonitoringPage }))
const ProfilePage = lazy(async () => ({ default: (await import('@/pages/ProfilePage')).ProfilePage }))

function RouteFallback() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto h-24 max-w-4xl animate-pulse rounded-md bg-surface" />
    </div>
  )
}

export function AppRouter() {
  const user = useAuthStore((s) => s.user)
  const hydrated = useAuthStore((s) => s.hydrated)

  if (!hydrated) return <RouteFallback />

  return (
    <BrowserRouter>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/" replace /> : <LoginPage />}
        />

        {/* All protected routes share AppLayout */}
        <Route element={user ? <AppLayout /> : <Navigate to="/login" replace />}>
          <Route path="/" element={<MainMenuPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/fires/create" element={<ProtectedRoute roles={['dispatcher', 'inspector', 'admin']}><FireCreatePage /></ProtectedRoute>} />
          <Route path="/fires" element={<ProtectedRoute roles={['inspector', 'admin']}><FireListPage /></ProtectedRoute>} />
          <Route path="/fires/:id" element={<ProtectedRoute roles={['inspector', 'admin']}><FireEditPage /></ProtectedRoute>} />
          <Route path="/monitoring" element={<ProtectedRoute roles={['admin', 'chief']}><MonitoringPage /></ProtectedRoute>} />
          <Route path="/monitoring/fires/:id" element={<ProtectedRoute roles={['admin', 'chief']}><FireViewPage /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute roles={['admin']}><UsersPage /></ProtectedRoute>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
