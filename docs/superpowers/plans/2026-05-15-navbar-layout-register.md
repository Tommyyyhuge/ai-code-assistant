# 导航栏 + 布局框架 + 注册页实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建前端基础骨架：顶部导航栏、页面布局容器、注册页面

**Architecture:** 新增 Layout 组件包裹所有页面（Navbar + Outlet），Navbar 从 authStore 读取认证状态动态渲染，RegisterPage 复用现有 LoginPage 布局风格。

**Tech Stack:** React 18 + TypeScript 5.8 + Tailwind CSS 3 + React Router 6 + Zustand + Lucide React

**Design Doc:** `docs/superpowers/specs/2026-05-15-navbar-layout-register-design.md`

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `src/components/Layout.tsx` | 创建 | 页面布局容器（Navbar + 主内容区） |
| `src/components/Navbar.tsx` | 创建 | 顶部导航栏（Logo + 链接 + 用户状态） |
| `src/pages/RegisterPage.tsx` | 创建 | 注册页面（表单 + 提交） |
| `src/App.tsx` | 修改 | 添加 Layout 包裹 + 注册路由 |
| `src/components/LoginForm.tsx` | 修改 | 添加 "去注册" 链接 |

---

### Task 1: 创建 Layout 组件

**Files:**
- Create: `frontend/src/components/Layout.tsx`

**背景:** Layout 是所有页面的统一容器，包含顶部 Navbar 和下方主内容区域。

- [ ] **Step 1: 创建 Layout.tsx**

创建文件 `frontend/src/components/Layout.tsx`：

```typescript
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
```

- [ ] **Step 2: 验证文件创建**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\Layout.tsx
```

Expected: `True`

---

### Task 2: 创建 Navbar 组件

**Files:**
- Create: `frontend/src/components/Navbar.tsx`

**背景:** Navbar 显示在页面顶部，包含 Logo、导航链接、用户认证状态。

- [ ] **Step 1: 创建 Navbar.tsx**

创建文件 `frontend/src/components/Navbar.tsx`：

```typescript
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { User, LogOut, Code2 } from 'lucide-react'
import { useState } from 'react'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore()
  const navigate = useNavigate()
  const [showDropdown, setShowDropdown] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 text-xl font-bold text-blue-600">
            <Code2 className="w-6 h-6" />
            <span>AI_code_assisstant</span>
          </Link>

          {/* 中间导航链接 */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              首页
            </Link>
            <Link to="/problems" className="text-gray-700 hover:text-blue-600 transition-colors">
              题目列表
            </Link>
          </div>

          {/* 右侧用户区域 */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <User className="w-5 h-5" />
                  <span>{user.username}</span>
                </button>

                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
                      {user.email}
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>退出登录</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-blue-600 transition-colors"
                >
                  登录
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  注册
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
```

- [ ] **Step 2: 验证文件创建**

```bash
Test-Path D:\AI_code_assistant\frontend\src\components\Navbar.tsx
```

Expected: `True`

---

### Task 3: 修改 App.tsx 添加 Layout 和注册路由

**Files:**
- Modify: `frontend/src/App.tsx`

**背景:** 当前 App.tsx 直接渲染 Routes，需要改为用 Layout 包裹，并添加 /register 路由。

- [ ] **Step 1: 读取当前 App.tsx**

```bash
cat D:\AI_code_assistant\frontend\src\App.tsx
```

当前内容：
```typescript
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  )
}

export default App
```

- [ ] **Step 2: 修改 App.tsx**

替换为：

```typescript
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/problems" element={<div className="text-center text-gray-500">题目列表页（开发中）</div>} />
      </Route>
    </Routes>
  )
}

export default App
```

**变更说明：**
- 删除外层 `<div className="min-h-screen">`
- 添加 `<Route element={<Layout />}>` 包裹所有页面
- 添加 `/register` 路由
- 添加 `/problems` 占位路由

---

### Task 4: 创建 RegisterPage

**Files:**
- Create: `frontend/src/pages/RegisterPage.tsx`

**背景:** 注册页面，包含用户名、邮箱、密码、确认密码表单。

- [ ] **Step 1: 创建 RegisterPage.tsx**

创建文件 `frontend/src/pages/RegisterPage.tsx`：

```typescript
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useNavigate, Link } from 'react-router-dom'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [localError, setLocalError] = useState('')
  const { register, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError('')

    if (password !== confirmPassword) {
      setLocalError('两次输入的密码不一致')
      return
    }

    if (username.length < 3 || username.length > 50) {
      setLocalError('用户名长度需在 3-50 个字符之间')
      return
    }

    if (password.length < 8) {
      setLocalError('密码长度至少为 8 位')
      return
    }

    try {
      await register(username, email, password)
      navigate('/')
    } catch (err: unknown) {
      let message = '注册失败'
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } }
        message = axiosError.response?.data?.detail || message
      } else if (err instanceof Error) {
        message = err.message
      }
      setLocalError(message)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          创建账号
        </h2>
        <p className="mt-2 text-center text-gray-500">注册开始使用 AI_code_assisstant</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {localError && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded">
              {localError}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              用户名
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={3}
              maxLength={50}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              邮箱
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={8}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              确认密码
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isLoading ? '注册中...' : '注册'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          已有账号？{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            去登录
          </Link>
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证文件创建**

```bash
Test-Path D:\AI_code_assistant\frontend\src\pages\RegisterPage.tsx
```

Expected: `True`

---

### Task 5: 修改 LoginForm 添加注册链接

**Files:**
- Modify: `frontend/src/components/LoginForm.tsx`

**背景:** 在登录表单底部添加 "还没有账号？去注册" 链接。

- [ ] **Step 1: 读取当前 LoginForm.tsx**

确认当前文件结尾部分（最后 10 行左右）。

- [ ] **Step 2: 添加注册链接**

在 `LoginForm.tsx` 的 `return` 语句中，在 `</form>` 结束标签之前添加：

```tsx
        <p className="mt-4 text-center text-sm text-gray-600">
          还没有账号？{' '}
          <Link to="/register" className="text-blue-600 hover:underline">
            去注册
          </Link>
        </p>
```

同时需要在文件顶部添加 `Link` 导入：

```typescript
import { useNavigate, Link } from 'react-router-dom'
```

- [ ] **Step 3: 验证修改**

确认 LoginForm.tsx 现在包含：
- `import { useNavigate, Link } from 'react-router-dom'`
- 表单底部有 "还没有账号？去注册" 链接

---

### Task 6: 修改 HomePage 移除多余 padding

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx`

**背景:** 由于 Layout 已经添加了 `container mx-auto px-4 py-8` 的 padding，HomePage 自身的 `p-8` 会导致双重 padding。

- [ ] **Step 1: 修改 HomePage.tsx**

将：
```tsx
<div className="p-8">
```

改为：
```tsx
<div>
```

---

### Task 7: 验证构建

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

Expected: 无错误输出（0 errors）

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
- [ ] 访问 `http://localhost:3000` — 看到首页 + 顶部导航栏
- [ ] 点击 "注册" 按钮 — 跳转到注册页面
- [ ] 注册页面表单显示正常（用户名、邮箱、密码、确认密码）
- [ ] 点击 "去登录" 链接 — 跳回登录页面
- [ ] 登录页面底部有 "还没有账号？去注册" 链接
- [ ] 点击 Logo — 返回首页

---

## 自检清单

### 规格覆盖

| 设计需求 | 对应 Task |
|---|---|
| 顶部导航栏 | Task 2 (Navbar.tsx) |
| 页面布局容器 | Task 1 (Layout.tsx) |
| 注册页面 | Task 4 (RegisterPage.tsx) |
| 路由集成 | Task 3 (App.tsx) |
| 登录/注册互链 | Task 5 (LoginForm.tsx) |

### 占位符扫描

- [x] 无 TBD/TODO/placeholder
- [x] 所有步骤包含完整代码
- [x] 无 "Add appropriate error handling" 等模糊描述

### 类型一致性

- [x] `useAuthStore` 在 Navbar 和 RegisterPage 中使用一致
- [x] `register` 方法签名与 authStore 中定义一致 `(username, email, password)`
- [x] 路由路径 `/register` 在 App.tsx 和 LoginForm.tsx Link 中一致

---

## 附录

### 可能遇到的问题

**Q: `lucide-react` 图标不显示？**
A: 确认 `lucide-react` 已安装（重构时已在 package.json 中）。

**Q: 点击下拉菜单外部不关闭？**
A: 当前版本使用简单 state 控制，如需点击外部关闭，后续可添加 `useEffect` + `useRef` 实现。

**Q: Navbar 在移动端显示异常？**
A: 当前版本未实现移动端汉堡菜单（按设计文档留到后续迭代）。

---

> **计划完成时间估算:** 7 个 Task，约 30-40 分钟  
> **计划文档版本:** v1.0  
> **生成时间:** 2026-05-15  
> **基于设计文档:** `docs/superpowers/specs/2026-05-15-navbar-layout-register-design.md`
