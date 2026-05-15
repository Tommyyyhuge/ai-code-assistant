# 导航栏 + 布局框架 + 注册页设计文档

> **文档类型**: 设计规格 (Design Spec)  
> **日期**: 2026-05-15  
> **主题**: 前端基础骨架搭建  
> **版本**: v1.0  
> **状态**: 已批准

---

## 1. 背景

前端重构已完成（React 18 + Vite 5 + TypeScript 5.8），当前仅有首页和登录页两个页面，缺少整体布局框架和注册功能。需要搭建基础骨架，为后续功能开发提供统一的页面容器和导航入口。

---

## 2. 目标

搭建前端基础骨架，包括：
1. **顶部导航栏（Navbar）** — 统一的顶部导航，包含 Logo、页面链接、用户认证状态
2. **布局框架（Layout）** — 页面布局容器，包裹所有页面内容
3. **注册页面（RegisterPage）** — 用户注册功能，与现有登录页配套

---

## 3. 设计决策

### 3.1 导航栏内容（基础版）

| 位置 | 内容 | 说明 |
|---|---|---|
| 左侧 | Logo | 点击返回首页 |
| 中间 | 首页、题目列表 | 核心页面入口 |
| 右侧 | 未登录：登录/注册按钮 | 引导用户认证 |
| 右侧 | 已登录：用户名 + 下拉菜单 | 个人中心、退出登录 |

### 3.2 布局结构

采用**顶部固定导航 + 主内容区**的经典布局：

```
┌─────────────────────────────────────────┐
│  Navbar (fixed top)                     │
├─────────────────────────────────────────┤
│                                         │
│  Main Content (Router Outlet)           │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 注册页表单字段

| 字段 | 类型 | 验证规则 |
|---|---|---|
| 用户名 | text | 3-50字符 |
| 邮箱 | email | 标准邮箱格式 |
| 密码 | password | 最少8位 |
| 确认密码 | password | 与密码一致 |

---

## 4. 文件变更

### 4.1 新增文件

| 文件 | 职责 |
|---|---|
| `src/components/Navbar.tsx` | 顶部导航栏组件，响应式用户信息展示 |
| `src/components/Layout.tsx` | 页面布局容器，包含 Navbar + Outlet |
| `src/pages/RegisterPage.tsx` | 注册页面，表单 + 提交逻辑 |

### 4.2 修改文件

| 文件 | 变更 |
|---|---|
| `src/App.tsx` | 用 Layout 包裹路由，添加 `/register` 路由 |
| `src/components/LoginForm.tsx` | 添加 "去注册" 链接 |

---

## 5. 路由结构

```
/           → HomePage
/login      → LoginPage
/register   → RegisterPage（新增）
/problems   → 题目列表页（占位，后续实现）
```

---

## 6. 组件设计

### 6.1 Navbar 组件

```typescript
// Props: 无（从 authStore 读取状态）
// 功能：
// - 显示 Logo 和导航链接
// - 根据 authStore.isAuthenticated 显示不同右侧内容
// - 已登录：显示用户名，点击打开下拉菜单（个人中心、退出）
// - 未登录：显示登录/注册按钮
```

### 6.2 Layout 组件

```typescript
// Props: children（或直接使用 Outlet）
// 功能：
// - 渲染 Navbar
// - 渲染主内容区域（children/Outlet）
// - 可选：添加 Footer
```

### 6.3 RegisterPage 组件

```typescript
// 功能：
// - 注册表单（用户名、邮箱、密码、确认密码）
// - 表单提交调用 authStore.register
// - 注册成功后自动登录并跳转首页
// - 显示注册错误信息
// - 提供 "已有账号？去登录" 链接
```

---

## 7. 数据流

```
用户点击注册
    ↓
RegisterPage 表单提交
    ↓
authStore.register(username, email, password)
    ↓
API POST /auth/register
    ↓
API POST /auth/login（自动登录）
    ↓
authStore 设置 isAuthenticated = true
    ↓
Navbar 检测到登录状态变化，显示用户信息
    ↓
页面跳转到首页
```

---

## 8. 不在本次范围内

以下功能留给后续迭代：

- 移动端汉堡菜单（响应式折叠）
- 表单实时验证提示（当前仅提交时验证）
- 路由守卫（未登录跳转登录页）
- 用户头像上传
- 题目列表页实际内容（仅导航占位）
- 用户下拉菜单中的个人中心页面

---

## 9. 依赖

- 现有依赖已足够（React, React Router, Tailwind, Zustand, Lucide React）
- 无需新增依赖

---

> **文档结束**  
> 本设计文档记录了导航栏 + 布局框架 + 注册页的设计决策  
> 基于用户确认的方案 A（最小可行版本）
