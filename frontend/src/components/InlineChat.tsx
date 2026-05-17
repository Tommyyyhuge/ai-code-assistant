import { useState, useRef, useEffect } from 'react'
import { useAIChatStore } from '../stores/aiChatStore'

interface Props {
  knowledgeNodeId: string
  knowledgeNodeTitle: string
  onClose: () => void
}

export default function InlineChat({ knowledgeNodeId, knowledgeNodeTitle, onClose }: Props) {
  const { messages, isStreaming, streamingContent, createConversation, sendMessage } = useAIChatStore()
  const [_convId, setConvId] = useState<string | null>(null)
  const [ready, setReady] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    (async () => {
      const id = await createConversation(knowledgeNodeId, `${knowledgeNodeTitle} 问答`)
      setConvId(id)
      setReady(true)
    })()
  }, [knowledgeNodeId, knowledgeNodeTitle, createConversation])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, streamingContent])

  const handleSend = () => {
    const val = inputRef.current?.value.trim()
    if (!val || !ready || isStreaming) return
    if (inputRef.current) inputRef.current.value = ''
    sendMessage(val)
  }

  return (
    <div className="border-t mt-6">
      <div className="flex items-center justify-between p-3 bg-blue-50 border-b">
        <span className="text-sm font-medium text-blue-700">
          💬 问 AI — {knowledgeNodeTitle}
        </span>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">✕</button>
      </div>

      <div className="max-h-64 overflow-y-auto p-3 space-y-3 bg-white">
        {messages.length === 0 && ready && (
          <p className="text-sm text-gray-400 text-center py-4">
            你好！有什么关于「{knowledgeNodeTitle}」的问题想问我？
          </p>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm
              ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {m.content}
            </div>
          </div>
        ))}

        {isStreaming && streamingContent && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg px-3 py-2 text-sm bg-gray-100 text-gray-800">
              {streamingContent}
              <span className="inline-block w-1.5 h-4 bg-blue-500 ml-0.5 animate-pulse align-middle" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 p-2 border-t bg-gray-50">
        <input
          ref={inputRef}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="输入问题..."
          className="flex-1 border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          disabled={!ready || isStreaming}
        />
        <button
          onClick={handleSend}
          disabled={!ready || isStreaming}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
        >
          发送
        </button>
      </div>
    </div>
  )
}
