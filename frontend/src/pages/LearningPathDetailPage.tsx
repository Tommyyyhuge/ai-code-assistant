import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'

interface PathDetail {
  path: {
    id: string
    title: string
    title_slug: string
    description: string | null
    node_count: number
    user_status: string
    user_progress_pct: number
  }
  nodes: {
    id: string
    knowledge_node_id: string
    title: string
    title_slug: string
    level: number
    order_index: number
    is_required: boolean
    user_status: string
  }[]
}

const statusConfig: Record<string, { icon: string; label: string; rowClass: string }> = {
  not_started: { icon: '○', label: '未开始', rowClass: 'border-gray-200' },
  in_progress: { icon: '◐', label: '学习中', rowClass: 'border-yellow-200 bg-yellow-50/30' },
  completed: { icon: '●', label: '已完成', rowClass: 'border-green-200 bg-green-50/30' },
}

function LevelBadge({ level }: { level: number }) {
  const colors = ['bg-green-100 text-green-700', 'bg-lime-100 text-lime-700', 'bg-yellow-100 text-yellow-700', 'bg-orange-100 text-orange-700', 'bg-red-100 text-red-700']
  return (
    <span className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${colors[Math.min(level - 1, 4)]}`}>
      L{level}
    </span>
  )
}

export default function LearningPathDetailPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [detail, setDetail] = useState<PathDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return
    api.get(`/paths/${slug}`)
      .then((r) => setDetail(r.data))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="animate-pulse space-y-3">
        <div className="h-8 bg-gray-200 rounded w-64" />
        <div className="h-4 bg-gray-100 rounded w-96" />
        <div className="h-3 bg-gray-100 rounded-full" />
        {[1,2,3,4,5].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg" />
        ))}
      </div>
    </div>
  )

  if (!detail) return (
    <div className="p-8 max-w-3xl mx-auto text-center">
      <p className="text-gray-400 text-lg">路线未找到</p>
      <button onClick={() => navigate('/paths')} className="mt-4 text-blue-600 hover:underline text-sm">返回路线列表</button>
    </div>
  )

  const { path, nodes } = detail
  const completed = nodes.filter((n) => n.user_status === 'completed').length

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {/* 面包屑 */}
      <button onClick={() => navigate('/paths')} className="text-sm text-gray-400 hover:text-blue-600 mb-4 inline-block">
        ← 返回路线列表
      </button>

      {/* 标题区 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{path.title}</h1>
        {path.description && <p className="text-gray-500 text-sm leading-relaxed">{path.description}</p>}
      </div>

      {/* 进度条 */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            学习进度
          </span>
          <span className="text-sm text-gray-500">
            <span className="font-semibold text-green-600">{completed}</span>
            <span className="text-gray-400"> / {path.node_count}</span>
            <span className="ml-2 font-medium">{path.user_progress_pct}%</span>
          </span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2.5">
          <div
            className="bg-gradient-to-r from-green-400 to-green-500 h-2.5 rounded-full transition-all duration-700"
            style={{ width: `${Math.max(path.user_progress_pct, 2)}%` }}
          />
        </div>
      </div>

      {/* 节点列表 */}
      <div className="space-y-2">
        {nodes.map((node) => {
          const cfg = (statusConfig[node.user_status] ?? statusConfig.not_started)!
          return (
            <div
              key={node.id}
              className={`flex items-center gap-4 border rounded-lg p-4 transition-colors ${cfg.rowClass}`}
            >
              {/* 序号 */}
              <span className="text-xs text-gray-400 w-6 text-right font-mono shrink-0">
                {node.order_index}
              </span>

              {/* 状态图标 */}
              <span className="text-lg w-6 text-center shrink-0" title={cfg.label}>
                {cfg.icon}
              </span>

              {/* 标题 + 标签 */}
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-800 truncate">{node.title}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <LevelBadge level={node.level} />
                  {node.is_required ? (
                    <span className="text-xs text-blue-500">必学</span>
                  ) : (
                    <span className="text-xs text-gray-400">选学</span>
                  )}
                  <span className="text-xs text-gray-400">{cfg.label}</span>
                </div>
              </div>

              {/* 操作按钮 */}
              <button
                onClick={() => navigate(`/knowledge/${node.title_slug}`)}
                className="shrink-0 px-4 py-1.5 text-sm font-medium border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
              >
                去学习
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
