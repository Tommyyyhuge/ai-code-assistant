# 前端代码修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复审查发现的所有 P0 + P1 级别问题，提升类型安全、错误处理和架构规范性

**Architecture:** 提取共享类型到独立模块，严格化组件 props 类型，添加运行时错误边界，实现按需加载优化

**Tech Stack:** React 18, TypeScript 5.8, Tailwind CSS, CodeMirror 6, React Router 6

---

## 文件变更映射

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/types/language.ts` | 新建 | 集中管理 Language 联合类型和 languages 常量 |
| `src/components/LanguageSelector.tsx` | 修改 | 移除内联类型定义，从 types/language 导入 |
| `src/components/CodeEditor.tsx` | 修改 | 严格化 language prop 类型，改为动态导入语言包 |
| `src/pages/ProblemDetailPage.tsx` | 修改 | 添加 404 处理、多语言代码状态、problemDetails fallback |
| `src/data/codeTemplates.ts` | 新建 | 提取代码模板到独立数据文件 |

---

## Task 1: 创建共享类型模块

**Files:**
- Create: `src/types/language.ts`

- [ ] **Step 1: 创建语言类型定义文件**

```typescript
export type Language =
  | 'c'
  | 'cpp'
  | 'python'
  | 'java'
  | 'javascript'
  | 'typescript'
  | 'go'
  | 'rust'
  | 'php'

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
  { value: 'go', label: 'Go', extension: 'go' },
  { value: 'rust', label: 'Rust', extension: 'rs' },
  { value: 'php', label: 'PHP', extension: 'php' },
] as const
```

- [ ] **Step 2: 验证文件创建成功**

检查文件路径 `src/types/language.ts` 存在且内容正确。

---

## Task 2: 重构 LanguageSelector 组件

**Files:**
- Modify: `src/components/LanguageSelector.tsx`

- [ ] **Step 1: 重构 LanguageSelector.tsx**

```typescript
import { ChevronDown } from 'lucide-react'
import type { Language } from '../types/language'
import { languages } from '../types/language'

interface LanguageSelectorProps {
  value: Language
  onChange: (lang: Language) => void
}

export default function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
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

- [ ] **Step 2: 更新 ProblemDetailPage 的导入路径**

在 `src/pages/ProblemDetailPage.tsx` 中，将：
```typescript
import type { Language } from '../components/LanguageSelector'
```
改为：
```typescript
import type { Language } from '../types/language'
```

---

## Task 3: 提取代码模板到独立文件

**Files:**
- Create: `src/data/codeTemplates.ts`

- [ ] **Step 1: 创建代码模板数据文件**

```typescript
import type { Language } from '../types/language'

export const codeTemplates: Record<Language, string> = {
  python: '# 在此编写你的 Python 代码\n',
  cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // 在此编写你的 C++ 代码\n    return 0;\n}\n',
  c: '#include <stdio.h>\n\nint main() {\n    // 在此编写你的 C 代码\n    return 0;\n}\n',
  java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        // 在此编写你的 Java 代码\n    }\n}\n',
  javascript: '// 在此编写你的 JavaScript 代码\n',
  typescript: '// 在此编写你的 TypeScript 代码\n',
  go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    // 在此编写你的 Go 代码\n}\n',
  rust: 'fn main() {\n    // 在此编写你的 Rust 代码\n}\n',
  php: '<?php\n// 在此编写你的 PHP 代码\n',
}
```

---

## Task 4: 重构 CodeEditor 组件（类型严格化 + 动态导入）

**Files:**
- Modify: `src/components/CodeEditor.tsx`

- [ ] **Step 1: 重写 CodeEditor 为动态导入模式**

```typescript
import { useState, useEffect, useMemo } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { javascript } from '@codemirror/lang-javascript'
import type { Extension } from '@codemirror/state'
import type { Language } from '../types/language'

interface CodeEditorProps {
  code: string
  language: Language
  onChange: (value: string) => void
  readOnly?: boolean
  height?: string
}

const languageLoaders: Record<string, () => Promise<Extension>> = {
  c: () => import('@codemirror/lang-cpp').then(m => m.cpp()),
  cpp: () => import('@codemirror/lang-cpp').then(m => m.cpp()),
  python: () => import('@codemirror/lang-python').then(m => m.python()),
  java: () => import('@codemirror/lang-java').then(m => m.java()),
  javascript: () => import('@codemirror/lang-javascript').then(m => m.javascript()),
  typescript: () => import('@codemirror/lang-javascript').then(m => m.javascript({ typescript: true })),
  go: () => import('@codemirror/lang-go').then(m => m.go()),
  rust: () => import('@codemirror/lang-rust').then(m => m.rust()),
  php: () => import('@codemirror/lang-php').then(m => m.php()),
}

export default function CodeEditor({
  code,
  language,
  onChange,
  readOnly = false,
  height = '400px',
}: CodeEditorProps) {
  const [languageExtension, setLanguageExtension] = useState<Extension | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)

    const loadLanguage = async () => {
      const loader = languageLoaders[language]
      if (!loader) {
        setLanguageExtension(javascript())
        setIsLoading(false)
        return
      }

      try {
        const ext = await loader()
        if (!cancelled) {
          setLanguageExtension(ext)
          setIsLoading(false)
        }
      } catch (error) {
        console.error(`Failed to load language ${language}:`, error)
        if (!cancelled) {
          setLanguageExtension(javascript())
          setIsLoading(false)
        }
      }
    }

    loadLanguage()
    return () => { cancelled = true }
  }, [language])

  const extensions = useMemo(() => {
    return languageExtension ? [languageExtension] : []
  }, [languageExtension])

  if (isLoading) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-700 bg-gray-800" style={{ height }}>
        <div className="flex items-center justify-center h-full text-gray-400">
          加载编辑器...
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700">
      <CodeMirror
        value={code}
        height={height}
        theme={oneDark}
        extensions={extensions}
        onChange={onChange}
        readOnly={readOnly}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightActiveLine: true,
          foldGutter: true,
          autocompletion: true,
          bracketMatching: true,
          closeBrackets: true,
          indentOnInput: true,
          tabSize: 2,
        }}
      />
    </div>
  )
}
```

---

## Task 5: 重构 ProblemDetailPage（404 + 多语言状态 + Fallback）

**Files:**
- Modify: `src/pages/ProblemDetailPage.tsx`
- 依赖: `src/data/codeTemplates.ts`, `src/types/language.ts`

- [ ] **Step 1: 添加导入和类型定义**

在文件顶部添加：
```typescript
import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { problems } from '../data/mockProblems'
import { codeTemplates } from '../data/codeTemplates'
import LanguageSelector from '../components/LanguageSelector'
import CodeEditor from '../components/CodeEditor'
import type { Language } from '../types/language'
import { ArrowLeft, Clock, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
```

- [ ] **Step 2: 添加 problemDetails fallback 定义**

```typescript
const defaultProblemDetail: ProblemDetail = {
  inputFormat: '暂无输入格式说明',
  outputFormat: '暂无输出格式说明',
  samples: [],
  constraints: [],
}
```

- [ ] **Step 3: 重构组件状态管理**

```typescript
export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [language, setLanguage] = useState<Language>('python')
  const [showSamples, setShowSamples] = useState(true)
  const [showConstraints, setShowConstraints] = useState(true)

  const problem = useMemo(() => problems.find(p => p.id === id), [id])
  const detail = useMemo(() => problemDetails[id] ?? defaultProblemDetail, [id])

  // 为每种语言维护独立的代码状态
  const [codeMap, setCodeMap] = useState<Record<Language, string>>(() => {
    const initial: Partial<Record<Language, string>> = {}
    const langValues: Language[] = ['c', 'cpp', 'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'php']
    langValues.forEach(lang => {
      initial[lang] = codeTemplates[lang]
    })
    return initial as Record<Language, string>
  })

  const currentCode = codeMap[language]

  const handleCodeChange = (value: string) => {
    setCodeMap(prev => ({ ...prev, [language]: value }))
  }

  const handleLanguageChange = (newLang: Language) => {
    setLanguage(newLang)
  }

  // 404 处理
  if (!problem) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">题目未找到</h2>
        <p className="text-gray-600 mb-6">ID 为 {id} 的题目不存在</p>
        <Link
          to="/problems"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          返回题目列表
        </Link>
      </div>
    )
  }

  const diffConfig = difficultyConfig[problem.difficulty]
  const acceptancePercent = Math.round(problem.acceptanceRate * 100)

  // ... 其余渲染逻辑保持不变
}
```

- [ ] **Step 4: 更新 CodeEditor 调用**

确保 CodeEditor 的调用使用 `language` 和 `currentCode`：
```typescript
<CodeEditor
  code={currentCode}
  language={language}
  onChange={handleCodeChange}
  height="500px"
/>
```

---

## Task 6: 构建验证

**Files:**
- 所有已修改文件

- [ ] **Step 1: 运行 TypeScript 编译检查**

```bash
cd D:/AI_code_assistant/frontend
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 2: 运行 ESLint**

```bash
npm run lint
```

Expected: 0 errors, 0 warnings（之前的 eslint-disable 注释已移除）

- [ ] **Step 3: 运行生产构建**

```bash
npm run build
```

Expected: Build successful，无 TypeScript 错误

- [ ] **Step 4: 浏览器验证**

1. 访问 `/problems/1` - 应正常显示题目详情和代码编辑器
2. 访问 `/problems/999` - 应显示 404 页面，不崩溃
3. 切换语言 - 每种语言应有独立的代码内容
4. 刷新页面 - 代码内容应重置为模板（符合预期）

---

## 依赖关系图

```
Task 1 (创建 types/language.ts)
  └── 被 Task 2, 3, 4, 5 依赖

Task 2 (重构 LanguageSelector)
  └── 依赖 Task 1

Task 3 (创建 codeTemplates.ts)
  └── 被 Task 5 依赖

Task 4 (重构 CodeEditor)
  └── 依赖 Task 1

Task 5 (重构 ProblemDetailPage)
  └── 依赖 Task 1, 3

Task 6 (构建验证)
  └── 依赖 Task 2, 4, 5
```

**执行顺序：** Task 1 → Task 3 → (Task 2, Task 4 并行) → Task 5 → Task 6

---

## 自我审查

### 1. 规范覆盖检查

| 审查问题 | 对应 Task | 状态 |
|----------|-----------|------|
| ProblemDetailPage 无效 ID 崩溃 | Task 5 Step 3 | ✅ |
| CodeEditor language 类型不安全 | Task 4 Step 1 | ✅ |
| 切换语言丢失代码 | Task 5 Step 3 | ✅ |
| 类型与组件混放 | Task 1 + Task 2 | ✅ |
| problemDetails 数据缺失 | Task 5 Step 2 | ✅ |
| 语言包全量导入 | Task 4 Step 1 | ✅ |

### 2. 占位符扫描

- [x] 无 "TBD" / "TODO"
- [x] 所有代码块完整
- [x] 文件路径精确
- [x] 命令与预期输出明确

### 3. 类型一致性检查

- `Language` 类型在 Task 1 定义，Task 2/4/5 引用一致 ✅
- `CodeEditorProps.language` 从 `string` 改为 `Language` ✅
- `codeTemplates` 键类型为 `Language` ✅
- `codeMap` 键类型为 `Language` ✅

---

## 执行方式

**计划已保存到 `docs/superpowers/plans/2026-05-15-code-fixes.md`**

**两种执行选项：**

**1. Subagent-Driven（推荐）** — 每个 Task 分配独立子代理，逐任务审查，快速迭代

**2. Inline Execution** — 在当前会话中使用 executing-plans 批量执行，设置检查点

**选择哪种方式？**
