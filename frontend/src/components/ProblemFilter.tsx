import { useState } from 'react'
import { Search, X } from 'lucide-react'

export interface FilterState {
  search: string
  difficultyMin: number
  difficultyMax: number
  tagIds: string[]
}

interface ProblemFilterProps {
  filter: FilterState
  tags: { id: string; name: string; color: string | null }[]
  onChange: (filter: FilterState) => void
  onApply: () => void
}

export default function ProblemFilter({ filter, tags, onChange, onApply }: ProblemFilterProps) {
  const [searchInput, setSearchInput] = useState(filter.search)

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    onChange({ ...filter, search: value })
  }

  const toggleTag = (tagId: string) => {
    const newTagIds = filter.tagIds.includes(tagId)
      ? filter.tagIds.filter(id => id !== tagId)
      : [...filter.tagIds, tagId]
    onChange({ ...filter, tagIds: newTagIds })
  }

  const clearAll = () => {
    setSearchInput('')
    onChange({ search: '', difficultyMin: 1, difficultyMax: 10, tagIds: [] })
  }

  const hasActiveFilter = filter.search || filter.tagIds.length > 0 || 
    filter.difficultyMin > 1 || filter.difficultyMax < 10

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      {/* 搜索框 */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="搜索题目..."
          value={searchInput}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* 难度范围 */}
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700 mb-2 block">
          难度范围: {filter.difficultyMin} - {filter.difficultyMax}
        </label>
        <div className="flex gap-4 items-center">
          <input
            type="range"
            min={1}
            max={10}
            value={filter.difficultyMin}
            onChange={(e) => {
              const val = Number(e.target.value)
              onChange({ 
                ...filter, 
                difficultyMin: Math.min(val, filter.difficultyMax) 
              })
            }}
            className="flex-1"
          />
          <input
            type="range"
            min={1}
            max={10}
            value={filter.difficultyMax}
            onChange={(e) => {
              const val = Number(e.target.value)
              onChange({ 
                ...filter, 
                difficultyMax: Math.max(val, filter.difficultyMin) 
              })
            }}
            className="flex-1"
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>简单 (1-3)</span>
          <span>中等 (4-7)</span>
          <span>困难 (8-10)</span>
        </div>
      </div>

      {/* 标签筛选 */}
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700 mb-2 block">标签</label>
        <div className="flex flex-wrap gap-2">
          {tags.map(tag => (
            <button
              key={tag.id}
              onClick={() => toggleTag(tag.id)}
              className={`text-xs px-3 py-1.5 rounded-md border transition-all ${
                filter.tagIds.includes(tag.id)
                  ? 'bg-blue-100 text-blue-700 border-blue-300'
                  : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'
              }`}
            >
              {tag.name}
            </button>
          ))}
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-3">
        <button
          onClick={onApply}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          应用筛选
        </button>
        {hasActiveFilter && (
          <button
            onClick={clearAll}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors text-sm flex items-center gap-1"
          >
            <X className="w-4 h-4" />
            清除筛选
          </button>
        )}
      </div>
    </div>
  )
}
