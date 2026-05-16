import { useEffect, useRef, useState } from 'react'
import { useAIChatStore } from '../stores/aiChatStore'
import { api } from '../services/api'

interface Provider {
  id: string; name: string; model: string; is_default: boolean
}

export default function AIChatPage() {
  const {
    conversations, currentId, messages, isStreaming, streamingContent, error,
    fetchConversations, createConversation, selectConversation, sendMessage, deleteConversation,
  } = useAIChatStore()

  const inputRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const [providers, setProviders] = useState<Provider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string>('')

  useEffect(() => {
    fetchConversations()
    api.get('/ai/providers').then((r) => {
      setProviders(r.data)
      const def = r.data.find((p: Provider) => p.is_default)
      if (def) setSelectedProvider(def.id)
    })
  }, [])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, streamingContent])

  const handleSend = () => {
    const val = inputRef.current?.value.trim()
    if (!val || isStreaming) return
    if (inputRef.current) inputRef.current.value = ''
    sendMessage(val)
  }

  const handleNew = async () => {
    await createConversation(undefined, '新对话', selectedProvider || undefined)
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <aside className="w-64 border-r bg-white flex flex-col shrink-0">
        <div className="p-3 border-b space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-sm text-gray-700">AI 对话</span>
            <button onClick={handleNew} className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700">+ 新对话</button>
          </div>
          {providers.length > 0 && (
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="w-full text-xs border rounded px-2 py-1"
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.model})</option>
              ))}
            </select>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 && (
            <p className="p-4 text-sm text-gray-400">暂无对话</p>
          )}
          {conversations.map((c) => (
            <div
              key={c.id}
              className={`flex items-center justify-between px-3 py-2.5 cursor-pointer text-sm border-b border-gray-50
                ${c.id === currentId ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50 text-gray-700'}`}
              onClick={() => selectConversation(c.id)}
            >
              <span className="truncate flex-1">{c.title}</span>
              <button
                onClick={(e) => { e.stopPropagation(); deleteConversation(c.id) }}
                className="text-gray-300 hover:text-red-500 text-xs ml-1 shrink-0"
              >✕</button>
            </div>
          ))}
        </div>
      </aside>

      {/* 右侧聊天区 */}
      <main className="flex-1 flex flex-col bg-gray-50">
        {!currentId ? (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            选择一个对话或创建新对话开始与 AI 交流
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m) => (
                <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] rounded-xl px-4 py-2.5 text-sm leading-relaxed
                    ${m.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-sm'
                      : 'bg-white border text-gray-800 rounded-bl-sm shadow-sm'}`}>
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  </div>
                </div>
              ))}

              {/* 流式输出 */}
              {isStreaming && streamingContent && (
                <div className="flex justify-start">
                  <div className="max-w-[70%] rounded-xl rounded-bl-sm px-4 py-2.5 text-sm bg-white border text-gray-800 shadow-sm">
                    <div className="whitespace-pre-wrap">
                      {streamingContent}
                      <span className="inline-block w-1.5 h-4 bg-blue-500 ml-0.5 animate-pulse align-middle" />
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="flex justify-center">
                  <span className="text-sm text-red-500 bg-red-50 px-3 py-1 rounded">{error}</span>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* 输入框 */}
            <div className="border-t bg-white p-3">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="输入你的问题..."
                  className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                  disabled={isStreaming}
                />
                <button
                  onClick={handleSend}
                  disabled={isStreaming}
                  className="px-5 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {isStreaming ? '...' : '发送'}
                </button>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
