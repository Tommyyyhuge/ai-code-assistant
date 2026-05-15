import { useEffect } from 'react'
import { useProblemStore } from '../stores/problemStore'
import ProblemCard from '../components/ProblemCard'
import ProblemFilter from '../components/ProblemFilter'
import { BookOpen, Loader2 } from 'lucide-react'

export default function ProblemListPage() {
  const { 
    problems, 
    total, 
    page, 
    pageSize, 
    isLoading, 
    listError,
    tags,
    filters,
    fetchProblems,
    fetchTags,
    setFilters,
  } = useProblemStore()

  // 初始加载
  useEffect(() => {
    fetchProblems(1, pageSize)
    fetchTags()
  }, [])

  // 应用筛选
  const handleApplyFilter = () => {
    fetchProblems(1, pageSize)
  }

  // 分页
  const handlePageChange = (newPage: number) => {
    fetchProblems(newPage, pageSize)
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-7 h-7 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">题目列表</h1>
        </div>
        <p className="text-gray-600">
          共 {total} 道题目
        </p>
      </div>

      <ProblemFilter 
        filter={{
          search: filters.search || '',
          difficultyMin: filters.difficultyMin || 1,
          difficultyMax: filters.difficultyMax || 10,
          tagIds: filters.tagIds || [],
        }}
        tags={tags}
        onChange={(newFilter) => setFilters({
          search: newFilter.search,
          difficultyMin: newFilter.difficultyMin,
          difficultyMax: newFilter.difficultyMax,
          tagIds: newFilter.tagIds,
        })}
        onApply={handleApplyFilter}
      />

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : listError ? (
        <div className="text-center py-12 text-red-600">
          <p>{listError}</p>
          <button 
            onClick={() => fetchProblems(page, pageSize)}
            className="mt-2 text-blue-600 hover:underline"
          >
            重试
          </button>
        </div>
      ) : (
        <>
          <div className="grid gap-4">
            {problems.map(problem => (
              <ProblemCard key={problem.id} problem={problem} />
            ))}
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                className="px-3 py-1 border rounded-md disabled:opacity-50"
              >
                上一页
              </button>
              <span className="px-3 py-1">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                className="px-3 py-1 border rounded-md disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
