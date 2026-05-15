import { create } from 'zustand'
import { problemApi, tagApi } from '../services/api'
import type { ProblemListItem, ProblemDetail, TagBrief } from '../types/problem'

interface ProblemFilters {
  search?: string
  difficultyMin?: number
  difficultyMax?: number
  sourceOj?: string
  tagIds?: string[]
}

interface ProblemState {
  // 列表状态
  problems: ProblemListItem[]
  total: number
  page: number
  pageSize: number
  isLoading: boolean
  listError: string | null
  
  // 详情状态
  currentProblem: ProblemDetail | null
  isDetailLoading: boolean
  detailError: string | null
  
  // 标签
  tags: TagBrief[]
  isTagsLoading: boolean
  
  // 筛选条件
  filters: ProblemFilters
  
  // Actions
  fetchProblems: (page?: number, pageSize?: number) => Promise<void>
  fetchProblemDetail: (id: string) => Promise<void>
  fetchTags: () => Promise<void>
  setFilters: (filters: Partial<ProblemFilters>) => void
  resetFilters: () => void
}

export const useProblemStore = create<ProblemState>((set, get) => ({
  // 初始状态
  problems: [],
  total: 0,
  page: 1,
  pageSize: 20,
  isLoading: false,
  listError: null,
  
  currentProblem: null,
  isDetailLoading: false,
  detailError: null,
  
  tags: [],
  isTagsLoading: false,
  
  filters: {},
  
  // 获取题目列表
  fetchProblems: async (page = 1, pageSize = 20) => {
    set({ isLoading: true, listError: null })
    try {
      const { filters } = get()
      const response = await problemApi.getProblems({
        page,
        page_size: pageSize,
        search: filters.search,
        difficulty_min: filters.difficultyMin,
        difficulty_max: filters.difficultyMax,
        source_oj: filters.sourceOj,
        tag_ids: filters.tagIds,
      })
      
      const { items, total } = response.data
      set({
        problems: items,
        total,
        page,
        pageSize,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        isLoading: false,
        listError: error.response?.data?.detail || '获取题目列表失败',
      })
    }
  },
  
  // 获取题目详情
  fetchProblemDetail: async (id: string) => {
    set({ isDetailLoading: true, detailError: null })
    try {
      const response = await problemApi.getProblem(id)
      set({
        currentProblem: response.data,
        isDetailLoading: false,
      })
    } catch (error: any) {
      set({
        isDetailLoading: false,
        detailError: error.response?.data?.detail || '获取题目详情失败',
      })
    }
  },
  
  // 获取标签列表
  fetchTags: async () => {
    set({ isTagsLoading: true })
    try {
      const response = await tagApi.getTags()
      set({ tags: response.data, isTagsLoading: false })
    } catch (error) {
      set({ isTagsLoading: false })
    }
  },
  
  // 设置筛选条件
  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }))
  },
  
  // 重置筛选条件
  resetFilters: () => {
    set({ filters: {}, page: 1 })
  },
}))
