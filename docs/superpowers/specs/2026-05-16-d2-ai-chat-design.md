# D2 AI 教练对话 — 设计规格说明书

> 版本: v1.0 | 日期: 2026-05-16 | 状态: 待审核
> 关联: D1 知识图谱, `technical_spec.md`

---

## 一、概述

为算法学习平台接入 DeepSeek API，提供知识点讲解 AI 对话功能。支持多轮对话 + SSE 流式输出。入口：知识图谱详情页底部内嵌小窗 + 独立 `/chat` 对话页。

---

## 二、数据模型

### 2.1 表结构

#### `ai_conversations` — 对话会话

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | |
| user_id | UUID | FK→users, NOT NULL | |
| knowledge_node_id | UUID | FK→knowledge_nodes, NULL | 关联知识点 |
| title | VARCHAR(255) | NOT NULL | 会话标题 |
| ai_model | VARCHAR(50) | NOT NULL, DEFAULT 'deepseek' | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

#### `ai_messages` — 消息记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | |
| conversation_id | UUID | FK→ai_conversations ON DELETE CASCADE | |
| role | VARCHAR(20) | NOT NULL | user / assistant / system |
| content | TEXT | NOT NULL | 消息内容 |
| token_count | INTEGER | NULL | Token 消耗估算 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

---

## 三、后端

### 3.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `backend/alembic/versions/xxxx_ai_chat.py` |
| CREATE | `backend/app/models/ai_chat.py` |
| CREATE | `backend/app/schemas/ai_chat.py` |
| CREATE | `backend/app/services/ai_service.py` |
| CREATE | `backend/app/routers/ai_chat.py` |
| MODIFY | `backend/app/models/__init__.py` |
| MODIFY | `backend/app/main.py` |

### 3.2 API

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/ai/conversations` | 是 | 用户会话列表 |
| POST | `/api/v1/ai/conversations` | 是 | 创建新会话 `{knowledge_node_id?, title?}` |
| GET | `/api/v1/ai/conversations/{id}/messages` | 是 | 消息历史 |
| POST | `/api/v1/ai/conversations/{id}/stream` | 是 | SSE 流式发送+接收 `{content}` |
| DELETE | `/api/v1/ai/conversations/{id}` | 是 | 删除会话 |

### 3.3 核心逻辑 (`ai_service.py`)

**System Prompt 构建**：

```
你是算法竞赛教练助手，用中文回答。
用户正在学习知识点：{title}。
核心概念：{core_concept}。
请用清晰的步骤讲解，避免直接给出完整代码答案，引导学生自己思考。
```

**流式调用 DeepSeek**：

```python
async def stream_chat(conversation_id, user_message):
    # 1. 查会话 + 关联知识点
    # 2. 查历史消息（最近 10 条）
    # 3. 构建 messages = [system_prompt, ...history, user_message]
    # 4. httpx 流式请求 DeepSeek API (POST /v1/chat/completions, stream=True)
    # 5. async generator yield 每个 chunk
    # 6. 流结束后保存 assistant 消息到 ai_messages
```

**SSE 端点**：FastAPI `StreamingResponse` + `text/event-stream`

---

## 四、前端

### 4.1 文件

| 操作 | 文件 |
|------|------|
| CREATE | `frontend/src/pages/AIChatPage.tsx` |
| CREATE | `frontend/src/components/ChatMessage.tsx` |
| CREATE | `frontend/src/components/ChatInput.tsx` |
| CREATE | `frontend/src/components/InlineChat.tsx` |
| MODIFY | `frontend/src/pages/KnowledgeTreePage.tsx` |
| MODIFY | `frontend/src/stores/aiChatStore.ts` |
| MODIFY | `frontend/src/App.tsx` |
| MODIFY | `frontend/src/components/Navbar.tsx` |

### 4.2 布局

**独立对话页 `/chat`**：

```
┌──────────┬─────────────────────────┐
│ 会话列表  │ 聊天区                    │
│ (w-72)   │                         │
│          │  ┌─────────────────────┐ │
│ ■ 排序问题│  │ AI: 冒泡排序的核心思想  │ │
│   冒泡排序│  │ 是通过相邻元素比较...   │ │
│ ■ DP 入门 │  └─────────────────────┘ │
│ ■ 链表    │  ┌─────────────────────┐ │
│          │  │ 你: 能再详细点吗     │ │
│ [+ 新对话]│  └─────────────────────┘ │
│          │  ┌─────────────────────┐ │
│          │  │ [输入框]       [发送] │ │
│          │  └─────────────────────┘ │
└──────────┴─────────────────────────┘
```

**内嵌小窗**（知识图谱详情页底部）：

```
┌─────────────────────────────────┐
│ 💬 问 AI                    [×] │
│ ──────────────────────────────  │
│ AI: 你好，有什么关于冒泡排序的   │
│ 问题想问我？                     │
│ ──────────────────────────────  │
│ [输入框]                   [发送]│
└─────────────────────────────────┘
```

流式输出时，AI 消息实时逐字增长。

### 4.3 交互流程

1. 用户在知识图谱详情页点击「问 AI」→ 底部弹出内嵌小窗，自动创建关联该知识点的会话
2. 用户输入问题 → POST `/stream` → SSE 流式返回 → 前端实时渲染
3. 流结束 → 消息保存到后端
4. 独立对话页 `/chat`：左侧会话历史，点击切换 → 加载消息历史

---

## 五、错误处理

| 场景 | 处理 |
|------|------|
| DeepSeek API 不可达 | SSE 流中断，前端显示"AI 服务暂不可用" |
| Token 超限 | 截断历史消息到最近 10 条 |
| 知识节点不存在 | knowledge_node_id 为 NULL，用通用 System Prompt |
| 未登录 | 401 |

> **审核检查点**: 确认数据库 + API + 前端布局 + 流式方案。通过后进入实现计划。
