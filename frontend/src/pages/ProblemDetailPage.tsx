import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useProblemStore } from '../stores/problemStore'
import { difficultyLabel, difficultyColorClass } from '../types/problem'
import { ArrowLeft, Clock, Loader2, AlertTriangle, Play } from 'lucide-react'
import CodeEditor from '../components/CodeEditor'
import LanguageSelector from '../components/LanguageSelector'
import SubmissionResult from '../components/SubmissionResult'
import { submissionApi } from '../services/submissionApi'
import type { Submission } from '../types/submission'
import type { Language } from '../types/language'

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { 
    currentProblem, 
    isDetailLoading, 
    detailError,
    fetchProblemDetail 
  } = useProblemStore()

  const [code, setCode] = useState<string>("")
  const [language, setLanguage] = useState<Language>("cpp")
  const [submission, setSubmission] = useState<Submission | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (id) {
      fetchProblemDetail(id)
    }
  }, [id])

  const pollSubmission = useCallback((submissionId: string) => {
    const interval = setInterval(async () => {
      try {
        const result = await submissionApi.getSubmission(submissionId)
        setSubmission(result)
        if (["accepted", "failed", "error"].includes(result.status)) {
          clearInterval(interval)
          setIsSubmitting(false)
        }
      } catch (error) {
        console.error("轮询失败:", error)
        clearInterval(interval)
        setIsSubmitting(false)
      }
    }, 2000)

    // 30 秒超时保护
    setTimeout(() => {
      clearInterval(interval)
      setIsSubmitting(false)
    }, 30000)
  }, [])

  const handleSubmit = async () => {
    if (!code.trim()) {
      alert("请先编写代码")
      return
    }
    setIsSubmitting(true)
    setSubmission(null)
    try {
      const result = await submissionApi.submit({
        problem_id: id!,
        code,
        language,
      })
      setSubmission(result)
      if (result.id) {
        pollSubmission(result.id)
      }
    } catch (error) {
      console.error("提交失败:", error)
      alert("提交失败，请重试")
      setIsSubmitting(false)
    }
  }

  if (isDetailLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (detailError || !currentProblem) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          {detailError || '题目未找到'}
        </h2>
        <Link to="/problems" className="text-blue-600 hover:underline">
          返回题目列表
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* 返回按钮 */}
      <div className="mb-6">
        <Link 
          to="/problems" 
          className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </Link>
      </div>

      {/* 左右分栏 */}
      <div className="flex gap-6">
        {/* 左侧：题目信息 */}
        <div className="w-1/2 min-w-0 space-y-6">
          {/* 头部信息 */}
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {currentProblem.title}
              </h1>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span className={`px-2 py-1 rounded-full text-xs border ${difficultyColorClass(currentProblem.difficulty)}`}>
                  {difficultyLabel(currentProblem.difficulty)}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {currentProblem.timeLimitMs}ms
                </span>
                <span>{currentProblem.memoryLimitMb}MB</span>
              </div>
            </div>
          </div>

          {/* 标签 */}
          <div className="flex flex-wrap gap-2">
            {currentProblem.tags.map(tag => (
              <span
                key={tag.id}
                className="text-xs px-2 py-1 rounded-md border"
                style={{ 
                  backgroundColor: tag.color ? `${tag.color}20` : '#f3f4f6',
                  color: tag.color || '#4b5563',
                  borderColor: tag.color ? `${tag.color}40` : '#e5e7eb'
                }}
              >
                {tag.name}
              </span>
            ))}
          </div>

          {/* 题目描述 */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">题目描述</h2>
            <div className="prose max-w-none">
              <p className="whitespace-pre-wrap">{currentProblem.description}</p>
            </div>
          </div>

          {/* 输入格式 */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">输入格式</h2>
            <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
              {currentProblem.inputFormat}
            </pre>
          </div>

          {/* 输出格式 */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">输出格式</h2>
            <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
              {currentProblem.outputFormat}
            </pre>
          </div>

          {/* 约束条件 */}
          {currentProblem.constraints && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">数据范围与约束</h2>
              <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
                {currentProblem.constraints}
              </pre>
            </div>
          )}
        </div>

        {/* 右侧：代码编辑区 */}
        <div className="w-1/2 min-w-0">
          {/* 顶部：语言选择 + 提交按钮 */}
          <div className="flex items-center justify-between mb-4">
            <LanguageSelector value={language} onChange={setLanguage} />
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg
                         hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed
                         transition-colors font-medium text-sm"
            >
              <Play className="w-4 h-4" />
              {isSubmitting ? '提交中...' : '提交'}
            </button>
          </div>

          {/* 代码编辑器 */}
          <div className="mb-4">
            <CodeEditor
              code={code}
              language={language}
              onChange={setCode}
              height="400px"
            />
          </div>

          {/* 评测结果 */}
          <SubmissionResult submission={submission} isSubmitting={isSubmitting} />
        </div>
      </div>
    </div>
  )
}
