import { create } from 'zustand'
import { authApi } from '../services/api'

interface User {
  id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
  elo_rating: number
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authApi.login({ email, password })
      const { access_token, refresh_token } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      const userResponse = await authApi.getMe()
      set({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error: unknown) {
      let message = '登录失败'
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } }
        message = axiosError.response?.data?.detail || message
      } else if (error instanceof Error) {
        message = error.message
      }
      set({ isLoading: false, error: message })
      throw error
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      await authApi.register({ username, email, password })
      // 注册成功后直接登录（原子操作，不调用 login action）
      const loginResponse = await authApi.login({ email, password })
      const { access_token, refresh_token } = loginResponse.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      const userResponse = await authApi.getMe()
      set({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error: unknown) {
      let message = '注册失败'
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } }
        message = axiosError.response?.data?.detail || message
      } else if (error instanceof Error) {
        message = error.message
      }
      set({ isLoading: false, error: message })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false, error: null })
  },

  fetchUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isAuthenticated: false })
      return
    }

    try {
      const response = await authApi.getMe()
      set({
        user: response.data,
        isAuthenticated: true
      })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
    }
  },
}))
