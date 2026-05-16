# D2-e 用户自有模型配置 — 设计规格说明书

> 版本: v1.0 | 日期: 2026-05-16 | 状态: 待审核
> 关联: D2 AI 对话设计规格

---

## 一、概述

改造 D2 的 AI 对话系统：从「平台配置单一 DeepSeek 密钥」改为「每个用户可自行配置多组 API 接入（官方/中转），对话时选择使用哪个」。密钥存在后端数据库中，AI 调用始终走后端代理转发，不暴露密钥到前端。

---

## 二、数据模型

### 2.1 新增表

#### `ai_providers` — 用户 API 配置

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | |
| user_id | UUID | FK→users, NOT NULL | 所属用户 |
| name | VARCHAR(100) | NOT NULL | 配置名，如"DeepSeek 官方" |
| base_url | VARCHAR(500) | NOT NULL | API 地址，如 `https://api.deepseek.com/v1` |
| api_key | VARCHAR(500) | NOT NULL | 密钥（服务端存储） |
| model | VARCHAR(100) | NOT NULL | 模型名，如 `deepseek-chat` |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否默认配置 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

**约束**: UNIQUE(user_id, name)

### 2.2 修改表

#### `ai_conversations` — 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| provider_id | UUID | FK→ai_providers ON DELETE SET NULL, NULL |

---

## 三、后端

### 3.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `backend/alembic/versions/xxxx_ai_providers.py` |
| CREATE | `backend/app/models/ai_provider.py` |
| CREATE | `backend/app/routers/ai_provider.py` |  
| MODIFY | `backend/app/services/ai_service.py` |
| MODIFY | `backend/app/routers/ai_chat.py` |
| MODIFY | `backend/app/models/__init__.py` |
| MODIFY | `backend/app/main.py` |

### 3.2 API

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/ai/providers` | 是 | 用户所有 API 配置列表 |
| POST | `/api/v1/ai/providers` | 是 | 新增配置 `{name, base_url, api_key, model, is_default}` |
| PUT | `/api/v1/ai/providers/{id}` | 是 | 修改配置 |
| DELETE | `/api/v1/ai/providers/{id}` | 是 | 删除配置 |

**修改现有**:

`POST /api/v1/ai/conversations` → 新增可选参数 `provider_id`，不传则自动选用户的默认配置。

### 3.3 核心逻辑变更 (`ai_service.py`)

`stream_chat` 方法改造：

```python
async def stream_chat(self, conversation_id, user_content):
    # 1. 查会话 → 取 provider_id
    # 2. 如果 provider_id 为 NULL → 查用户默认配置
    # 3. 从 ai_providers 读 base_url / api_key / model
    # 4. 构建 System Prompt（用 KnowledgeNode 上下文）
    # 5. 构建消息历史
    # 6. 用读到的配置调 AI API（替代原来的 settings.DEEPSEEK_*）
    # 7. SSE 流式返回
```

---

## 四、前端

### 4.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `frontend/src/pages/AISettingsPage.tsx` |
| CREATE | `frontend/src/components/ProviderForm.tsx` |
| MODIFY | `frontend/src/pages/AIChatPage.tsx` |
| MODIFY | `frontend/src/components/InlineChat.tsx` |
| MODIFY | `frontend/src/App.tsx` |

### 4.2 页面

**AISettingsPage** (`/settings/ai`):

```
┌──────────────────────────────────────────────┐
│ AI 模型设置                                   │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │ ● DeepSeek 官方                          │ │
│ │   https://api.deepseek.com/v1            │ │
│ │   deepseek-chat                          │ │
│ │   sk-xxxx....xxxx                        │ │
│ │   [设为默认] [编辑] [删除]                │ │
│ └──────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────┐ │
│ │ ○ 硅基流动中转                            │ │
│ │   https://api.siliconflow.cn/v1          │ │
│ │   deepseek-ai/DeepSeek-V3                │ │
│ │   sk-xxxx....xxxx                        │ │
│ │   [设为默认] [编辑] [删除]                │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ [+ 添加新配置]                                │
└──────────────────────────────────────────────┘
```

**AIChatPage** 顶部新增模型选择下拉框，创建新对话时可指定 provider。

**InlineChat** — 知识图谱内嵌对话，自动使用默认配置创建会话。

---

## 五、数据流

```
用户创建对话 → 选 provider → POST /ai/conversations {provider_id}
  → 用户发消息 → POST /ai/conversations/{id}/stream
    → ai_service 读 provider (base_url + api_key + model)
    → httpx.stream(provider的配置) → SSE 转发
```

---

## 六、安全

| 措施 | 说明 |
|------|------|
| 密钥不出服务端 | api_key 仅在后端数据库和 AI API 之间传输 |
| 配置隔离 | 用户只能看到自己的 providers |
| 密码字段不返回 | GET /providers 返回时 api_key 只显示后 4 位 `sk-...xxxx` |

---

## 七、清理

移除 `config.py` 中的 `DEEPSEEK_API_KEY` / `DEEPSEEK_API_BASE` 配置项（不再需要平台级密钥）。删除 `backend/.env` 中的对应项。

---

> **审核检查点**: 确认 1 新表 + 4 配置 API + 流式改造 + 设置页。通过后进入实现计划。
