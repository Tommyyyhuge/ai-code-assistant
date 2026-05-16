import { useEffect, useState } from 'react'
import { api } from '../services/api'

interface Provider {
  id: string; name: string; base_url: string; api_key: string; model: string; is_default: boolean
}

export default function AISettingsPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Provider | null>(null)
  const [showForm, setShowForm] = useState(false)

  const fetchProviders = async () => {
    const r = await api.get('/ai/providers')
    setProviders(r.data)
    setLoading(false)
  }

  useEffect(() => { fetchProviders() }, [])

  const handleSave = async (data: { name: string; base_url: string; api_key: string; model: string; is_default: boolean }) => {
    if (editing) {
      await api.put(`/ai/providers/${editing.id}`, data)
    } else {
      await api.post('/ai/providers', data)
    }
    setShowForm(false)
    setEditing(null)
    fetchProviders()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除此配置？')) return
    await api.delete(`/ai/providers/${id}`)
    fetchProviders()
  }

  const handleSetDefault = async (id: string) => {
    const p = providers.find((x) => x.id === id)
    if (!p) return
    await api.put(`/ai/providers/${id}`, { is_default: true, name: p.name, base_url: p.base_url, api_key: p.api_key, model: p.model })
    fetchProviders()
  }

  if (loading) return <div className="p-8 text-gray-400">加载中...</div>

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI 模型设置</h1>
          <p className="text-sm text-gray-500 mt-1">配置自己的 API 接入，支持 OpenAI 兼容接口</p>
        </div>
        <button
          onClick={() => { setEditing(null); setShowForm(true) }}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
        >
          + 添加配置
        </button>
      </div>

      {providers.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg mb-2">暂无配置</p>
          <p className="text-sm">点击「添加配置」接入你的 AI 模型</p>
        </div>
      )}

      <div className="space-y-3">
        {providers.map((p) => (
          <div key={p.id} className={`border rounded-xl p-5 ${p.is_default ? 'border-blue-300 bg-blue-50/30' : 'border-gray-200'}`}>
            <div className="flex items-start justify-between mb-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{p.name}</span>
                  {p.is_default && (
                    <span className="text-xs bg-blue-600 text-white px-1.5 py-0.5 rounded">默认</span>
                  )}
                </div>
                <div className="text-sm text-gray-500 mt-0.5">{p.base_url}</div>
              </div>
              <div className="flex gap-2">
                {!p.is_default && (
                  <button onClick={() => handleSetDefault(p.id)} className="text-xs text-blue-600 hover:underline">设为默认</button>
                )}
                <button onClick={() => { setEditing(p); setShowForm(true) }} className="text-xs text-gray-500 hover:underline">编辑</button>
                <button onClick={() => handleDelete(p.id)} className="text-xs text-red-500 hover:underline">删除</button>
              </div>
            </div>
            <div className="flex gap-4 text-sm text-gray-500">
              <span>模型: <code className="bg-gray-100 px-1 rounded">{p.model}</code></span>
              <span>密钥: <code className="bg-gray-100 px-1 rounded">{p.api_key}</code></span>
            </div>
          </div>
        ))}
      </div>

      {/* 表单弹窗 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="text-lg font-semibold mb-4">{editing ? '编辑配置' : '添加配置'}</h2>
            <ProviderForm
              initial={editing ? { name: editing.name, base_url: editing.base_url, api_key: '', model: editing.model, is_default: editing.is_default } : undefined}
              onSave={handleSave}
              onCancel={() => { setShowForm(false); setEditing(null) }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function ProviderForm({
  initial, onSave, onCancel,
}: {
  initial?: { name: string; base_url: string; api_key: string; model: string; is_default: boolean }
  onSave: (d: { name: string; base_url: string; api_key: string; model: string; is_default: boolean }) => void
  onCancel: () => void
}) {
  const [name, setName] = useState(initial?.name || '')
  const [baseUrl, setBaseUrl] = useState(initial?.base_url || '')
  const [apiKey, setApiKey] = useState(initial?.api_key || '')
  const [model, setModel] = useState(initial?.model || '')
  const [isDefault, setIsDefault] = useState(initial?.is_default || false)

  const handleSubmit = () => {
    if (!name || !baseUrl || !apiKey || !model) {
      alert('所有字段必填')
      return
    }
    onSave({ name, base_url: baseUrl, api_key: apiKey, model, is_default: isDefault })
  }

  return (
    <div className="space-y-3">
      <input placeholder="配置名称" value={name} onChange={(e) => setName(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
      <input placeholder="API 地址 (如 https://api.deepseek.com/v1)" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
      <input placeholder="API Key" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
      <input placeholder="模型名 (如 deepseek-chat)" value={model} onChange={(e) => setModel(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={isDefault} onChange={(e) => setIsDefault(e.target.checked)} />
        设为默认
      </label>
      <div className="flex gap-2 pt-2">
        <button onClick={handleSubmit} className="flex-1 bg-blue-600 text-white py-2 rounded text-sm">保存</button>
        <button onClick={onCancel} className="flex-1 border py-2 rounded text-sm">取消</button>
      </div>
    </div>
  )
}
