import { useEffect } from 'react'
import { useKnowledgeStore } from '../stores/knowledgeStore'
import { useNavigate } from 'react-router-dom'

export default function KnowledgeGraphPage() {
  const { tree, fetchTree, isLoading } = useKnowledgeStore()
  const navigate = useNavigate()

  useEffect(() => { fetchTree() }, [fetchTree])

  const allNodes = flattenTree(tree)

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">知识图谱全图</h1>
      {isLoading ? (
        <p className="text-gray-400">加载中...</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {allNodes.map((n) => (
            <button
              key={n.id}
              onClick={() => navigate(`/knowledge/${n.title_slug}`)}
              className="text-left border rounded-lg p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium text-sm text-blue-700">{n.title}</div>
              <div className="text-xs text-gray-400 mt-1">
                {n.category} · L{n.level}
                {n.user_status !== 'not_started' && (
                  <span className="ml-2">
                    {n.user_status === 'completed' ? '✅' : '📖'}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function flattenTree(items: import('../stores/knowledgeStore').KnowledgeNodeTreeItem[]): import('../stores/knowledgeStore').KnowledgeNodeTreeItem[] {
  const result: import('../stores/knowledgeStore').KnowledgeNodeTreeItem[] = []
  for (const item of items) {
    result.push(item)
    result.push(...flattenTree(item.children))
  }
  return result
}
