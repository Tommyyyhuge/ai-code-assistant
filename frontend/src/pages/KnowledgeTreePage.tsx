import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useKnowledgeStore } from '../stores/knowledgeStore'
import { useAuthStore } from '../stores/authStore'
import KnowledgeTree from '../components/KnowledgeTree'
import KnowledgeNeighborGraph from '../components/KnowledgeNeighborGraph'

type Tab = 'lecture' | 'problems' | 'related'

export default function KnowledgeTreePage() {
  const { '*': slugParam } = useParams()
  const navigate = useNavigate()
  const { tree, currentNode, isLoading, error, fetchTree, fetchNode, updateProgress } = useKnowledgeStore()
  const { isAuthenticated } = useAuthStore()
  const [tab, setTab] = useState<Tab>('lecture')
  const [codeLang, setCodeLang] = useState<'cpp' | 'py' | 'java'>('cpp')

  useEffect(() => { fetchTree() }, [fetchTree])

  const selectedSlug = slugParam || null

  useEffect(() => {
    if (selectedSlug) fetchNode(selectedSlug)
  }, [selectedSlug, fetchNode])

  const handleSelect = (slug: string) => {
    navigate(`/knowledge/${slug}`)
  }

  const handleMarkComplete = async () => {
    if (!currentNode || !isAuthenticated) return
    const nodeId = currentNode.node.id
    await updateProgress(nodeId, 'completed')
    fetchTree() // 刷新树的状态图标
    fetchNode(currentNode.node.title_slug) // 刷新详情
  }

  const handleMarkInProgress = async () => {
    if (!currentNode || !isAuthenticated) return
    await updateProgress(currentNode.node.id, 'in_progress')
    fetchTree()
    fetchNode(currentNode.node.title_slug)
  }

  const codeTemplate = currentNode?.node?.[
    `code_template_${codeLang}` as keyof typeof currentNode.node
  ] as string | null

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* 左侧知识树 */}
      <aside className="w-72 border-r overflow-y-auto bg-white shrink-0">
        <div className="p-3 border-b font-semibold text-gray-700">知识图谱</div>
        {tree.length === 0 && !isLoading && (
          <p className="p-4 text-sm text-gray-400">暂无知识点</p>
        )}
        <KnowledgeTree items={tree} selectedSlug={selectedSlug} onSelect={handleSelect} />
        {isLoading && <p className="p-4 text-sm text-gray-400">加载中...</p>}
      </aside>

      {/* 右侧详情 */}
      <main className="flex-1 overflow-y-auto p-6">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>
        )}

        {!selectedSlug && !currentNode && (
          <div className="flex items-center justify-center h-full text-gray-400">
            选择一个知识点开始学习
          </div>
        )}

        {isLoading && !currentNode && (
          <div className="text-gray-400">加载中...</div>
        )}

        {currentNode && (
          <div>
            {/* 标题区 */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{currentNode.node.title}</h1>
                <div className="flex gap-2 mt-1 text-sm text-gray-500">
                  <span>{currentNode.node.category}</span>
                  <span>·</span>
                  <span>难度 {currentNode.node.level}/5</span>
                  {currentNode.node.estimated_minutes && (
                    <>
                      <span>·</span>
                      <span>约 {currentNode.node.estimated_minutes} 分钟</span>
                    </>
                  )}
                </div>
              </div>
              {isAuthenticated && (
                <div className="flex gap-2">
                  <button
                    onClick={handleMarkInProgress}
                    className="px-3 py-1.5 text-sm border rounded hover:bg-yellow-50"
                  >
                    标记学习中
                  </button>
                  <button
                    onClick={handleMarkComplete}
                    className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    标记完成
                  </button>
                </div>
              )}
            </div>

            {/* 用户进度 */}
            {currentNode.user_progress && (
              <div className="mb-4 text-sm text-gray-500">
                状态: {currentNode.user_progress.status === 'completed' ? '✅ 已完成' :
                        currentNode.user_progress.status === 'in_progress' ? '📖 学习中' : '○ 未开始'}
                {' · '}练习 {currentNode.user_progress.practice_count} 次
              </div>
            )}

            {/* Tab 切换 */}
            <div className="flex gap-0 border-b mb-4">
              {(['lecture', 'problems', 'related'] as Tab[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`px-4 py-2 text-sm border-b-2 transition-colors ${
                    tab === t
                      ? 'border-blue-600 text-blue-600 font-medium'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {t === 'lecture' ? '讲解' : t === 'problems' ? '题集' : '关联知识'}
                </button>
              ))}
            </div>

            {/* Tab: 讲解 */}
            {tab === 'lecture' && (
              <div className="prose max-w-none space-y-4">
                <section>
                  <h3 className="text-lg font-semibold">概念定义</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{currentNode.node.description}</p>
                </section>

                <section>
                  <h3 className="text-lg font-semibold">核心思想</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{currentNode.node.core_concept}</p>
                </section>

                {currentNode.node.algorithm_steps && (
                  <section>
                    <h3 className="text-lg font-semibold">算法步骤</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{currentNode.node.algorithm_steps}</p>
                  </section>
                )}

                {currentNode.node.applicable_scenarios && (
                  <section>
                    <h3 className="text-lg font-semibold">适用场景</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{currentNode.node.applicable_scenarios}</p>
                  </section>
                )}

                {/* 代码模板 */}
                <section>
                  <h3 className="text-lg font-semibold">代码模板</h3>
                  <div className="flex gap-2 mb-2">
                    {(['cpp', 'py', 'java'] as const).map((l) => (
                      <button
                        key={l}
                        onClick={() => setCodeLang(l)}
                        className={`px-2 py-1 text-xs rounded ${
                          codeLang === l ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {l === 'cpp' ? 'C++' : l === 'py' ? 'Python' : 'Java'}
                      </button>
                    ))}
                  </div>
                  {codeTemplate ? (
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
                      <code>{codeTemplate}</code>
                    </pre>
                  ) : (
                    <p className="text-sm text-gray-400">暂无 {codeLang === 'cpp' ? 'C++' : codeLang === 'py' ? 'Python' : 'Java'} 代码模板</p>
                  )}
                </section>

                {(currentNode.node.time_complexity || currentNode.node.space_complexity) && (
                  <section className="flex gap-6">
                    {currentNode.node.time_complexity && (
                      <div>
                        <span className="text-sm text-gray-500">时间复杂度: </span>
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">
                          {currentNode.node.time_complexity}
                        </code>
                      </div>
                    )}
                    {currentNode.node.space_complexity && (
                      <div>
                        <span className="text-sm text-gray-500">空间复杂度: </span>
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">
                          {currentNode.node.space_complexity}
                        </code>
                      </div>
                    )}
                  </section>
                )}

                {currentNode.node.common_mistakes && (
                  <section>
                    <h3 className="text-lg font-semibold text-red-700">⚠️ 常见错误</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{currentNode.node.common_mistakes}</p>
                  </section>
                )}
              </div>
            )}

            {/* Tab: 题集 */}
            {tab === 'problems' && (
              <div>
                {currentNode.problems.length === 0 ? (
                  <p className="text-gray-400 text-sm">暂无关联题目</p>
                ) : (
                  <div className="grid gap-3">
                    {currentNode.problems.map((p) => (
                      <a
                        key={p.problem_id}
                        href={`/problems/${p.problem_id}`}
                        className="block border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-blue-700">{p.title}</span>
                          <div className="flex gap-2 items-center">
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              p.difficulty_level === 1 ? 'bg-green-100 text-green-700' :
                              p.difficulty_level === 2 ? 'bg-yellow-100 text-yellow-700' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {p.difficulty_level === 1 ? '入门' : p.difficulty_level === 2 ? '进阶' : '挑战'}
                            </span>
                            {p.is_required && (
                              <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">必做</span>
                            )}
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab: 关联知识 */}
            {tab === 'related' && (
              <div className="space-y-6">
                {/* 邻居链接 */}
                <div className="flex flex-wrap gap-4 text-sm">
                  {currentNode.prerequisites.length > 0 && (
                    <div>
                      <span className="text-gray-400">前置知识: </span>
                      {currentNode.prerequisites.map((n) => (
                        <button
                          key={n.id}
                          onClick={() => handleSelect(n.title_slug)}
                          className="text-blue-600 hover:underline mr-2"
                        >
                          {n.title}
                        </button>
                      ))}
                    </div>
                  )}
                  {currentNode.next_nodes.length > 0 && (
                    <div>
                      <span className="text-gray-400">后续知识: </span>
                      {currentNode.next_nodes.map((n) => (
                        <button
                          key={n.id}
                          onClick={() => handleSelect(n.title_slug)}
                          className="text-blue-600 hover:underline mr-2"
                        >
                          {n.title}
                        </button>
                      ))}
                    </div>
                  )}
                  {currentNode.related_nodes.length > 0 && (
                    <div>
                      <span className="text-gray-400">相关知识: </span>
                      {currentNode.related_nodes.map((n) => (
                        <button
                          key={n.id}
                          onClick={() => handleSelect(n.title_slug)}
                          className="text-blue-600 hover:underline mr-2"
                        >
                          {n.title}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* 迷你关系图 */}
                <KnowledgeNeighborGraph
                  node={currentNode.node}
                  prerequisites={currentNode.prerequisites}
                  nextNodes={currentNode.next_nodes}
                  relatedNodes={currentNode.related_nodes}
                  onNodeClick={handleSelect}
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
