# 前端稳定降级重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将前端从 React 19 + Vite 8 + TypeScript 6 pre-release 降级到 React 18 + Vite 5 + TypeScript 5.8 稳定版，同时修复所有导致"修复时卡退"的根因。

**Architecture:** 通过依赖版本降级消除不稳定因素，添加 ErrorBoundary 三层防御体系捕获错误，修复 API 响应格式不匹配，完整集成 Tailwind CSS 样式系统。

**Tech Stack:** React 18.3 + TypeScript 5.8 + Vite 5.4 + React Router 6 + Zustand 4 + Tailwind CSS 3 + Axios

**Design Doc:** `docs/superpowers/specs/2026-05-15-fix-crashes-design.md`

---

## 文件结构映射

| 文件 | 操作 | 职责 |
|---|---|---|
| `frontend/package.json` | 修改 | 依赖版本降级 + 新增 tailwindcss/postcss/autoprefixer |
| `frontend/package-lock.json` | 重新生成 | 依赖锁定文件 |
| `frontend/vite.config.ts` | 修改 | 删除 `hmr: { overlay: false }` |
| `frontend/tsconfig.app.json` | 修改 | 降级 target，删除实验特性 |
| `frontend/tsconfig.json` | 不变 | 项目引用配置 |
| `frontend/tsconfig.node.json` | 不变 | Node 环境配置 |
| `frontend/tailwind.config.js` | 新增 | Tailwind 主题配置 |
| `frontend/postcss.config.js` | 新增 | PostCSS 插件配置 |
| `frontend/src/main.tsx` | 修改 | 包裹 ErrorBoundary，注入 navigate 回调 |
| `frontend/src/App.tsx` | 不变 | 路由结构保持 |
| `frontend/src/App.css` | 重写 | 删除 SCSS 嵌套语法 |
| `frontend/src/index.css` | 重写 | Tailwind @指令 + 清理 BEM |
| `frontend/src/services/api.ts` | 修改 | 401 拦截器改用 navigate 回调 |
| `frontend/src/stores/authStore.ts` | 修改 | 修复 response.data 访问 + register 原子性 |
| `frontend/src/components/LoginForm.tsx` | 修改 | 添加错误保护 |
| `frontend/src/components/ErrorBoundary.tsx` | 新增 | 全局错误边界组件 |
| `frontend/src/types/api.ts` | 新增 | API 响应类型定义 |

---

### Task 1: 清理并重新安装依赖

**Files:**
- Modify: `frontend/package.json`
- Delete: `frontend/package-lock.json`
- Delete: `frontend/node_modules/` (整个目录)

**背景:** 当前 `package.json` 使用 React 19 + Vite 8 + TypeScript 6 pre-release，需要降级到稳定版本。

- [ ] **Step 1: 删除现有依赖**

```bash
cd D:\AI_code_assistant\frontend
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
```

- [ ] **Step 2: 修改 package.json**

打开 `frontend/package.json`，将内容替换为：

```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.16.1",
    "lucide-react": "^1.14.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "zustand": "^4.5.5"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@types/node": "^24.12.3",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "eslint": "^10.3.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.6.0",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.17",
    "typescript": "~5.8.0",
    "typescript-eslint": "^8.59.2",
    "vite": "^5.4.14"
  }
}
```

**变更点说明:**
- `react`: `^19.2.6` → `^18.3.1`
- `react-dom`: `^19.2.6` → `^18.3.1`
- `react-router-dom`: `^7.15.0` → `^6.28.0`
- `zustand`: `^5.0.13` → `^4.5.5`
- `@types/react`: `^19.2.14` → `^18.3.12`
- `@types/react-dom`: `^19.2.3` → `^18.3.1`
- `@vitejs/plugin-react`: `^6.0.1` → `^4.3.4`
- `typescript`: `~6.0.2` → `~5.8.0`
- `vite`: `^8.0.12` → `^5.4.14`
- 新增: `tailwindcss`, `postcss`, `autoprefixer`

- [ ] **Step 3: 安装依赖**

```bash
cd D:\AI_code_assistant\frontend
npm install
```

Expected: 安装成功，无 peer dependency 冲突警告。如果有警告，检查版本兼容性。

- [ ] **Step 4: 验证 node_modules 存在**

```bash
Test-Path D:\AI_code_assistant\frontend\node_modules\react\package.json
Test-Path D:\AI_code_assistant\frontend\node_modules\tailwindcss\package.json
Test-Path D:\AI_code_assistant\frontend\node_modules\vite\package.json
```

Expected: 全部返回 `True`

---

### Task 2: 配置构建工具

**Files:**
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/tsconfig.app.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`

**背景:** 修复 HMR 错误覆盖层配置，降级 TypeScript 编译目标，新增 Tailwind CSS 工具链。

- [ ] **Step 1: 修改 vite.config.ts**

打开 `frontend/vite.config.ts`，替换为：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
})
```

**变更:** 删除 `hmr: { overlay: false }` 配置块，恢复默认的 `overlay: true`。

- [ ] **Step 2: 修改 tsconfig.app.json**

打开 `frontend/tsconfig.app.json`，替换为：

```json
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "types": ["vite/client"],
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

**变更说明:**
- `target`: `"es2023"` → `"ES2020"`
- `lib`: 添加 `"DOM.Iterable"`
- 删除: `verbatimModuleSyntax`, `erasableSyntaxOnly`, `moduleDetection`
- 添加: `resolveJsonModule`, `isolatedModules`, `strict`

- [ ] **Step 3: 创建 tailwind.config.js**

创建文件 `frontend/tailwind.config.js`：

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 4: 创建 postcss.config.js**

创建文件 `frontend/postcss.config.js`：

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 5: 验证配置**

```bash
cd D:\AI_code_assistant\frontend
npx tailwindcss --help
```

Expected: 显示 tailwindcss CLI 帮助信息，证明安装正确。

---

### Task 3: 创建 ErrorBoundary 和 API 类型

**Files:**
- Create: `frontend/src/components/ErrorBoundary.tsx`
- Create: `frontend/src/types/api.ts`

**背景:** 添加全局错误边界捕获 React 渲染错误，定义后端 API 响应类型避免 `any` 类型。

- [ ] **Step 1: 创建 ErrorBoundary 组件**

创建文件 `frontend/src/components/ErrorBoundary.tsx`：

```typescript
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h2>出错了</h2>
            <p style={{ color: '#666' }}>
              {this.state.error?.message || '发生了未知错误'}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                background: '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer'
              }}
            >
              刷新页面
            </button>
          </div>
        )
      )
    }

    return this.props.children
  }
}
```

- [ ] **Step 2: 创建 API 类型定义**

创建文件 `frontend/src/types/api.ts`：

```typescript
/**
 * FastAPI 后端响应类型定义
 * 注意：FastAPI 直接返回模型对象，不嵌套在 {data: ...} 中
 */

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
  elo_rating: number
  is_active: boolean
  created_at: string
}
```

- [ ] **Step 3: 验证文件创建**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\ErrorBoundary.tsx
Test-Path D:\AI_code_assistant\frontend\src\types\api.ts
```

Expected: 全部返回 `True`

---

### Task 4: 修复 API 服务层

**Files:**
- Modify: `frontend/src/services/api.ts`

**背景:** 当前 401 拦截器使用 `window.location.href = '/login'` 硬跳转，导致页面重载和状态丢失。需要改用 React Router 的 `navigate()`。

- [ ] **Step 1: 修改 api.ts**

打开 `frontend/src/services/api.ts`，替换为：

```typescript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 全局 navigate 回调（由 main.tsx 注入）
let navigateCallback: ((path: string) => void) | null = null

export const setNavigateCallback = (cb: (path: string) => void) => {
  navigateCallback = cb
}

// 响应拦截器 - 处理 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      // 优先使用 React Router navigate，避免页面重载
      if (navigateCallback) {
        navigateCallback('/login')
      } else {
        // 降级方案：直接跳转
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  getMe: () =>
    api.get('/auth/me'),
}
```

**变更说明:**
- 新增 `navigateCallback` 全局变量
- 新增 `setNavigateCallback()` 导出函数
- 401 拦截器优先使用 `navigateCallback`，降级到 `window.location.href`

---

### Task 5: 修复 Auth Store

**Files:**
- Modify: `frontend/src/stores/authStore.ts`

**背景:** 当前代码访问 `response.data.data`，但 FastAPI 返回平铺 JSON（`response.data` 就是实际数据），导致所有登录/注册操作抛出 TypeError。

- [ ] **Step 1: 修改 authStore.ts**

打开 `frontend/src/stores/authStore.ts`，替换为：

```typescript
import { create } from 'zustand'
import { authApi } from '../services/api'

interface User {
  id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
  elo_rating: number
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authApi.login({ email, password })
      const { access_token, refresh_token } = response.data
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      const userResponse = await authApi.getMe()
      set({ 
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      set({ isLoading: false, error: message })
      throw error
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      await authApi.register({ username, email, password })
      // 注册成功后直接登录（原子操作，不调用 login action）
      const loginResponse = await authApi.login({ email, password })
      const { access_token, refresh_token } = loginResponse.data
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      const userResponse = await authApi.getMe()
      set({ 
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
    } catch (error: any) {
      const message = error.response?.data?.detail || '注册失败'
      set({ isLoading: false, error: message })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false, error: null })
  },

  fetchUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isAuthenticated: false })
      return
    }
    
    try {
      const response = await authApi.getMe()
      set({ 
        user: response.data,
        isAuthenticated: true 
      })
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
    }
  },
}))
```

**变更说明:**
- `response.data.data` → `response.data`（3 处）
- register 不再调用 `useAuthStore.getState().login()`，改为内联登录逻辑（避免嵌套 set 调用和竞态）
- 新增 `error` 状态字段
- 每个成功分支重置 `error: null`

---

### Task 6: 修复入口点和组件

**Files:**
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/components/LoginForm.tsx`

**背景:** 入口点需要包裹 ErrorBoundary 并注入 navigate 回调，LoginForm 需要更好的错误保护。

- [ ] **Step 1: 修改 main.tsx**

打开 `frontend/src/main.tsx`，替换为：

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, useNavigate } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import ErrorBoundary from './components/ErrorBoundary.tsx'
import { setNavigateCallback } from './services/api.ts'

// 注入 navigate 回调到 API 拦截器
function AppWithNavigate() {
  const navigate = useNavigate()
  setNavigateCallback(navigate)
  return <App />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AppWithNavigate />
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
```

**变更说明:**
- 新增 `AppWithNavigate` 组件注入 `navigate` 回调
- 用 `ErrorBoundary` 包裹整个应用

- [ ] **Step 2: 修改 LoginForm.tsx**

打开 `frontend/src/components/LoginForm.tsx`，替换为：

```typescript
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useNavigate } from 'react-router-dom'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState('')
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError('')
    
    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setLocalError(err.response?.data?.detail || err.message || '登录失败')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {localError && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded">
          {localError}
        </div>
      )}
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          邮箱
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          密码
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? '登录中...' : '登录'}
      </button>
    </form>
  )
}
```

**变更说明:**
- 错误显示添加 `err.message` 回退：`err.response?.data?.detail || err.message || '登录失败'`

---

### Task 7: 修复 CSS 文件

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/App.css`

**背景:** 清理 BEM 全局类名（与 Tailwind 冲突），删除 SCSS 嵌套语法。

- [ ] **Step 1: 重写 index.css**

打开 `frontend/src/index.css`，替换为：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  min-height: 100vh;
  background-color: #f9fafb;
  color: #111827;
  font-family: system-ui, -apple-system, sans-serif;
}

#root {
  min-height: 100vh;
}
```

**变更说明:**
- 添加 Tailwind `@tailwind` 指令
- 删除所有 BEM 类名（`.container`, `.title`, `.card`, `.input`, `.button`, `.label`, `.error`）

- [ ] **Step 2: 重写 App.css**

打开 `frontend/src/App.css`，替换为：

```css
.counter {
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 5px;
  color: var(--accent);
  background: var(--accent-bg);
  border: 2px solid transparent;
  transition: border-color 0.3s;
  margin-bottom: 24px;
}

.counter:hover {
  border-color: var(--accent-border);
}

.counter:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.hero {
  position: relative;
}

.hero .base,
.hero .framework,
.hero .vite {
  inset-inline: 0;
  margin: 0 auto;
}

.hero .base {
  width: 170px;
  position: relative;
  z-index: 0;
}

.hero .framework,
.hero .vite {
  position: absolute;
}

.hero .framework {
  z-index: 1;
  top: 34px;
  height: 28px;
  transform: perspective(2000px) rotateZ(300deg) rotateX(44deg) rotateY(39deg) scale(1.4);
}

.hero .vite {
  z-index: 0;
  top: 107px;
  height: 26px;
  width: auto;
  transform: perspective(2000px) rotateZ(300deg) rotateX(40deg) rotateY(39deg) scale(0.8);
}

#center {
  display: flex;
  flex-direction: column;
  gap: 25px;
  place-content: center;
  place-items: center;
  flex-grow: 1;
}

@media (max-width: 1024px) {
  #center {
    padding: 32px 20px 24px;
    gap: 18px;
  }
}

#next-steps {
  display: flex;
  border-top: 1px solid var(--border);
  text-align: left;
}

#next-steps > div {
  flex: 1 1 0;
  padding: 32px;
}

@media (max-width: 1024px) {
  #next-steps > div {
    padding: 24px 20px;
  }
}

#next-steps .icon {
  margin-bottom: 16px;
  width: 22px;
  height: 22px;
}

@media (max-width: 1024px) {
  #next-steps {
    flex-direction: column;
    text-align: center;
  }
}

#docs {
  border-right: 1px solid var(--border);
}

@media (max-width: 1024px) {
  #docs {
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
}

#next-steps ul {
  list-style: none;
  padding: 0;
  display: flex;
  gap: 8px;
  margin: 32px 0 0;
}

#next-steps ul .logo {
  height: 18px;
}

#next-steps ul a {
  color: var(--text-h);
  font-size: 16px;
  border-radius: 6px;
  background: var(--social-bg);
  display: flex;
  padding: 6px 12px;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: box-shadow 0.3s;
}

#next-steps ul a:hover {
  box-shadow: var(--shadow);
}

#next-steps ul a .button-icon {
  height: 18px;
  width: 18px;
}

@media (max-width: 1024px) {
  #next-steps ul {
    margin-top: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }
}
```

**变更说明:**
- 删除所有 SCSS 嵌套语法（`.hero { .base { ... } }` → `.hero .base { ... }`）
- 保持媒体查询不变（原生 CSS 支持）

---

### Task 8: 最终验证

**Files:**
- 所有已修改/创建的文件

**背景:** 验证所有修改正确，构建通过，HMR 正常工作。

- [ ] **Step 1: TypeScript 编译检查**

```bash
cd D:\AI_code_assistant\frontend
npx tsc -b
```

Expected: 无错误输出（命令退出码 0）

- [ ] **Step 2: ESLint 检查**

```bash
cd D:\AI_code_assistant\frontend
npm run lint
```

Expected: 无错误输出，或仅显示可忽略的警告

- [ ] **Step 3: 生产构建**

```bash
cd D:\AI_code_assistant\frontend
npm run build
```

Expected: `dist/` 目录生成，无构建错误

- [ ] **Step 4: 开发服务器启动测试**

```bash
cd D:\AI_code_assistant\frontend
npm run dev
```

在另一个终端窗口或浏览器中打开 `http://localhost:3000`：
- 页面正常加载，无白屏
- 修改任意 `.tsx` 文件并保存
- 观察 HMR 正常更新，无错误覆盖层（因为默认 overlay: true，如果有错误会显示）

- [ ] **Step 5: 验证 Tailwind 生效**

检查 `HomePage.tsx` 中的 `text-3xl font-bold text-primary-600` 类名是否正确渲染样式。

- [ ] **Step 6: 验证 ErrorBoundary**

临时在 `HomePage.tsx` 中添加 `throw new Error('test')`，保存后页面应显示 ErrorBoundary 的兜底 UI 而非白屏。测试完成后删除该错误。

---

## 验证清单

- [ ] `npm install` 成功，无 peer dependency 冲突
- [ ] `npx tsc -b` 无 TypeScript 错误
- [ ] `npm run lint` 无 ESLint 错误
- [ ] `npm run build` 成功生成 `dist/`
- [ ] `npm run dev` 启动无报错
- [ ] 修改代码后 HMR 正常，无白屏/卡退
- [ ] Tailwind 类名生效（文字大小、颜色等）
- [ ] ErrorBoundary 在故意抛出错误时显示兜底 UI
- [ ] `response.data` 正确解析（非 `response.data.data`）
- [ ] 401 响应触发路由跳转（无页面重载）

---

## 附录

### A. 回滚方案

如果实施过程中遇到不可解决的问题：

1. 保留原始 `package.json` 备份（Git 历史或手动复制）
2. 重新执行 Task 1 但使用原始 `package.json`
3. 恢复原始 `vite.config.ts`（含 `overlay: false`）
4. 恢复原始 `tsconfig.app.json`
5. 删除新增的 `tailwind.config.js`, `postcss.config.js`
6. 恢复原始 `src/` 下的所有文件

### B. 常见问题

**Q: `npm install` 时出现 peer dependency 冲突？**
A: 尝试添加 `--legacy-peer-deps` 标志，或手动调整冲突包的版本。

**Q: TypeScript 编译报错 "Cannot find module 'react'"？**
A: 确认 `@types/react` 和 `@types/react-dom` 版本与 `react` 版本匹配。

**Q: Tailwind 类名不生效？**
A: 检查 `tailwind.config.js` 的 `content` 配置是否包含所有源文件路径。

**Q: HMR 仍然导致白屏？**
A: 检查浏览器控制台是否有错误，确认 `vite.config.ts` 中没有 `hmr: { overlay: false }`。

---

> **计划完成时间估算:** 8 个 Task，约 40-60 分钟（含验证）  
> **计划文档版本:** v1.0  
> **生成时间:** 2026-05-15  
> **基于设计文档:** `docs/superpowers/specs/2026-05-15-fix-crashes-design.md`
