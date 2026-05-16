# D2-e 用户自有模型配置 — 实现计划

**Goal:** 改造 D2 AI 对话系统，支持用户配置自己的 API 接入（多组），对话时选择。

**Architecture:** 1 新表 ai_providers + 4 CRUD API + 改造 stream_chat 从 DB 读配置 + 前端设置页。

**Spec:** `docs/superpowers/specs/2026-05-16-d2e-provider-settings-design.md`

---

## Task 1: 数据库迁移

**File:** `backend/alembic/versions/xxxx_ai_providers.py`

- [ ] 生成：`conda run -n ai_code_assistant_env alembic revision -m "ai_providers"`
- [ ] 写入迁移（建 ai_providers 表 + ai_conversations 加 provider_id）
- [ ] 执行：`conda run -n ai_code_assistant_env alembic upgrade head`

---

## Task 2: 模型 + Schema + Router

**Files:** 
- `backend/app/models/ai_provider.py`
- `backend/app/routers/ai_provider.py`
- `backend/app/models/__init__.py` + `backend/app/main.py`

**API:**
```
GET    /api/v1/ai/providers       → list (api_key 脱敏)
POST   /api/v1/ai/providers       → create
PUT    /api/v1/ai/providers/{id}  → update
DELETE /api/v1/ai/providers/{id}  → delete
```

---

## Task 3: 改造 ai_service + ai_chat router

- `ai_chat.py`: `create_conversation` 新增 `provider_id` 参数，不传则查用户默认配置
- `ai_service.py`: `stream_chat` 从 `ai_providers` 表读配置替代 `settings.DEEPSEEK_*`

---

## Task 4: 清理 config

- `config.py`: 删除 `DEEPSEEK_API_KEY` / `DEEPSEEK_API_BASE`
- `backend/.env`: 删除对应行

---

## Task 5: 前端

- **AISettingsPage.tsx**: 配置列表 + 添加/编辑表单 + 设为默认
- **ProviderForm.tsx**: 弹窗表单组件
- **AIChatPage.tsx**: 新建对话时选择 provider
- **InlineChat.tsx**: 无需改动（用默认配置）
- **App.tsx**: 加路由 `/settings/ai` + Navbar 加设置入口

---

## Task 6: 验证

- 前端 `npm run build`
- 后端 `conda run -n ai_code_assistant_env python -c "from app.main import app; print(len(app.routes))"`
