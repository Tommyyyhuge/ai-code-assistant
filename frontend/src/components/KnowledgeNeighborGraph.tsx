interface Props {
  node: { id: string; title: string }
  prerequisites: { id: string; title: string; title_slug: string }[]
  nextNodes: { id: string; title: string; title_slug: string }[]
  relatedNodes: { id: string; title: string; title_slug: string }[]
  onNodeClick: (slug: string) => void
}

/**
 * 迷你知识点关系图（D3 占位，先用简洁 HTML 渲染）
 */
export default function KnowledgeNeighborGraph({
  node: _node, prerequisites, nextNodes, relatedNodes, onNodeClick,
}: Props) {
  const allNeighbors = [
    ...prerequisites.map((n) => ({ ...n, type: '前置' })),
    ...nextNodes.map((n) => ({ ...n, type: '后续' })),
    ...relatedNodes.map((n) => ({ ...n, type: '相关' })),
  ]

  if (allNeighbors.length === 0) return null

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <h4 className="text-sm font-medium text-gray-500 mb-3">关系图</h4>
      <div className="flex items-center justify-center gap-4 flex-wrap">
        {allNeighbors.map((n) => (
          <button
            key={n.id}
            onClick={() => onNodeClick(n.title_slug)}
            className={`px-3 py-1.5 rounded-full text-xs border transition-colors
              ${n.type === '前置' ? 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100' :
                n.type === '后续' ? 'border-green-200 bg-green-50 text-green-700 hover:bg-green-100' :
                'border-gray-200 bg-white text-gray-600 hover:bg-gray-100'}`}
            title={`${n.type}知识: ${n.title}`}
          >
            {n.title}
          </button>
        ))}
      </div>
    </div>
  )
}
