import { create } from 'zustand'
import { api } from '../services/api'

export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
}

export interface AIConversation {
  id: string
  title: string
  problemId: string | null
  knowledgeNodeId: string | null
  promptLevel: number
  messages: AIMessage[]
  createdAt: string
}

interface AIChatState {
  conversations: AIConversation[]
  currentConversation: AIConversation | null
  isStreaming: boolean
  streamingContent: string
  isLoading: boolean
  error: string | null

  fetchConversations: () => Promise<void>
  createConversation: (params: {
    title?: string
    problemId?: string
    knowledgeNodeId?: string
    promptLevel?: number
  }) => Promise<AIConversation>
  sendMessage: (conversationId: string, content: string) => Promise<void>
  fetchMessages: (conversationId: string) => Promise<void>
}

export const useAIChatStore = create<AIChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  isStreaming: false,
  streamingContent: '',
  isLoading: false,
  error: null,

  fetchConversations: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/ai/conversations')
      set({ conversations: response.data, isLoading: false })
    } catch {
      set({ isLoading: false, error: '获取对话列表失败' })
    }
  },

  createConversation: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post('/ai/conversations', params)
      const conv: AIConversation = response.data
      set((s) => ({
        conversations: [conv, ...s.conversations],
        currentConversation: conv,
        isLoading: false,
      }))
      return conv
    } catch {
      set({ isLoading: false, error: '创建对话失败' })
      throw new Error('创建对话失败')
    }
  },

  sendMessage: async (conversationId: string, content: string) => {
    set({ isStreaming: true, streamingContent: '' })
    try {
      const response = await api.post(`/ai/conversations/${conversationId}/messages`, { content })
      const assistantMessage: AIMessage = response.data
      const conv = get().currentConversation
      if (conv && conv.id === conversationId) {
        set({
          currentConversation: {
            ...conv,
            messages: [...conv.messages, assistantMessage],
          },
        })
      }
    } catch {
      set({ error: '发送消息失败' })
    } finally {
      set({ isStreaming: false, streamingContent: '' })
    }
  },

  fetchMessages: async (conversationId: string) => {
    set({ isLoading: true })
    try {
      const response = await api.get(`/ai/conversations/${conversationId}/messages`)
      const conv = get().currentConversation
      if (conv && conv.id === conversationId) {
        set({ currentConversation: { ...conv, messages: response.data } })
      }
    } finally {
      set({ isLoading: false })
    }
  },
}))
