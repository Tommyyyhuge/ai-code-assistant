import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h2>出错了</h2>
            <p style={{ color: '#666' }}>
              {this.state.error?.message || '发生了未知错误'}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: '1rem', padding: '0.5rem 1rem', background: '#2563eb',
                color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer'
              }}
            >
              刷新页面
            </button>
          </div>
        )
      )
    }
    return this.props.children
  }
}
