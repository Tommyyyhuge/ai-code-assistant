import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'

interface PathBrief {
  id: string
  title: string
  title_slug: string
  category: string
  description: string | null
  estimated_days: number | null
  node_count: number
  user_status: string
  user_progress_pct: number
}

const categoryLabels: Record<string, string> = {
  oi_junior: 'OI 入门',
  oi_senior: 'OI 提高',
  lanqiao: '蓝桥杯',
  self_study: '零基础自学',
  acm: 'ACM-ICPC',
}

const categoryColors: Record<string, string> = {
  oi_junior: 'bg-green-100 text-green-700',
  oi_senior: 'bg-purple-100 text-purple-700',
  lanqiao: 'bg-blue-100 text-blue-700',
  self_study: 'bg-orange-100 text-orange-700',
  acm: 'bg-red-100 text-red-700',
}

export default function LearningPathListPage() {
  const navigate = useNavigate()
  const [paths, setPaths] = useState<PathBrief[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/paths').then((r) => setPaths(r.data)).finally(() => setLoading(false))
  }, [])

  const handleEnroll = async (slug: string) => {
    try {
      await api.post(`/paths/${slug}/enroll`)
      const r = await api.get('/paths')
      setPaths(r.data)
    } catch {
      // 忽略
    }
  }

  if (loading) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-32" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {[1,2,3].map((i) => (
              <div key={i} className="h-48 bg-gray-100 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">学习路径</h1>
        <p className="text-sm text-gray-500 mt-1">选择一条路线，系统按推荐顺序引导学习</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {paths.map((p) => (
          <div
            key={p.id}
            className="flex flex-col border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-sm transition-all bg-white"
          >
            {/* 分类标签 */}
            <div className="mb-3">
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${categoryColors[p.category] || 'bg-gray-100 text-gray-600'}`}>
                {categoryLabels[p.category] || p.category}
              </span>
            </div>

            {/* 标题 */}
            <h2 className="text-base font-semibold text-gray-900 mb-2 leading-snug">{p.title}</h2>

            {/* 描述 */}
            {p.description ? (
              <p className="text-sm text-gray-500 mb-3 line-clamp-2 leading-relaxed">{p.description}</p>
            ) : (
              <div className="mb-3" />
            )}

            {/* 统计 */}
            <div className="flex items-center gap-3 text-xs text-gray-400 mb-4">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                {p.node_count} 个知识点
              </span>
              {p.estimated_days && (
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-300" />
                  约 {p.estimated_days} 天
                </span>
              )}
            </div>

            {/* 进度条 */}
            {p.user_status !== 'not_started' && (
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>完成进度</span>
                  <span className="font-medium">{p.user_progress_pct}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-green-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${p.user_progress_pct}%` }}
                  />
                </div>
              </div>
            )}

            {/* 按钮 — mt-auto 推到底部 */}
            <div className="mt-auto flex gap-2">
              <button
                onClick={() => navigate(`/paths/${p.title_slug}`)}
                className="flex-1 px-4 py-2 text-sm font-medium border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {p.user_status !== 'not_started' ? '继续学习' : '查看路线'}
              </button>
              {p.user_status === 'not_started' && (
                <button
                  onClick={() => handleEnroll(p.title_slug)}
                  className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  加入
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
