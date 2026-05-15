import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 全局 navigate 回调（由 main.tsx 注入）
let navigateCallback: ((path: string) => void) | null = null

export const setNavigateCallback = (cb: (path: string) => void) => {
  navigateCallback = cb
}

// 响应拦截器 - 处理 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      // 优先使用 React Router navigate，避免页面重载
      if (navigateCallback) {
        navigateCallback('/login')
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  getMe: () =>
    api.get('/auth/me'),
}

// 题目 API
export const problemApi = {
  getProblems: (params?: {
    search?: string
    difficulty_min?: number
    difficulty_max?: number
    source_oj?: string
    tag_ids?: string[]
    page?: number
    page_size?: number
  }) => api.get('/problems', { params }),
  
  getProblem: (id: string) => api.get(`/problems/${id}`),
}

// 标签 API
export const tagApi = {
  getTags: (category?: string) => 
    api.get('/tags', { params: { category } }),
}