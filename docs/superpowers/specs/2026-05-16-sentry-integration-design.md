# Sentry 前后端错误监控集成 — 设计规格

> 日期: 2026-05-16  
> 关联问题: M10 (前端错误上报)

---

## 一、目标

为 AI Code Assistant 添加 Sentry 错误监控，覆盖前端渲染错误和后端 500 错误，使开发者在生产环境中可感知用户端异常。

---

## 二、环境前提

> ⚠️ **强制要求**: 所有 Python 相关操作（安装依赖、运行脚本、启动服务）必须在 `ai_code_assistant_env` conda 虚拟环境中执行。

- 激活命令: `conda activate ai_code_assistant_env`
- 验证命令: `conda info --envs`（查看 `*` 标记的当前环境）
- **严禁**将 Python 依赖安装到 `base` 环境
- 前端 `npm install` 不受此限制

---

## 三、依赖

### 新增

| 层 | 包 | 版本 | 说明 |
|----|-----|------|------|
| 前端 | `@sentry/react` | ^9.x | React ErrorBoundary 集成 + 自动捕获 |
| 后端 | `sentry-sdk[fastapi]` | ^2.x | FastAPI 中间件 + 自动 500 捕获 |

### 不新增

- 不做 source map 上传（需构建步骤 + CI）
- 不做 release tracking（需 CI 注入 commit SHA）
- Performance tracing 默认关闭（`traces_sample_rate: 0.0`）

---

## 四、环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SENTRY_DSN` | `""` (空=禁用) | 前后端共用 DSN |
| `SENTRY_ENVIRONMENT` | `"development"` | 环境标签 |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.0` | 性能采样率 |

---

## 五、前端变更

### 4.1 依赖安装

```bash
cd frontend && npm install @sentry/react
```

### 4.2 main.tsx — 初始化

在 React 渲染前调用 `Sentry.init()`：

```ts
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || "development",
  tracesSampleRate: Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE) || 0.0,
  integrations: [Sentry.browserTracingIntegration()],
})
```

### 4.3 ErrorBoundary.tsx — 上报

在 `componentDidCatch` 中增加 Sentry 调用（保留原有 console.error 和 fallback UI）：

```ts
componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
  console.error('ErrorBoundary caught error:', error, errorInfo)
  Sentry.captureException(error, { contexts: { react: errorInfo } })
}
```

### 4.4 .env.example

```
# ── 监控 ──
VITE_SENTRY_DSN=
VITE_SENTRY_ENVIRONMENT=development
VITE_SENTRY_TRACES_SAMPLE_RATE=0.0
```

### 4.5 docker-compose.yml — 前端服务 environment

```
SENTRY_DSN=${SENTRY_DSN:-}
SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT:-development}
```

---

## 六、后端变更

### 5.1 依赖安装

```bash
pip install sentry-sdk[fastapi]
```

并加入 `requirements.txt`。

### 5.2 config.py

```python
# Sentry
SENTRY_DSN: str = ""
SENTRY_ENVIRONMENT: str = "development"
```

### 5.3 main.py — 初始化

在 `app = FastAPI(...)` 之后、注册路由之前初始化：

```python
import sentry_sdk
from app.config import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=0.0,
)
```

### 5.4 .env.example

```
# ── 监控 ──
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

### 5.5 docker-compose.yml — 后端服务 environment

```
SENTRY_DSN=${SENTRY_DSN:-}
SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT:-development}
```

---

## 七、数据流

```
用户浏览器 ──(render error)──→ ErrorBoundary ──→ captureException() ──→ sentry.io
FastAPI    ──(500 error)────→ sentry-sdk middleware ────────────────→ sentry.io
```

DSN 为空时 Sentry SDK 自动静默禁用，无副作用。

---

## 八、验证方式

1. 前端：在页面故意抛一个 `throw new Error("test")`，确认 Sentry Issues 中出现
2. 后端：调用一个必然 500 的端点，确认上报
3. 不配置 DSN 时，应用行为不受影响（SDK noop）

---

## 九、不计入范围

- ❌ Performance tracing（性能采样）
- ❌ Source map 上传（错误堆栈可读性）
- ❌ Release tracking（版本关联）
- ❌ Session replay
