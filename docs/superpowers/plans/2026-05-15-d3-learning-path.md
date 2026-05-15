# D3 学习路径 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 5 条学习路线组织 D1 的 20 个知识点，支持用户加入路线、自由跳学、进度追踪。

**Architecture:** 3 张新表（learning_paths / path_nodes / path_progress），遵循现有四层模式（models→schemas→services→routers）。前端路线卡片列表 + 路线详情页（进度条 + 节点列表）。

**Tech Stack:** PostgreSQL, SQLAlchemy async, FastAPI, React + Zustand + Tailwind

**Spec:** `docs/superpowers/specs/2026-05-15-d3-learning-path-design.md`

**环境约束:** Python 命令使用 `conda activate ai_code_assistant_env` 或 `conda run -n ai_code_assistant_env`

---

## 文件清单

| 操作 | 文件 |
|------|------|
| CREATE | `backend/alembic/versions/xxxx_learning_path.py` |
| CREATE | `backend/app/models/learning_path.py` |
| CREATE | `backend/app/schemas/learning_path.py` |
| CREATE | `backend/app/services/learning_path_service.py` |
| CREATE | `backend/app/routers/learning_path.py` |
| CREATE | `backend/app/data_path_seed.py` |
| CREATE | `frontend/src/pages/LearningPathListPage.tsx` |
| CREATE | `frontend/src/pages/LearningPathDetailPage.tsx` |
| MODIFY | `backend/app/models/__init__.py` |
| MODIFY | `backend/app/main.py` |
| MODIFY | `frontend/src/App.tsx` |
| MODIFY | `frontend/src/components/Navbar.tsx` |

---

## Task 1: 数据库迁移

**Files:** `backend/alembic/versions/xxxx_learning_path.py`

- [ ] **Step 1: 生成空白迁移**

```bash
cd backend
conda run -n ai_code_assistant_env alembic revision -m "learning_path"
```

- [ ] **Step 2: 写入迁移内容**

```python
"""learning_path

Revision ID: xxxx
Revises: 7e9140efa2a3
Create Date: 2026-05-15

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'xxxx'
down_revision: Union[str, None] = '7e9140efa2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learning_paths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("estimated_days", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_learning_paths_category", "learning_paths", ["category"])

    op.create_table(
        "learning_path_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False),
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("path_id", "knowledge_node_id"),
    )
    op.create_index("idx_path_nodes_path", "learning_path_nodes", ["path_id", "order_index"])

    op.create_table(
        "learning_path_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("completed_nodes", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("total_nodes", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "path_id"),
    )


def downgrade() -> None:
    op.drop_table("learning_path_progress")
    op.drop_table("learning_path_nodes")
    op.drop_table("learning_paths")
```

- [ ] **Step 3: 执行迁移**

```bash
conda run -n ai_code_assistant_env alembic upgrade head
```

Expected: `Running upgrade 7e9140efa2a3 -> xxxx, learning_path`

---

## Task 2: SQLAlchemy 模型

**Files:** `backend/app/models/learning_path.py`, `backend/app/models/__init__.py`

- [ ] **Step 1: 创建模型文件**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, SmallInteger, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    title_slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    estimated_days = Column(Integer, nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"
    __table_args__ = (UniqueConstraint("path_id", "knowledge_node_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    knowledge_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LearningPathProgress(Base):
    __tablename__ = "learning_path_progress"
    __table_args__ = (UniqueConstraint("user_id", "path_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    status = Column(String(20), nullable=False, default="not_started")
    completed_nodes = Column(SmallInteger, nullable=False, default=0)
    total_nodes = Column(SmallInteger, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

- [ ] **Step 2: 更新 __init__.py**

在 `backend/app/models/__init__.py` 追加:

```python
from app.models.learning_path import LearningPath, LearningPathNode, LearningPathProgress
# 更新 __all__ 列表追加 "LearningPath", "LearningPathNode", "LearningPathProgress"
```

- [ ] **Step 3: 验证**

```bash
conda run -n ai_code_assistant_env python -c "from app.models.learning_path import LearningPath, LearningPathNode, LearningPathProgress; print('OK')"
```

---

## Task 3: Schemas + Service + Router

**Files:** 3 个新文件 + main.py 修改

### Schema

```python
# backend/app/schemas/learning_path.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class LearningPathBrief(BaseModel):
    id: UUID
    title: str
    title_slug: str
    category: str
    description: Optional[str] = None
    estimated_days: Optional[int] = None
    node_count: int = 0
    user_status: str = "not_started"
    user_progress_pct: int = 0

    class Config:
        from_attributes = True


class PathNodeItem(BaseModel):
    id: UUID
    knowledge_node_id: UUID
    title: str
    title_slug: str
    category: str
    level: int
    order_index: int
    is_required: bool
    user_status: str = "not_started"


class LearningPathDetail(BaseModel):
    path: LearningPathBrief
    nodes: list[PathNodeItem] = []


class EnrollResponse(BaseModel):
    path_id: UUID
    status: str
    total_nodes: int
```

### Service (`learning_path_service.py`)

核心方法:
- `list_paths(user_id=None)` — 查所有已发布路径，合并用户进度
- `get_path_detail(slug, user_id=None)` — 路径详情 + 节点列表（含每个节点的 user_progress）
- `enroll(user_id, path_slug)` — 加入路线，创建 progress 记录

### Router (`learning_path.py`)

```python
router = APIRouter(prefix="/api/v1/paths", tags=["学习路径"])

GET  /          → list_paths()
GET  /{slug}    → get_path_detail()
POST /{slug}/enroll  → enroll()
GET  /{slug}/progress → get_user_progress()
```

注册: `main.py` 添加 `app.include_router(learning_path.router)`

---

## Task 4: 种子数据

**Files:** `backend/app/data_path_seed.py`

5 条路线 + 节点关联:

```python
SEED_PATHS = [
    {"title_slug": "oi-junior", "title": "OI 入门路线 (CSP-J)", "category": "oi_junior",
     "description": "面向小学/初中竞赛入门，从零开始掌握基础算法和数据结构",
     "node_slugs": ["time-complexity","recursion-divide-conquer","stack-queue","linked-list",
                    "binary-tree","bubble-sort","selection-sort","insertion-sort","binary-search","greedy-intro"]},
    # ... 其余4条
]
```

插入逻辑: 按 slug 查 knowledge_nodes 获取 UUID，插入 learning_paths + learning_path_nodes。

- [ ] **Step 1: 运行种子**

```bash
conda run -n ai_code_assistant_env python -m app.data_path_seed
```

Expected: `Seeded 5 paths with XX nodes`

---

## Task 5: 前端页面

### LearningPathListPage.tsx

5 张路线卡片，3 列网格。每张卡片显示标题、描述、节点数、进度条（若已加入）。按钮「加入此路线」或「继续学习」。

### LearningPathDetailPage.tsx

节点列表（带 ○/◐/✅ 状态图标）+ 顶部进度条。每个节点可点击跳转到 `/knowledge/{slug}`。

### 路由 + 导航

```tsx
// App.tsx
<Route path="/paths" element={<LearningPathListPage />} />
<Route path="/paths/:slug" element={<LearningPathDetailPage />} />

// Navbar.tsx 添加
<Link to="/paths">学习路径</Link>
```

---

## Task 6: 验证

- [ ] **Step 1: 后端 API**

```bash
python -c "import httpx; r=httpx.get('http://127.0.0.1:8000/api/v1/paths',timeout=5); print(len(r.json()))"
# Expected: 5

python -c "import httpx; r=httpx.get('http://127.0.0.1:8000/api/v1/paths/oi-junior',timeout=5); d=r.json(); print(d['path']['title'], 'nodes:', len(d['nodes']))"
# Expected: OI 入门路线 (CSP-J) nodes: 10
```

- [ ] **Step 2: 前端构建**

```bash
cd frontend && npm run build
```

---

> **实现顺序:** Task 1→2→3→4→5→6。Task 3 包含 3 个后端文件可并行。
