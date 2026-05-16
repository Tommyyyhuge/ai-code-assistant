import { create } from 'zustand'
import { api } from '../services/api'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

interface ConversationBrief {
  id: string; title: string; knowledge_node_id: string | null
  created_at: string; updated_at: string
}

interface MessageItem {
  id: string; role: 'user' | 'assistant' | 'system'; content: string; created_at: string
}

interface AIChatState {
  conversations: ConversationBrief[]
  currentId: string | null
  messages: MessageItem[]
  isStreaming: boolean
  streamingContent: string
  error: string | null

  fetchConversations: () => Promise<void>
  createConversation: (knowledgeNodeId?: string, title?: string, providerId?: string) => Promise<string>
  fetchMessages: (id: string) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  deleteConversation: (id: string) => Promise<void>
  selectConversation: (id: string) => Promise<void>
}

export const useAIChatStore = create<AIChatState>((set, get) => ({
  conversations: [],
  currentId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  error: null,

  fetchConversations: async () => {
    try {
      const r = await api.get('/ai/conversations')
      set({ conversations: r.data })
    } catch { /* ignore */ }
  },

  createConversation: async (knowledgeNodeId, title, providerId) => {
    const body: Record<string, unknown> = { knowledge_node_id: knowledgeNodeId, title }
    if (providerId) body.provider_id = providerId
    const r = await api.post('/ai/conversations', body)
    const id = r.data.id
    set({ currentId: id, messages: [] })
    await get().fetchConversations()
    return id
  },

  fetchMessages: async (id: string) => {
    try {
      const r = await api.get(`/ai/conversations/${id}/messages`)
      set({ messages: r.data, currentId: id })
    } catch { /* ignore */ }
  },

  selectConversation: async (id: string) => {
    set({ currentId: id, error: null })
    await get().fetchMessages(id)
  },

  sendMessage: async (content: string) => {
    const { currentId } = get()
    if (!currentId) return

    const userMsg: MessageItem = {
      id: Date.now().toString(), role: 'user', content, created_at: new Date().toISOString(),
    }
    set((s) => ({ messages: [...s.messages, userMsg], isStreaming: true, streamingContent: '', error: null }))

    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch(`${API_BASE}/ai/conversations/${currentId}/stream?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      })

      if (!response.ok) throw new Error('Stream failed')

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader')

      const decoder = new TextDecoder()
      let fullContent = ''
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullContent += parsed.content
                set({ streamingContent: fullContent })
              }
            } catch { /* skip */ }
          }
        }
      }

      if (fullContent) {
        const assistantMsg: MessageItem = {
          id: Date.now().toString(), role: 'assistant', content: fullContent, created_at: new Date().toISOString(),
        }
        set((s) => ({ messages: [...s.messages, assistantMsg], isStreaming: false, streamingContent: '' }))
      } else {
        set({ isStreaming: false, streamingContent: '' })
      }

      get().fetchConversations()
    } catch {
      set({ isStreaming: false, error: 'AI 服务暂不可用' })
    }
  },

  deleteConversation: async (id: string) => {
    try {
      await api.delete(`/ai/conversations/${id}`)
      set((s) => ({
        conversations: s.conversations.filter((c) => c.id !== id),
        currentId: s.currentId === id ? null : s.currentId,
        messages: s.currentId === id ? [] : s.messages,
      }))
    } catch { /* ignore */ }
  },
}))

export type { ConversationBrief, MessageItem }
