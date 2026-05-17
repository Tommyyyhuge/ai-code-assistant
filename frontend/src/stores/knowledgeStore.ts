import { create } from 'zustand'
import { api } from '../services/api'

export interface KnowledgeNodeTreeItem {
  id: string
  title: string
  title_slug: string
  category: string
  level: number
  order_index: number
  user_status: string
  children: KnowledgeNodeTreeItem[]
}

export interface KnowledgeNodeDetail {
  node: {
    id: string
    title: string
    title_slug: string
    category: string
    level: number
    description: string
    core_concept: string
    applicable_scenarios: string | null
    algorithm_steps: string | null
    code_template_cpp: string | null
    code_template_py: string | null
    code_template_java: string | null
    time_complexity: string | null
    space_complexity: string | null
    common_mistakes: string | null
    estimated_minutes: number | null
  }
  prerequisites: { id: string; title: string; title_slug: string }[]
  next_nodes: { id: string; title: string; title_slug: string }[]
  related_nodes: { id: string; title: string; title_slug: string }[]
  problems: {
    problem_id: string; title: string; title_slug: string
    difficulty: number; difficulty_level: number; is_required: boolean
  }[]
  user_progress: { status: string; practice_count: number } | null
}

interface KnowledgeState {
  tree: KnowledgeNodeTreeItem[]
  currentNode: KnowledgeNodeDetail | null
  isLoading: boolean
  error: string | null

  fetchTree: (category?: string) => Promise<void>
  fetchNode: (slug: string) => Promise<void>
  updateProgress: (nodeId: string, status: string) => Promise<void>
  clearError: () => void
}

export const useKnowledgeStore = create<KnowledgeState>((set) => ({
  tree: [],
  currentNode: null,
  isLoading: false,
  error: null,

  fetchTree: async (category?: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/knowledge/tree', { params: { category } })
      set({ tree: response.data.children, isLoading: false })
    } catch {
      set({ isLoading: false, error: '获取知识树失败' })
    }
  },

  fetchNode: async (slug: string) => {
    set({ isLoading: true, error: null, currentNode: null })
    try {
      const response = await api.get(`/knowledge/nodes/${slug}`)
      set({ currentNode: response.data, isLoading: false })
    } catch {
      set({ isLoading: false, error: '获取知识点失败' })
    }
  },

  updateProgress: async (nodeId: string, status: string) => {
    try {
      await api.post('/knowledge/progress', { knowledge_node_id: nodeId, status })
    } catch {
      // 静默失败，不自增 error
    }
  },

  clearError: () => set({ error: null }),
}))
