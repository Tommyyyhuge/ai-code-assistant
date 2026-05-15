import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useNavigate, Link } from 'react-router-dom'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState('')
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError('')
    
    try {
      await login(email, password)
      navigate('/')
    } catch (err: unknown) {
      let message = '登录失败'
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } }
        message = axiosError.response?.data?.detail || message
      } else if (err instanceof Error) {
        message = err.message
      }
      setLocalError(message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {localError && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded">
          {localError}
        </div>
      )}
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          邮箱
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          密码
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? '登录中...' : '登录'}
      </button>
        <p className="mt-4 text-center text-sm text-gray-600">
          还没有账号？{' '}
          <Link to="/register" className="text-blue-600 hover:underline">
            去注册
          </Link>
        </p>
    </form>
  )
}