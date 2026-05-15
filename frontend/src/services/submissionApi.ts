import { api } from './api'
import type { Submission, SubmissionCreate } from '../types/submission'

/**
 * 提交 API（使用共享 axios 实例，自动携带 Token 和 401 处理）
 */
export const submissionApi = {
  submit: async (data: SubmissionCreate): Promise<Submission> => {
    const response = await api.post('/submissions/', data)
    return response.data
  },

  getSubmission: async (id: string): Promise<Submission> => {
    const response = await api.get(`/submissions/${id}`)
    return response.data
  },

  listSubmissions: async (params?: { problem_id?: string; status?: string }): Promise<Submission[]> => {
    const response = await api.get('/submissions/', { params })
    return response.data
  },
}
