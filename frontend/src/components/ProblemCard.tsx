import { Link } from 'react-router-dom'
import type { ProblemListItem } from '../types/problem'
import { difficultyLabel, difficultyColorClass } from '../types/problem'
import { FileText } from 'lucide-react'

interface ProblemCardProps {
  problem: ProblemListItem
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  return (
    <Link
      to={`/problems/${problem.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200 group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400 font-mono">
            #{problem.titleSlug}
          </span>
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
            {problem.title}
          </h3>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium border ${difficultyColorClass(problem.difficulty)}`}>
          {difficultyLabel(problem.difficulty)}
        </span>
      </div>

      <div className="flex items-center gap-4 mb-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <FileText className="w-4 h-4" />
          <span>通过率 -</span>
        </div>
        <div className="flex items-center gap-1">
          <FileText className="w-4 h-4" />
          <span>- 次提交</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {problem.tags.map(tag => (
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
    </Link>
  )
}
