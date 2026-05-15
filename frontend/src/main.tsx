import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, useNavigate } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import ErrorBoundary from './components/ErrorBoundary.tsx'
import { setNavigateCallback } from './services/api.ts'

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
