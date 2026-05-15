import { CheckCircle, XCircle, AlertCircle, Clock, Loader2 } from 'lucide-react'
import type { Submission } from '../types/submission'

interface SubmissionResultProps {
  submission: Submission | null
  isSubmitting: boolean
}

function statusDisplay(status: Submission['status']) {
  switch (status) {
    case 'pending':
      return { icon: Clock, label: '等待评测', colorClass: 'text-yellow-600 bg-yellow-50 border-yellow-200' }
    case 'judging':
      return { icon: Loader2, label: '评测中', colorClass: 'text-blue-600 bg-blue-50 border-blue-200' }
    case 'accepted':
      return { icon: CheckCircle, label: '通过', colorClass: 'text-green-600 bg-green-50 border-green-200' }
    case 'failed':
      return { icon: XCircle, label: '未通过', colorClass: 'text-red-600 bg-red-50 border-red-200' }
    case 'error':
      return { icon: AlertCircle, label: '错误', colorClass: 'text-red-600 bg-red-50 border-red-200' }
  }
}

function formatRuntime(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)} s`
  return `${ms} ms`
}

function formatMemory(kb: number): string {
  if (kb >= 1024 * 1024) return `${(kb / 1024 / 1024).toFixed(2)} GB`
  if (kb >= 1024) return `${(kb / 1024).toFixed(2)} MB`
  return `${kb} KB`
}

export default function SubmissionResult({ submission, isSubmitting }: SubmissionResultProps) {
  // 正在提交中
  if (isSubmitting && !submission) {
    return (
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-6">
        <div className="flex items-center gap-3 text-blue-600">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="font-medium">提交中...</span>
        </div>
      </div>
    )
  }

  // 无提交数据
  if (!submission) {
    return null
  }

  const display = statusDisplay(submission.status)
  const IconComponent = display.icon

  return (
    <div className={`rounded-lg border p-5 ${display.colorClass}`}>
      {/* 状态头部 */}
      <div className="flex items-center gap-2 mb-4">
        <IconComponent className={`w-5 h-5 ${submission.status === 'judging' ? 'animate-spin' : ''}`} />
        <span className="text-lg font-semibold">{display.label}</span>
      </div>

      {/* 评测结果摘要（仅在 accepted / failed 时显示） */}
      {(submission.status === 'accepted' || submission.status === 'failed') && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-white/60 rounded px-3 py-2">
            <div className="text-xs opacity-70 mb-0.5">运行时间</div>
            <div className="font-mono text-sm font-medium">
              {submission.runtime_ms != null ? formatRuntime(submission.runtime_ms) : '-'}
            </div>
          </div>
          <div className="bg-white/60 rounded px-3 py-2">
            <div className="text-xs opacity-70 mb-0.5">内存</div>
            <div className="font-mono text-sm font-medium">
              {submission.memory_kb != null ? formatMemory(submission.memory_kb) : '-'}
            </div>
          </div>
          <div className="bg-white/60 rounded px-3 py-2">
            <div className="text-xs opacity-70 mb-0.5">通过</div>
            <div className="font-mono text-sm font-medium">
              {submission.passed_count != null && submission.total_count != null
                ? `${submission.passed_count} / ${submission.total_count}`
                : submission.passed_count != null
                  ? `${submission.passed_count}`
                  : '-'}
            </div>
          </div>
        </div>
      )}

      {/* 错误信息 */}
      {submission.error_message && (
        <div className="mt-2">
          <div className="text-xs font-medium opacity-70 mb-1">错误信息：</div>
          <pre className="text-sm whitespace-pre-wrap font-mono bg-black/5 rounded px-3 py-2 max-h-40 overflow-y-auto">
            {submission.error_message}
          </pre>
        </div>
      )}
    </div>
  )
}
