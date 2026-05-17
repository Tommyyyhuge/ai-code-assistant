import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, useNavigate } from 'react-router-dom'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.tsx'
import ErrorBoundary from './components/ErrorBoundary.tsx'
import { setNavigateCallback } from './services/api.ts'

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development',
  tracesSampleRate: Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE) || 0.0,
  integrations: [Sentry.browserTracingIntegration()],
})

// eslint-disable-next-line react-refresh/only-export-components
function AppWithNavigate() {
  const navigate = useNavigate()
  setNavigateCallback(navigate)
  return <App />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AppWithNavigate />
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
