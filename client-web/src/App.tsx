import { AppRouter } from './router'
import { ToastContainer } from './components/shared/ToastContainer'
import { AuthSessionGuard } from './components/auth/AuthSessionGuard'

function App() {
  return (
    <>
      <AuthSessionGuard />
      <AppRouter />
      <ToastContainer />
    </>
  )
}

export default App
