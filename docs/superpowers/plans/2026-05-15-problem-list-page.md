# 题目列表页实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现题目列表页，包含卡片网格展示、难度/分类筛选、搜索功能，使用模拟数据。

**Architecture:** 分离关注点：mockProblems.ts 提供数据，ProblemCard 负责单卡片渲染，ProblemFilter 处理筛选逻辑，ProblemListPage 作为页面容器组合所有子组件。筛选状态用 React useState 管理，纯前端过滤。

**Tech Stack:** React 18 + TypeScript 5.8 + Tailwind CSS 3 + Lucide React

**Design Doc:** `docs/superpowers/specs/2026-05-15-navbar-layout-register-design.md`（同项目设计规范）

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `src/data/mockProblems.ts` | 创建 | 模拟题目数据（15-20道）+ Problem 类型定义 |
| `src/components/ProblemCard.tsx` | 创建 | 单道题目卡片组件 |
| `src/components/ProblemFilter.tsx` | 创建 | 筛选栏（搜索框 + 难度 + 分类） |
| `src/pages/ProblemListPage.tsx` | 创建 | 题目列表页面（容器 + 网格布局） |
| `src/App.tsx` | 修改 | 添加 `/problems` 路由（替换占位符） |

---

### Task 1: 创建模拟数据

**Files:**
- Create: `frontend/src/data/mockProblems.ts`

**背景:** 定义 Problem 类型和 15 道模拟题目数据，不依赖后端。

- [ ] **Step 1: 创建 mockProblems.ts**

创建文件 `frontend/src/data/mockProblems.ts`：

```typescript
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface Problem {
  id: string
  title: string
  difficulty: Difficulty
  tags: string[]
  acceptanceRate: number
  totalSubmissions: number
  description: string
}

export const problems: Problem[] = [
  {
    id: '1',
    title: '两数之和',
    difficulty: 'easy',
    tags: ['数组', '哈希表'],
    acceptanceRate: 0.65,
    totalSubmissions: 15200,
    description: '给定一个整数数组和一个目标值，找出数组中和为目标值的两个数。',
  },
  {
    id: '2',
    title: '最长无重复子串',
    difficulty: 'medium',
    tags: ['字符串', '滑动窗口', '哈希表'],
    acceptanceRate: 0.42,
    totalSubmissions: 23100,
    description: '给定一个字符串，找出不含有重复字符的最长子串的长度。',
  },
  {
    id: '3',
    title: '合并两个有序链表',
    difficulty: 'easy',
    tags: ['链表', '递归'],
    acceptanceRate: 0.78,
    totalSubmissions: 18900,
    description: '将两个升序链表合并为一个新的升序链表。',
  },
  {
    id: '4',
    title: '最长回文子串',
    difficulty: 'medium',
    tags: ['字符串', '动态规划'],
    acceptanceRate: 0.35,
    totalSubmissions: 19800,
    description: '给定一个字符串，找到最长的回文子串。',
  },
  {
    id: '5',
    title: '接雨水',
    difficulty: 'hard',
    tags: ['数组', '双指针', '动态规划', '栈'],
    acceptanceRate: 0.28,
    totalSubmissions: 12400,
    description: '给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子下雨之后能接多少雨水。',
  },
  {
    id: '6',
    title: '二叉树的中序遍历',
    difficulty: 'easy',
    tags: ['树', '栈', '递归'],
    acceptanceRate: 0.82,
    totalSubmissions: 16700,
    description: '给定一个二叉树的根节点，返回它的中序遍历。',
  },
  {
    id: '7',
    title: '每日温度',
    difficulty: 'medium',
    tags: ['数组', '栈', '单调栈'],
    acceptanceRate: 0.55,
    totalSubmissions: 14300,
    description: '给定一个整数数组 temperatures，表示每天的温度，返回一个数组 answer，其中 answer[i] 是指对于第 i 天，下一个更高温度出现在几天后。',
  },
  {
    id: '8',
    title: '编辑距离',
    difficulty: 'hard',
    tags: ['字符串', '动态规划'],
    acceptanceRate: 0.22,
    totalSubmissions: 9800,
    description: '给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。',
  },
  {
    id: '9',
    title: '有效的括号',
    difficulty: 'easy',
    tags: ['字符串', '栈'],
    acceptanceRate: 0.88,
    totalSubmissions: 21500,
    description: '给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。',
  },
  {
    id: '10',
    title: '全排列',
    difficulty: 'medium',
    tags: ['数组', '回溯'],
    acceptanceRate: 0.48,
    totalSubmissions: 17600,
    description: '给定一个不含重复数字的数组 nums，返回其所有可能的全排列。',
  },
  {
    id: '11',
    title: '最小覆盖子串',
    difficulty: 'hard',
    tags: ['字符串', '滑动窗口', '哈希表'],
    acceptanceRate: 0.19,
    totalSubmissions: 8900,
    description: '给定两个字符串 s 和 t，返回 s 中涵盖 t 所有字符的最小子串。',
  },
  {
    id: '12',
    title: '反转链表',
    difficulty: 'easy',
    tags: ['链表', '递归'],
    acceptanceRate: 0.91,
    totalSubmissions: 20100,
    description: '给你单链表的头节点 head，请你反转链表，并返回反转后的链表。',
  },
  {
    id: '13',
    title: '岛屿数量',
    difficulty: 'medium',
    tags: ['数组', '深度优先搜索', '广度优先搜索', '并查集'],
    acceptanceRate: 0.52,
    totalSubmissions: 16500,
    description: '给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。',
  },
  {
    id: '14',
    title: '正则表达式匹配',
    difficulty: 'hard',
    tags: ['字符串', '动态规划', '递归'],
    acceptanceRate: 0.15,
    totalSubmissions: 7600,
    description: '给你一个字符串 s 和一个字符规律 p，请你来实现一个支持 '.' 和 '*' 的正则表达式匹配。',
  },
  {
    id: '15',
    title: '爬楼梯',
    difficulty: 'easy',
    tags: ['动态规划', '记忆化搜索'],
    acceptanceRate: 0.73,
    totalSubmissions: 19800,
    description: '假设你正在爬楼梯。需要 n 阶你才能到达楼顶。每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？',
  },
]

// 提取所有不重复的分类标签
export const allTags = Array.from(new Set(problems.flatMap(p => p.tags)))

// 难度配置（用于显示）
export const difficultyConfig = {
  easy: { label: '简单', color: 'bg-green-100 text-green-700' },
  medium: { label: '中等', color: 'bg-yellow-100 text-yellow-700' },
  hard: { label: '困难', color: 'bg-red-100 text-red-700' },
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\data\mockProblems.ts
```

Expected: `True`

---

### Task 2: 创建 ProblemCard 组件

**Files:**
- Create: `frontend/src/components/ProblemCard.tsx`

**背景:** 单道题目卡片，显示题号、标题、难度、通过率、标签。

- [ ] **Step 1: 创建 ProblemCard.tsx**

创建文件 `frontend/src/components/ProblemCard.tsx`：

```typescript
import { Link } from 'react-router-dom'
import type { Problem } from '../data/mockProblems'
import { difficultyConfig } from '../data/mockProblems'
import { TrendingUp, FileText } from 'lucide-react'

interface ProblemCardProps {
  problem: Problem
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  const diffConfig = difficultyConfig[problem.difficulty]
  const acceptancePercent = Math.round(problem.acceptanceRate * 100)

  return (
    <Link
      to={`/problems/${problem.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200 group"
    >
      {/* 标题行 */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400 font-mono">#{problem.id}</span>
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
            {problem.title}
          </h3>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${diffConfig.color}`}>
          {diffConfig.label}
        </span>
      </div>

      {/* 描述 */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {problem.description}
      </p>

      {/* 通过率 */}
      <div className="flex items-center gap-4 mb-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <TrendingUp className="w-4 h-4" />
          <span>通过率 {acceptancePercent}%</span>
        </div>
        <div className="flex items-center gap-1">
          <FileText className="w-4 h-4" />
          <span>{problem.totalSubmissions.toLocaleString()} 次提交</span>
        </div>
      </div>

      {/* 标签 */}
      <div className="flex flex-wrap gap-2">
        {problem.tags.map(tag => (
          <span
            key={tag}
            className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-md"
          >
            {tag}
          </span>
        ))}
      </div>
    </Link>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\ProblemCard.tsx
```

Expected: `True`

---

### Task 3: 创建 ProblemFilter 组件

**Files:**
- Create: `frontend/src/components/ProblemFilter.tsx`

**背景:** 筛选栏包含搜索框、难度多选、分类多选。筛选状态通过回调函数传递给父组件。

- [ ] **Step 1: 创建 ProblemFilter.tsx**

创建文件 `frontend/src/components/ProblemFilter.tsx`：

```typescript
import { useState } from 'react'
import { Search, X } from 'lucide-react'
import { allTags } from '../data/mockProblems'
import type { Difficulty } from '../data/mockProblems'

export interface FilterState {
  search: string
  difficulties: Difficulty[]
  tags: string[]
}

interface ProblemFilterProps {
  filter: FilterState
  onChange: (filter: FilterState) => void
}

const difficultyOptions: { value: Difficulty; label: string; color: string }[] = [
  { value: 'easy', label: '简单', color: 'bg-green-100 text-green-700 border-green-200' },
  { value: 'medium', label: '中等', color: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  { value: 'hard', label: '困难', color: 'bg-red-100 text-red-700 border-red-200' },
]

export default function ProblemFilter({ filter, onChange }: ProblemFilterProps) {
  const [searchInput, setSearchInput] = useState(filter.search)

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    onChange({ ...filter, search: value })
  }

  const toggleDifficulty = (diff: Difficulty) => {
    const newDiffs = filter.difficulties.includes(diff)
      ? filter.difficulties.filter(d => d !== diff)
      : [...filter.difficulties, diff]
    onChange({ ...filter, difficulties: newDiffs })
  }

  const toggleTag = (tag: string) => {
    const newTags = filter.tags.includes(tag)
      ? filter.tags.filter(t => t !== tag)
      : [...filter.tags, tag]
    onChange({ ...filter, tags: newTags })
  }

  const clearAll = () => {
    setSearchInput('')
    onChange({ search: '', difficulties: [], tags: [] })
  }

  const hasActiveFilter = filter.search || filter.difficulties.length > 0 || filter.tags.length > 0

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      {/* 搜索框 */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="搜索题目..."
          value={searchInput}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* 难度筛选 */}
      <div className="mb-4">
        <span className="text-sm font-medium text-gray-700 mb-2 block">难度</span>
        <div className="flex gap-2">
          {difficultyOptions.map(option => (
            <button
              key={option.value}
              onClick={() => toggleDifficulty(option.value)}
              className={`px-3 py-1.5 text-sm rounded-md border transition-all ${
                filter.difficulties.includes(option.value)
                  ? option.color + ' border-current'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* 分类筛选 */}
      <div className="mb-4">
        <span className="text-sm font-medium text-gray-700 mb-2 block">分类</span>
        <div className="flex flex-wrap gap-2">
          {allTags.map(tag => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-3 py-1.5 text-sm rounded-md border transition-all ${
                filter.tags.includes(tag)
                  ? 'bg-blue-100 text-blue-700 border-blue-200'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* 清除筛选 */}
      {hasActiveFilter && (
        <button
          onClick={clearAll}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 transition-colors"
        >
          <X className="w-4 h-4" />
          清除筛选
        </button>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\ProblemFilter.tsx
```

Expected: `True`

---

### Task 4: 创建 ProblemListPage

**Files:**
- Create: `frontend/src/pages/ProblemListPage.tsx`

**背景:** 题目列表页面容器，组合 ProblemFilter 和 ProblemCard，管理筛选状态和过滤逻辑。

- [ ] **Step 1: 创建 ProblemListPage.tsx**

创建文件 `frontend/src/pages/ProblemListPage.tsx`：

```typescript
import { useState, useMemo } from 'react'
import { problems } from '../data/mockProblems'
import ProblemCard from '../components/ProblemCard'
import ProblemFilter from '../components/ProblemFilter'
import type { FilterState } from '../components/ProblemFilter'
import { BookOpen } from 'lucide-react'

export default function ProblemListPage() {
  const [filter, setFilter] = useState<FilterState>({
    search: '',
    difficulties: [],
    tags: [],
  })

  const filteredProblems = useMemo(() => {
    return problems.filter(problem => {
      // 搜索筛选
      if (filter.search) {
        const searchLower = filter.search.toLowerCase()
        const matchTitle = problem.title.toLowerCase().includes(searchLower)
        const matchDesc = problem.description.toLowerCase().includes(searchLower)
        if (!matchTitle && !matchDesc) return false
      }

      // 难度筛选
      if (filter.difficulties.length > 0) {
        if (!filter.difficulties.includes(problem.difficulty)) return false
      }

      // 分类筛选
      if (filter.tags.length > 0) {
        const hasMatchingTag = problem.tags.some(tag => filter.tags.includes(tag))
        if (!hasMatchingTag) return false
      }

      return true
    })
  }, [filter])

  return (
    <div>
      {/* 页面标题 */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-7 h-7 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">题目列表</h1>
        </div>
        <p className="text-gray-600">
          共 {filteredProblems.length} 道题目（总计 {problems.length} 道）
        </p>
      </div>

      {/* 筛选栏 */}
      <ProblemFilter filter={filter} onChange={setFilter} />

      {/* 题目网格 */}
      {filteredProblems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProblems.map(problem => (
            <ProblemCard key={problem.id} problem={problem} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">没有找到匹配的题目</p>
          <p className="text-gray-400 text-sm mt-2">试试调整筛选条件</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\pages\ProblemListPage.tsx
```

Expected: `True`

---

### Task 5: 修改 App.tsx 添加题目列表路由

**Files:**
- Modify: `frontend/src/App.tsx`

**背景:** 当前 `/problems` 路由是占位 div，需要替换为 ProblemListPage 组件。

- [ ] **Step 1: 修改 App.tsx**

读取当前 `App.tsx`，找到 `/problems` 路由行，将：

```tsx
<Route path="/problems" element={<div className="text-center text-gray-500">题目列表页（开发中）</div>} />
```

替换为：

```tsx
<Route path="/problems" element={<ProblemListPage />} />
```

并在文件顶部添加导入：

```typescript
import ProblemListPage from './pages/ProblemListPage'
```

- [ ] **Step 2: 验证修改**

确认 `App.tsx` 包含：
- `import ProblemListPage from './pages/ProblemListPage'`
- `<Route path="/problems" element={<ProblemListPage />} />`

---

### Task 6: 最终验证

**Files:**
- 所有已修改/创建的文件

- [ ] **Step 1: TypeScript 编译检查**

```bash
cd D:\AI_code_assistant\frontend
npx tsc -b
```

Expected: 无错误输出（退出码 0）

- [ ] **Step 2: ESLint 检查**

```bash
cd D:\AI_code_assistant\frontend
npm run lint
```

Expected: 0 errors

- [ ] **Step 3: 生产构建**

```bash
cd D:\AI_code_assistant\frontend
npm run build
```

Expected: `dist/` 目录成功生成

- [ ] **Step 4: 浏览器验证**

启动开发服务器：
```bash
cd D:\AI_code_assistant\frontend
npm run dev
```

在浏览器中验证：
- [ ] 访问 `http://localhost:3000/problems` — 看到题目列表页
- [ ] 页面显示 15 道题目卡片，每道题包含标题、难度、通过率、标签
- [ ] 搜索框输入 "两数" — 只显示匹配的题目
- [ ] 点击难度 "简单" — 只显示简单题
- [ ] 点击分类 "数组" — 只显示含数组标签的题目
- [ ] 同时选择多个筛选条件 — 结果正确取交集
- [ ] 点击 "清除筛选" — 恢复显示所有题目
- [ ] 选择无匹配条件的组合 — 显示 "没有找到匹配的题目"

---

## 自检清单

### 规格覆盖

| 设计需求 | 对应 Task |
|---|---|
| 模拟数据（15-20道） | Task 1 (mockProblems.ts) |
| 卡片网格展示 | Task 2 (ProblemCard) + Task 4 (grid layout) |
| 搜索框 | Task 3 (ProblemFilter) |
| 难度筛选 | Task 3 (ProblemFilter) |
| 分类筛选 | Task 3 (ProblemFilter) |
| 页面路由 | Task 5 (App.tsx) |

### 占位符扫描

- [x] 无 TBD/TODO/placeholder
- [x] 所有步骤包含完整代码

### 类型一致性

- [x] `Problem` 类型在 mockProblems.ts、ProblemCard.tsx、ProblemListPage.tsx 中一致
- [x] `FilterState` 类型在 ProblemFilter.tsx 和 ProblemListPage.tsx 中一致
- [x] `Difficulty` 类型在 mockProblems.ts 和 ProblemFilter.tsx 中一致

---

## 附录

### 可能遇到的问题

**Q: `line-clamp-2` 不生效？**
A: Tailwind CSS 3 默认未启用 line-clamp，需要在 `tailwind.config.js` 的 `plugins` 中添加 `require('@tailwindcss/line-clamp')`，或使用 `overflow-hidden` + 固定高度作为替代。

**Q: 卡片网格在大屏幕上显示 3 列，小屏幕显示 1 列？**
A: 已在 ProblemListPage 中使用 `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`，默认响应式行为正确。

**Q: 筛选性能问题？**
A: 当前 15 道题，useMemo 足够。如果数据量增长到 1000+，需要考虑虚拟列表或后端分页。

---

> **计划完成时间估算:** 6 个 Task，约 30-40 分钟  
> **计划文档版本:** v1.0  
> **生成时间:** 2026-05-15
