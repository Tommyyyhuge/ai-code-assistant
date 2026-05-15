import { create } from 'zustand'
import { api } from '../services/api'
import type { Submission, SubmissionCreate } from '../types/submission'

interface SubmissionState {
  // 列表
  submissions: Submission[]
  isLoading: boolean
  error: string | null

  // 当前详情
  currentSubmission: Submission | null
  isDetailLoading: boolean

  // 轮询状态
  pollingId: string | null

  // Actions
  submitCode: (data: SubmissionCreate) => Promise<Submission>
  fetchSubmission: (id: string) => Promise<void>
  fetchSubmissions: (problemId?: string) => Promise<void>
  clearError: () => void
}

export const useSubmissionStore = create<SubmissionState>((set) => ({
  submissions: [],
  isLoading: false,
  error: null,

  currentSubmission: null,
  isDetailLoading: false,

  pollingId: null,

  submitCode: async (data: SubmissionCreate) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post('/submissions/', data)
      const submission: Submission = response.data
      set((s) => ({
        submissions: [submission, ...s.submissions],
        currentSubmission: submission,
        isLoading: false,
      }))
      return submission
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '提交失败'
          : '提交失败'
      set({ isLoading: false, error: msg })
      throw err
    }
  },

  fetchSubmission: async (id: string) => {
    set({ isDetailLoading: true })
    try {
      const response = await api.get(`/submissions/${id}`)
      set({ currentSubmission: response.data, isDetailLoading: false })
    } catch (err: unknown) {
      set({ isDetailLoading: false })
    }
  },

  fetchSubmissions: async (problemId?: string) => {
    set({ isLoading: true, error: null })
    try {
      const params: Record<string, string> = {}
      if (problemId) params.problem_id = problemId
      const response = await api.get('/submissions/', { params })
      set({ submissions: response.data, isLoading: false })
    } catch (err: unknown) {
      set({ isLoading: false, error: '获取提交记录失败' })
    }
  },

  clearError: () => set({ error: null }),
}))
