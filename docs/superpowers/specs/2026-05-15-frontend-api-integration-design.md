# 前端对接 API 设计方案

> 日期: 2026-05-15  
> 版本: v1.0  
> 范围: 前端题目功能从 Mock 数据切换至真实后端 API  
> 状态: 已批准

---

## 1. 项目背景

后端题目 API 和标签体系已实现（problems/tags CRUD + 筛选分页）。前端当前使用 Mock 数据（`mockProblems.ts`），需要切换为调用真实后端 API，实现前后端数据打通。

## 2. 目标

- 题目列表页从后端 API 获取真实数据
- 题目详情页从后端 API 获取完整信息
- 标签数据从后端 API 获取
- 统一前端数据类型与后端 Schema 对齐
- 新增 ProblemStore（Zustand）管理题目状态

## 3. 范围边界

### 3.1 包含（IN SCOPE）

- ProblemStore（Zustand）状态管理
- API 层扩展（problemApi, tagApi）
- 类型定义更新（ProblemListItem, ProblemDetail, TagBrief）
- 题目列表页（ProblemListPage）对接 API
- 题目卡片（ProblemCard）适配新数据格式
- 题目筛选器（ProblemFilter）适配数字难度
- 题目详情页（ProblemDetailPage）对接 API

### 3.2 排除（OUT OF SCOPE）

- 题目创建/编辑页面（管理员功能，后续迭代）
- 提交记录/评测结果（依赖评测引擎）
- 用户进度/统计（依赖提交记录）
- 题目搜索高亮/全文检索（后续优化）
- 图片/文件上传（题目描述中的图片）

## 4. 架构方案

### 4.1 整体架构

```
后端 API (FastAPI)
    ↓ HTTP
API 层 (axios) - problemApi, tagApi
    ↓
ProblemStore (Zustand) - 状态管理
    ↓
React 组件 - ProblemListPage, ProblemDetailPage, etc.
```

### 4.2 状态管理策略

采用 **Zustand ProblemStore**，原因：
- 与现有 authStore 保持一致
- 题目状态需要跨组件共享（列表页 ↔ 详情页）
- 筛选条件需要持久化

## 5. ProblemStore 设计

```typescript
// stores/problemStore.ts
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
      
      const { items, total, total_pages } = response.data
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

## 6. API 层扩展

```typescript
// services/api.ts

// 在现有 api 实例基础上新增

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

export const tagApi = {
  getTags: (category?: string) => 
    api.get('/tags', { params: { category } }),
}
```

## 7. 类型定义

```typescript
// types/problem.ts

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
  if (d <= 3) return 'text-green-500 bg-green-50'
  if (d <= 7) return 'text-yellow-500 bg-yellow-50'
  return 'text-red-500 bg-red-50'
}
```

## 8. 组件层改动

### 8.1 ProblemListPage

```typescript
// 改动要点
import { useProblemStore } from '../stores/problemStore'

const ProblemListPage = () => {
  const { problems, isLoading, total, page, pageSize, fetchProblems } = useProblemStore()
  
  useEffect(() => {
    fetchProblems(page, pageSize)
  }, [page, pageSize])
  
  // 渲染逻辑基本不变，数据源从 mockProblems 改为 problems
}
```

### 8.2 ProblemCard

```typescript
// 改动要点：difficulty 从字符串改为数字

interface Props {
  problem: ProblemListItem
}

const ProblemCard = ({ problem }: Props) => {
  return (
    <div>
      <h3>{problem.title}</h3>
      <span className={difficultyColorClass(problem.difficulty)}>
        {difficultyLabel(problem.difficulty)}
      </span>
      <div>
        {problem.tags.map(tag => (
          <span key={tag.id} style={{ color: tag.color || undefined }}>
            {tag.name}
          </span>
        ))}
      </div>
    </div>
  )
}
```

### 8.3 ProblemFilter

```typescript
// 改动要点：难度筛选改为数字区间

const ProblemFilter = () => {
  const { filters, setFilters, resetFilters, fetchProblems } = useProblemStore()
  
  return (
    <div>
      {/* 难度范围 Slider */}
      <input
        type="range"
        min={1}
        max={10}
        value={filters.difficultyMin || 1}
        onChange={(e) => setFilters({ difficultyMin: Number(e.target.value) })}
      />
      <input
        type="range"
        min={1}
        max={10}
        value={filters.difficultyMax || 10}
        onChange={(e) => setFilters({ difficultyMax: Number(e.target.value) })}
      />
      
      {/* 搜索框 */}
      <input
        value={filters.search || ''}
        onChange={(e) => setFilters({ search: e.target.value })}
      />
      
      {/* 标签筛选 */}
      <TagFilter />
      
      <button onClick={() => fetchProblems(1)}>应用筛选</button>
      <button onClick={resetFilters}>重置</button>
    </div>
  )
}
```

### 8.4 ProblemDetailPage

```typescript
// 改动要点：从 Mock 数据改为 API 获取

const ProblemDetailPage = () => {
  const { id } = useParams()
  const { currentProblem, isDetailLoading, fetchProblemDetail } = useProblemStore()
  
  useEffect(() => {
    if (id) fetchProblemDetail(id)
  }, [id])
  
  if (isDetailLoading) return <Loading />
  if (!currentProblem) return <NotFound />
  
  return (
    <div>
      <h1>{currentProblem.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: marked(currentProblem.description) }} />
      <div>
        <h3>输入格式</h3>
        <pre>{currentProblem.inputFormat}</pre>
      </div>
      <div>
        <h3>输出格式</h3>
        <pre>{currentProblem.outputFormat}</pre>
      </div>
      {/* 约束条件 */}
      {currentProblem.constraints && (
        <div>
          <h3>数据范围</h3>
          <pre>{currentProblem.constraints}</pre>
        </div>
      )}
    </div>
  )
}
```

## 9. 缺失字段处理

后端暂无以下字段（依赖评测引擎）：
- `acceptanceRate`（通过率）
- `totalSubmissions`（总提交次数）

前端暂时显示占位符：
```tsx
<span className="text-gray-400">-</span>
```

等评测引擎完成后，后端添加统计字段，前端再显示真实数据。

## 10. 文件变更清单

### 新增文件
- `frontend/src/stores/problemStore.ts` - ProblemStore 状态管理
- `frontend/src/types/problem.ts` - 题目相关类型定义

### 修改文件
- `frontend/src/services/api.ts` - 新增 problemApi, tagApi
- `frontend/src/pages/ProblemListPage.tsx` - 使用 ProblemStore
- `frontend/src/components/ProblemCard.tsx` - 适配数字难度
- `frontend/src/components/ProblemFilter.tsx` - 适配数字难度和 API 筛选
- `frontend/src/pages/ProblemDetailPage.tsx` - 使用 ProblemStore 获取详情

### 可选保留
- `frontend/src/data/mockProblems.ts` - 可作为 fallback 或开发调试使用

## 11. 错误处理策略

| 场景 | 处理方式 |
|------|----------|
| API 请求失败 | Store 中设置 error 状态，组件显示错误提示 |
| 题目不存在（404） | 跳转 404 页面或显示"题目未找到" |
| 网络超时 | 自动重试 1 次，仍失败则显示错误 |
| 服务器 500 | 显示"服务器错误，请稍后重试" |

## 12. 性能优化

- **防抖搜索**：搜索框输入后 300ms 再触发 API 请求
- **分页加载**：滚动加载或分页按钮，避免一次性加载大量数据
- **缓存策略**：题目详情可短期缓存（5 分钟），列表数据实时获取

---

## 13. 验收标准

- [ ] 题目列表页显示后端真实数据（非 Mock）
- [ ] 题目详情页正确显示题目描述、输入输出格式
- [ ] 筛选功能正常工作（难度、搜索、标签）
- [ ] 分页功能正常工作
- [ ] 标签正确显示（名称、颜色）
- [ ] 加载状态和错误状态正常显示
- [ ] 刷新页面后数据正确加载
