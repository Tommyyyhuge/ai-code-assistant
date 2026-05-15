export interface TagBrief {
  id: string
  name: string
  color: string | null
}

export interface ProblemListItem {
  id: string
  title: string
  titleSlug: string
  difficulty: number  // 1-10
  sourceOj: string | null
  tags: TagBrief[]
}

export interface ProblemDetail extends ProblemListItem {
  description: string
  inputFormat: string
  outputFormat: string
  constraints: string | null
  timeLimitMs: number
  memoryLimitMb: number
}

// 难度显示辅助函数
export const difficultyLabel = (d: number): string => {
  if (d <= 3) return '简单'
  if (d <= 7) return '中等'
  return '困难'
}

export const difficultyColorClass = (d: number): string => {
  if (d <= 3) return 'bg-green-100 text-green-700 border-green-200'
  if (d <= 7) return 'bg-yellow-100 text-yellow-700 border-yellow-200'
  return 'bg-red-100 text-red-700 border-red-200'
}
