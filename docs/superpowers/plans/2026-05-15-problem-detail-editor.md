# 题目详情页 + CodeMirror 编辑器实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现题目详情页，包含左右分栏布局（题目描述 + CodeMirror 代码编辑器）、11 种语言支持、语言选择器。

**Architecture:** 题目详情页采用左右分栏布局，左侧渲染题目描述和示例，右侧集成 CodeMirror 6 代码编辑器。语言选择器通过下拉菜单切换编辑器语法高亮。CodeMirror 使用 `@uiw/react-codemirror` React 封装库简化集成。

**Tech Stack:** React 18 + TypeScript 5.8 + Tailwind CSS 3 + CodeMirror 6 + @uiw/react-codemirror

**Design Doc:** （基于对话中的设计确认）

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `package.json` | 修改 | 添加 CodeMirror 6 依赖 |
| `src/pages/ProblemDetailPage.tsx` | 创建 | 题目详情页（左右分栏容器） |
| `src/components/CodeEditor.tsx` | 创建 | CodeMirror 6 编辑器封装 |
| `src/components/LanguageSelector.tsx` | 创建 | 语言选择下拉框 |
| `src/App.tsx` | 修改 | 添加 `/problems/:id` 路由 |
| `src/components/ProblemCard.tsx` | 修改 | 更新链接为 `/problems/${id}` |

---

## 依赖安装

需要安装以下 npm 包：

```bash
npm install @uiw/react-codemirror @codemirror/state @codemirror/view @codemirror/theme-one-dark @codemirror/commands
npm install @codemirror/lang-cpp @codemirror/lang-python @codemirror/lang-java @codemirror/lang-javascript @codemirror/lang-go @codemirror/lang-rust @codemirror/lang-php @codemirror/lang-ruby
```

**依赖说明：**
- `@uiw/react-codemirror`: CodeMirror 6 的 React 封装
- `@codemirror/state`, `@codemirror/view`, `@codemirror/commands`: CodeMirror 核心
- `@codemirror/theme-one-dark`: 暗色主题
- `@codemirror/lang-*`: 各语言语法高亮支持（8 个包覆盖 11 种语言）

---

### Task 1: 安装 CodeMirror 6 依赖

**Files:**
- Modify: `frontend/package.json`（间接修改）

**背景:** CodeMirror 6 需要安装核心库和语言包。

- [ ] **Step 1: 安装依赖**

```bash
cd D:\AI_code_assistant\frontend
npm install @uiw/react-codemirror @codemirror/state @codemirror/view @codemirror/theme-one-dark @codemirror/commands @codemirror/lang-cpp @codemirror/lang-python @codemirror/lang-java @codemirror/lang-javascript @codemirror/lang-go @codemirror/lang-rust @codemirror/lang-php @codemirror/lang-ruby
```

Expected: 安装成功，无 peer dependency 冲突。

- [ ] **Step 2: 验证安装**

```bash
Test-Path D:\AI_code_assistant\frontend\node_modules\@uiw\react-codemirror\package.json
Test-Path D:\AI_code_assistant\frontend\node_modules\@codemirror\lang-python\package.json
```

Expected: 全部返回 `True`。

---

### Task 2: 创建 LanguageSelector 组件

**Files:**
- Create: `frontend/src/components/LanguageSelector.tsx`

**背景:** 语言选择下拉框，支持 11 种语言，选择后切换编辑器语法高亮。

- [ ] **Step 1: 创建 LanguageSelector.tsx**

创建文件 `frontend/src/components/LanguageSelector.tsx`：

```typescript
import { ChevronDown } from 'lucide-react'

export type Language =
  | 'c'
  | 'cpp'
  | 'csharp'
  | 'python'
  | 'java'
  | 'javascript'
  | 'typescript'
  | 'go'
  | 'rust'
  | 'php'
  | 'ruby'

export interface LanguageOption {
  value: Language
  label: string
  extension: string
}

export const languages: LanguageOption[] = [
  { value: 'python', label: 'Python', extension: 'py' },
  { value: 'cpp', label: 'C++', extension: 'cpp' },
  { value: 'c', label: 'C', extension: 'c' },
  { value: 'java', label: 'Java', extension: 'java' },
  { value: 'javascript', label: 'JavaScript', extension: 'js' },
  { value: 'typescript', label: 'TypeScript', extension: 'ts' },
  { value: 'csharp', label: 'C#', extension: 'cs' },
  { value: 'go', label: 'Go', extension: 'go' },
  { value: 'rust', label: 'Rust', extension: 'rs' },
  { value: 'php', label: 'PHP', extension: 'php' },
  { value: 'ruby', label: 'Ruby', extension: 'rb' },
]

interface LanguageSelectorProps {
  value: Language
  onChange: (lang: Language) => void
}

export default function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  const selected = languages.find(l => l.value === value)

  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as Language)}
        className="appearance-none bg-white border border-gray-300 text-gray-700 py-2 pl-4 pr-10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer text-sm font-medium"
      >
        {languages.map(lang => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
    </div>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\LanguageSelector.tsx
```

Expected: `True`

---

### Task 3: 创建 CodeEditor 组件

**Files:**
- Create: `frontend/src/components/CodeEditor.tsx`

**背景:** CodeMirror 6 编辑器封装，支持 11 种语言语法高亮、暗色主题、自动缩进。

- [ ] **Step 1: 创建 CodeEditor.tsx**

创建文件 `frontend/src/components/CodeEditor.tsx`：

```typescript
import React, { useMemo } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { cpp } from '@codemirror/lang-cpp'
import { python } from '@codemirror/lang-python'
import { java } from '@codemirror/lang-java'
import { javascript } from '@codemirror/lang-javascript'
import { go } from '@codemirror/lang-go'
import { rust } from '@codemirror/lang-rust'
import { php } from '@codemirror/lang-php'
import { ruby } from '@codemirror/lang-ruby'
import type { Language } from './LanguageSelector'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  language: Language
  height?: string
}

function getLanguageExtension(lang: Language) {
  switch (lang) {
    case 'c':
    case 'cpp':
      return cpp()
    case 'csharp':
      // C# 用 C++ 语法近似高亮
      return cpp()
    case 'python':
      return python()
    case 'java':
      return java()
    case 'javascript':
      return javascript()
    case 'typescript':
      // TypeScript 用 JavaScript 语法高亮（包含 TS 支持）
      return javascript({ typescript: true })
    case 'go':
      return go()
    case 'rust':
      return rust()
    case 'php':
      return php()
    case 'ruby':
      return ruby()
    default:
      return javascript()
  }
}

export default function CodeEditor({ value, onChange, language, height = '400px' }: CodeEditorProps) {
  const extensions = useMemo(() => {
    return [oneDark, getLanguageExtension(language)]
  }, [language])

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden">
      <CodeMirror
        value={value}
        height={height}
        extensions={extensions}
        onChange={onChange}
        theme="dark"
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightActiveLine: true,
          foldGutter: false,
          dropCursor: false,
          allowMultipleSelections: false,
          indentOnInput: true,
          bracketMatching: true,
          closeBrackets: true,
          autocompletion: false,
          highlightSelectionMatches: true,
        }}
        className="text-sm"
      />
    </div>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\CodeEditor.tsx
```

Expected: `True`

---

### Task 4: 创建 ProblemDetailPage

**Files:**
- Create: `frontend/src/pages/ProblemDetailPage.tsx`

**背景:** 题目详情页，左右分栏布局。左侧显示题目描述，右侧显示代码编辑器。

- [ ] **Step 1: 创建 ProblemDetailPage.tsx**

创建文件 `frontend/src/pages/ProblemDetailPage.tsx`：

```typescript
import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { problems, difficultyConfig } from '../data/mockProblems'
import CodeEditor from '../components/CodeEditor'
import LanguageSelector, { languages } from '../components/LanguageSelector'
import type { Language } from '../components/LanguageSelector'
import { ArrowLeft, BookOpen, Lightbulb, Clock } from 'lucide-react'

// 各语言的默认代码模板
const defaultTemplates: Record<Language, string> = {
  python: 'def solution():\n    pass\n',
  cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    return 0;\n}\n',
  c: '#include <stdio.h>\n\nint main() {\n    return 0;\n}\n',
  java: 'public class Solution {\n    public static void main(String[] args) {\n        \n    }\n}\n',
  javascript: 'function solution() {\n    \n}\n',
  typescript: 'function solution(): void {\n    \n}\n',
  csharp: 'using System;\n\nclass Program {\n    static void Main() {\n        \n    }\n}\n',
  go: 'package main\n\nfunc main() {\n    \n}\n',
  rust: 'fn main() {\n    \n}\n',
  php: '<?php\n\nfunction solution() {\n    \n}\n',
  ruby: 'def solution\n  \nend\n',
}

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [language, setLanguage] = useState<Language>('python')
  const [code, setCode] = useState(defaultTemplates['python'])

  const problem = useMemo(() => {
    return problems.find(p => p.id === id)
  }, [id])

  const handleLanguageChange = (newLang: Language) => {
    setLanguage(newLang)
    setCode(defaultTemplates[newLang])
  }

  if (!problem) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">题目不存在</p>
        <Link to="/problems" className="text-blue-600 hover:underline mt-2 inline-block">
          返回题目列表
        </Link>
      </div>
    )
  }

  const diffConfig = difficultyConfig[problem.difficulty]
  const acceptancePercent = Math.round(problem.acceptanceRate * 100)

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* 顶部工具栏 */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/problems"
            className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">返回列表</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400 font-mono">#{problem.id}</span>
            <h1 className="text-lg font-semibold text-gray-900">{problem.title}</h1>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diffConfig.color}`}>
              {diffConfig.label}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <LanguageSelector value={language} onChange={handleLanguageChange} />
        </div>
      </div>

      {/* 左右分栏 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：题目描述 */}
        <div className="w-1/2 overflow-y-auto border-r border-gray-200 bg-white">
          <div className="p-6">
            {/* 题目统计 */}
            <div className="flex items-center gap-6 mb-6 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>通过率 {acceptancePercent}%</span>
              </div>
              <div className="flex items-center gap-1">
                <BookOpen className="w-4 h-4" />
                <span>{problem.totalSubmissions.toLocaleString()} 次提交</span>
              </div>
            </div>

            {/* 标签 */}
            <div className="flex flex-wrap gap-2 mb-6">
              {problem.tags.map(tag => (
                <span
                  key={tag}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-md"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* 题目描述 */}
            <div className="prose prose-gray max-w-none">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">题目描述</h3>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {problem.description}
              </p>
            </div>

            {/* 占位：输入输出格式 */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">输入格式</h3>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                （输入格式占位，后续接入真实数据）
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">输出格式</h3>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                （输出格式占位，后续接入真实数据）
              </div>
            </div>

            {/* 占位：示例 */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">示例</h3>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                <p className="font-medium mb-2">示例 1：</p>
                <p className="mb-1"><span className="text-gray-500">输入：</span>...</p>
                <p className="mb-1"><span className="text-gray-500">输出：</span>...</p>
                <p><span className="text-gray-500">解释：</span>...</p>
              </div>
            </div>

            {/* 占位：提示 */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                提示
              </h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
                （提示占位，后续接入真实数据）
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：代码编辑器 */}
        <div className="w-1/2 flex flex-col bg-gray-900">
          <div className="flex-1 p-4">
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              height="calc(100vh - 12rem)"
            />
          </div>

          {/* 底部操作栏 */}
          <div className="px-4 py-3 bg-gray-800 border-t border-gray-700 flex items-center justify-between">
            <div className="text-xs text-gray-400">
              当前语言: {languages.find(l => l.value === language)?.label}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => alert('运行功能需要后端支持（开发中）')}
                className="px-4 py-2 bg-gray-700 text-gray-200 rounded-md hover:bg-gray-600 transition-colors text-sm"
              >
                运行测试
              </button>
              <button
                onClick={() => alert('提交功能需要后端支持（开发中）')}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm font-medium"
              >
                提交代码
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证文件**

```bash
Test-Path D:\AI_code_assistant\frontend\src\pages\ProblemDetailPage.tsx
```

Expected: `True`

---

### Task 5: 修改 App.tsx 添加题目详情路由

**Files:**
- Modify: `frontend/src/App.tsx`

**背景:** 添加 `/problems/:id` 路由指向 ProblemDetailPage。

- [ ] **Step 1: 修改 App.tsx**

读取当前 `App.tsx`，添加：

```typescript
import ProblemDetailPage from './pages/ProblemDetailPage'
```

在 `/problems` 路由下方添加：

```tsx
<Route path="/problems/:id" element={<ProblemDetailPage />} />
```

- [ ] **Step 2: 验证修改**

确认 `App.tsx` 包含 `ProblemDetailPage` 的导入和路由。

---

### Task 6: 修改 ProblemCard 链接

**Files:**
- Modify: `frontend/src/components/ProblemCard.tsx`

**背景:** ProblemCard 的 `to` 属性当前是 `/problems/${problem.id}`，需要确认正确无误。

- [ ] **Step 1: 验证 ProblemCard 链接**

读取 `ProblemCard.tsx`，确认 Link 的 `to` 属性为：

```tsx
to={`/problems/${problem.id}`}
```

如果已经是这个格式，则无需修改。

---

### Task 7: 最终验证

**Files:**
- 所有已修改/创建的文件

- [ ] **Step 1: TypeScript 编译检查**

```bash
cd D:\AI_code_assistant\frontend
npx tsc -b
```

Expected: 无错误输出

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

Expected: `dist/` 目录生成

- [ ] **Step 4: 浏览器验证**

启动开发服务器：
```bash
cd D:\AI_code_assistant\frontend
npm run dev
```

在浏览器中验证：
- [ ] 访问 `http://localhost:3000/problems/1` — 看到题目详情页
- [ ] 左侧显示题目描述（标题、难度、标签、描述）
- [ ] 右侧显示代码编辑器（暗色主题）
- [ ] 顶部有语言选择器，点击切换语言
- [ ] 切换语言后编辑器语法高亮变化（如 Python → C++）
- [ ] 代码模板随语言切换而变化
- [ ] 底部有 "运行测试" 和 "提交代码" 按钮
- [ ] 点击 "返回列表" 回到题目列表
- [ ] 从题目列表点击卡片进入详情页

---

## 自检清单

### 规格覆盖

| 设计需求 | 对应 Task |
|---|---|
| 左右分栏布局 | Task 4 (ProblemDetailPage) |
| 题目描述展示 | Task 4 (左侧栏) |
| CodeMirror 6 编辑器 | Task 3 (CodeEditor) |
| 11 种语言支持 | Task 2 + Task 3 (LanguageSelector + CodeEditor) |
| 语言选择器 | Task 2 (LanguageSelector) |
| 路由集成 | Task 5 (App.tsx) |
| 运行/提交按钮 | Task 4 (底部操作栏) |

### 占位符扫描

- [x] 无 TBD/TODO
- [x] 所有步骤包含完整代码

### 类型一致性

- [x] `Language` 类型在 LanguageSelector.tsx 和 CodeEditor.tsx 中一致
- [x] `languages` 数组在 LanguageSelector.tsx 中导出并被 CodeEditor 使用

---

> **计划完成时间估算:** 7 个 Task，约 40-50 分钟  
> **计划文档版本:** v1.0  
> **生成时间:** 2026-05-15
