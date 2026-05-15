# 前端对接 API 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将前端题目功能从 Mock 数据切换至真实后端 API，实现前后端数据打通。

**Architecture:** 新增 Zustand ProblemStore 管理题目状态，扩展 API 层调用后端接口，更新组件适配新数据格式。

**Tech Stack:** React 18, TypeScript, Zustand, Axios, Tailwind CSS

---

## 文件结构

### 新增文件
| 文件 | 职责 |
|------|------|
| `frontend/src/types/problem.ts` | 题目相关 TypeScript 类型定义 |
| `frontend/src/stores/problemStore.ts` | ProblemStore 状态管理 |

### 修改文件
| 文件 | 修改内容 |
|------|----------|
| `frontend/src/services/api.ts` | 新增 problemApi, tagApi |
| `frontend/src/components/ProblemCard.tsx` | 适配数字难度和新类型 |
| `frontend/src/components/ProblemFilter.tsx` | 适配数字难度和 API 标签 |
| `frontend/src/pages/ProblemListPage.tsx` | 使用 ProblemStore 获取数据 |
| `frontend/src/pages/ProblemDetailPage.tsx` | 使用 ProblemStore 获取详情 |

---

## Task 1: 创建类型定义

**Files:**
- Create: `frontend/src/types/problem.ts`

**依赖:** 无

- [ ] **Step 1: 创建类型定义文件**

创建文件 `frontend/src/types/problem.ts`：

```typescript
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
```

- [ ] **Step 2: 验证类型定义**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/types/problem.ts
```

Expected: 无类型错误。

---

## Task 2: 扩展 API 层

**Files:**
- Modify: `frontend/src/services/api.ts`

**依赖:** Task 1（类型已定义）

- [ ] **Step 1: 在 api.ts 末尾新增 API 函数**

修改文件 `frontend/src/services/api.ts`，在 `authApi` 定义之后添加：

```typescript
// 题目 API
export const problemApi = {
  getProblems: (params?: {
    search?: string
    difficulty_min?: number
    difficulty_max?: number
    source_oj?: string
    tag_ids?: string[]
    page?: number
    page_size?: number
  }) => api.get('/problems', { params }),
  
  getProblem: (id: string) => api.get(`/problems/${id}`),
}

// 标签 API
export const tagApi = {
  getTags: (category?: string) => 
    api.get('/tags', { params: { category } }),
}
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/services/api.ts
```

Expected: 无类型错误。

---

## Task 3: 创建 ProblemStore

**Files:**
- Create: `frontend/src/stores/problemStore.ts`

**依赖:** Task 2（API 层已扩展）

- [ ] **Step 1: 创建 ProblemStore**

创建文件 `frontend/src/stores/problemStore.ts`：

```typescript
import { create } from 'zustand'
import { problemApi, tagApi } from '../services/api'
import type { ProblemListItem, ProblemDetail, TagBrief } from '../types/problem'

interface ProblemFilters {
  search?: string
  difficultyMin?: number
  difficultyMax?: number
  sourceOj?: string
  tagIds?: string[]
}

interface ProblemState {
  // 列表状态
  problems: ProblemListItem[]
  total: number
  page: number
  pageSize: number
  isLoading: boolean
  listError: string | null
  
  // 详情状态
  currentProblem: ProblemDetail | null
  isDetailLoading: boolean
  detailError: string | null
  
  // 标签
  tags: TagBrief[]
  isTagsLoading: boolean
  
  // 筛选条件
  filters: ProblemFilters
  
  // Actions
  fetchProblems: (page?: number, pageSize?: number) => Promise<void>
  fetchProblemDetail: (id: string) => Promise<void>
  fetchTags: () => Promise<void>
  setFilters: (filters: Partial<ProblemFilters>) => void
  resetFilters: () => void
}

export const useProblemStore = create<ProblemState>((set, get) => ({
  // 初始状态
  problems: [],
  total: 0,
  page: 1,
  pageSize: 20,
  isLoading: false,
  listError: null,
  
  currentProblem: null,
  isDetailLoading: false,
  detailError: null,
  
  tags: [],
  isTagsLoading: false,
  
  filters: {},
  
  // 获取题目列表
  fetchProblems: async (page = 1, pageSize = 20) => {
    set({ isLoading: true, listError: null })
    try {
      const { filters } = get()
      const response = await problemApi.getProblems({
        page,
        page_size: pageSize,
        search: filters.search,
        difficulty_min: filters.difficultyMin,
        difficulty_max: filters.difficultyMax,
        source_oj: filters.sourceOj,
        tag_ids: filters.tagIds,
      })
      
      const { items, total } = response.data
      set({
        problems: items,
        total,
        page,
        pageSize,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        isLoading: false,
        listError: error.response?.data?.detail || '获取题目列表失败',
      })
    }
  },
  
  // 获取题目详情
  fetchProblemDetail: async (id: string) => {
    set({ isDetailLoading: true, detailError: null })
    try {
      const response = await problemApi.getProblem(id)
      set({
        currentProblem: response.data,
        isDetailLoading: false,
      })
    } catch (error: any) {
      set({
        isDetailLoading: false,
        detailError: error.response?.data?.detail || '获取题目详情失败',
      })
    }
  },
  
  // 获取标签列表
  fetchTags: async () => {
    set({ isTagsLoading: true })
    try {
      const response = await tagApi.getTags()
      set({ tags: response.data, isTagsLoading: false })
    } catch (error) {
      set({ isTagsLoading: false })
    }
  },
  
  // 设置筛选条件
  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }))
  },
  
  // 重置筛选条件
  resetFilters: () => {
    set({ filters: {}, page: 1 })
  },
}))
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/stores/problemStore.ts
```

Expected: 无类型错误。

---

## Task 4: 重构 ProblemCard 组件

**Files:**
- Modify: `frontend/src/components/ProblemCard.tsx`

**依赖:** Task 1（类型已定义）

- [ ] **Step 1: 重写 ProblemCard 组件**

修改文件 `frontend/src/components/ProblemCard.tsx`：

```tsx
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
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/components/ProblemCard.tsx
```

Expected: 无类型错误。

---

## Task 5: 重构 ProblemFilter 组件

**Files:**
- Modify: `frontend/src/components/ProblemFilter.tsx`

**依赖:** Task 1（类型已定义）

- [ ] **Step 1: 重写 ProblemFilter 组件**

修改文件 `frontend/src/components/ProblemFilter.tsx`：

```tsx
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
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/components/ProblemFilter.tsx
```

Expected: 无类型错误。

---

## Task 6: 重构 ProblemListPage

**Files:**
- Modify: `frontend/src/pages/ProblemListPage.tsx`

**依赖:** Task 3（ProblemStore 已创建）, Task 4（ProblemCard 已更新）, Task 5（ProblemFilter 已更新）

- [ ] **Step 1: 重写 ProblemListPage**

修改文件 `frontend/src/pages/ProblemListPage.tsx`：

```tsx
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
    resetFilters,
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
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/pages/ProblemListPage.tsx
```

Expected: 无类型错误。

---

## Task 7: 重构 ProblemDetailPage

**Files:**
- Modify: `frontend/src/pages/ProblemDetailPage.tsx`

**依赖:** Task 3（ProblemStore 已创建）

- [ ] **Step 1: 重写 ProblemDetailPage**

修改文件 `frontend/src/pages/ProblemDetailPage.tsx`：

```tsx
import { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useProblemStore } from '../stores/problemStore'
import LanguageSelector from '../components/LanguageSelector'
import CodeEditor from '../components/CodeEditor'
import { codeTemplates } from '../data/codeTemplates'
import type { Language } from '../types/language'
import { difficultyLabel, difficultyColorClass } from '../types/problem'
import { ArrowLeft, Clock, Loader2, AlertTriangle } from 'lucide-react'

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { 
    currentProblem, 
    isDetailLoading, 
    detailError,
    fetchProblemDetail 
  } = useProblemStore()

  useEffect(() => {
    if (id) {
      fetchProblemDetail(id)
    }
  }, [id])

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
    <div className="max-w-4xl mx-auto">
      {/* 头部 */}
      <div className="mb-6">
        <Link 
          to="/problems" 
          className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </Link>
        
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
      </div>

      {/* 标签 */}
      <div className="flex flex-wrap gap-2 mb-6">
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
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">题目描述</h2>
        <div className="prose max-w-none">
          <p className="whitespace-pre-wrap">{currentProblem.description}</p>
        </div>
      </div>

      {/* 输入格式 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">输入格式</h2>
        <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
          {currentProblem.inputFormat}
        </pre>
      </div>

      {/* 输出格式 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">输出格式</h2>
        <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
          {currentProblem.outputFormat}
        </pre>
      </div>

      {/* 约束条件 */}
      {currentProblem.constraints && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">数据范围与约束</h2>
          <pre className="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
            {currentProblem.constraints}
          </pre>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 验证编译**

```bash
cd D:\AI_code_assistant\frontend
npx tsc --noEmit src/pages/ProblemDetailPage.tsx
```

Expected: 无类型错误。

---

## Task 8: 集成验证

**Files:**
- 无新增/修改

**依赖:** Task 6 和 Task 7 完成

- [ ] **Step 1: 启动后端服务**

确保后端服务正在运行：

```bash
cd D:\AI_code_assistant\backend
uvicorn app.main:app --reload
```

- [ ] **Step 2: 启动前端开发服务器**

```bash
cd D:\AI_code_assistant\frontend
npm run dev
```

- [ ] **Step 3: 功能验证清单**

在浏览器中访问 http://localhost:3000，验证：

| 检查项 | 预期结果 |
|--------|----------|
| 题目列表页加载 | 显示真实数据（或空列表） |
| 筛选功能 | 难度范围、搜索、标签筛选正常工作 |
| 分页功能 | 上一页/下一页正常工作 |
| 题目详情页 | 正确显示题目描述、输入输出格式 |
| 加载状态 | 显示 Loading 动画 |
| 错误处理 | 网络错误时显示错误提示 |

- [ ] **Step 4: 运行构建检查**

```bash
cd D:\AI_code_assistant\frontend
npm run build
```

Expected: 构建成功，无 TypeScript 错误。

---

## 自审检查清单

**1. Spec 覆盖检查：**

| 设计需求 | 对应任务 | 状态 |
|----------|----------|------|
| ProblemStore | Task 3 | ✅ |
| API 层扩展 | Task 2 | ✅ |
| 类型定义 | Task 1 | ✅ |
| ProblemCard 适配 | Task 4 | ✅ |
| ProblemFilter 适配 | Task 5 | ✅ |
| ProblemListPage 对接 | Task 6 | ✅ |
| ProblemDetailPage 对接 | Task 7 | ✅ |
| 验证测试 | Task 8 | ✅ |

**2. Placeholder 扫描：**
- 无 TBD/TODO/"implement later"/"similar to Task X"
- 所有步骤包含完整代码

**3. 类型一致性检查：**
- `ProblemListItem` 在所有 Task 中使用一致
- `TagBrief` 类型定义与使用一致
- API 参数名与后端接口一致

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-05-15-frontend-api-integration.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints for review

**Which approach?**
