import { useState } from 'react'
import type { KnowledgeNodeTreeItem } from '../stores/knowledgeStore'

const statusIcon: Record<string, string> = {
  not_started: '○',
  in_progress: '◐',
  completed: '●',
}

interface Props {
  items: KnowledgeNodeTreeItem[]
  selectedSlug: string | null
  onSelect: (slug: string) => void
  level?: number
}

function TreeNode({ item, selectedSlug, onSelect, level }: {
  item: KnowledgeNodeTreeItem
  selectedSlug: string | null
  onSelect: (slug: string) => void
  level: number
}) {
  const [expanded, setExpanded] = useState(level < 2)
  const hasChildren = item.children.length > 0
  const isSelected = item.title_slug === selectedSlug

  return (
    <li>
      <div
        className={`flex items-center gap-1.5 px-2 py-1 cursor-pointer rounded text-sm
          ${isSelected ? 'bg-blue-100 text-blue-800 font-medium' : 'hover:bg-gray-100 text-gray-700'}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onSelect(item.title_slug)}
      >
        {hasChildren ? (
          <span
            className="text-xs w-4 text-center cursor-pointer text-gray-400"
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}
          >
            {expanded ? '▼' : '▶'}
          </span>
        ) : (
          <span className="w-4" />
        )}
        <span className="text-xs" title={
          item.user_status === 'completed' ? '已完成' :
          item.user_status === 'in_progress' ? '学习中' : '未开始'
        }>
          {statusIcon[item.user_status] || '○'}
        </span>
        <span className="truncate">{item.title}</span>
      </div>
      {hasChildren && expanded && (
        <ul>
          {item.children.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              selectedSlug={selectedSlug}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function KnowledgeTree({ items, selectedSlug, onSelect, level = 0 }: Props) {
  return (
    <ul className="space-y-0.5">
      {items.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          selectedSlug={selectedSlug}
          onSelect={onSelect}
          level={level}
        />
      ))}
    </ul>
  )
}
