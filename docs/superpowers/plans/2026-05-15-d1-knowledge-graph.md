# D1 知识图谱 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建算法知识图谱系统：ltree 树形存储 + REST API + 左侧目录树/右侧详情前端 + D3 关系图 + 用户学习进度。

**Architecture:** PostgreSQL ltree 物化路径存储知识树，FastAPI 四层架构 (models → schemas → services → routers)，React + Zustand + D3.js 前端，遵循项目现有模式。

**Tech Stack:** PostgreSQL 15 (ltree), SQLAlchemy async, FastAPI, React 18, TypeScript, Zustand, D3.js v7, Tailwind CSS

**环境约束:** 所有 python 命令必须在 `ai_code_assistant_env` 虚拟环境中执行: `conda activate ai_code_assistant_env` 或 `conda run -n ai_code_assistant_env python ...`

**Spec:** `docs/superpowers/specs/2026-05-15-d1-knowledge-graph-design.md`

---

## 文件清单

| 操作 | 文件 |
|------|------|
| CREATE | `backend/app/models/knowledge.py` |
| CREATE | `backend/app/schemas/knowledge.py` |
| CREATE | `backend/app/services/knowledge_service.py` |
| CREATE | `backend/app/routers/knowledge.py` |
| CREATE | `backend/app/data_seed.py` |
| CREATE | `backend/alembic/versions/xxxx_ltree_knowledge_graph.py` |
| CREATE | `frontend/src/pages/KnowledgeTreePage.tsx` |
| CREATE | `frontend/src/pages/KnowledgeGraphPage.tsx` |
| CREATE | `frontend/src/components/KnowledgeTree.tsx` |
| CREATE | `frontend/src/components/KnowledgeNeighborGraph.tsx` |
| MODIFY | `backend/app/routers/__init__.py` |
| MODIFY | `backend/app/main.py` |
| MODIFY | `frontend/src/App.tsx` |
| MODIFY | `frontend/src/components/Navbar.tsx` |
| MODIFY | `frontend/src/stores/knowledgeStore.ts` |

---

## Phase 1: 数据库

### Task 1: 生成 Alembic 迁移 (ltree + 4 表)

- [ ] **Step 1: 进入虚拟环境并生成迁移**

```bash
conda activate ai_code_assistant_env
cd backend
alembic revision --autogenerate -m "ltree_knowledge_graph"
```
Expected: 新文件生成在 `alembic/versions/`

- [ ] **Step 2: 编辑迁移文件，手动添加 ltree 扩展和表**

在 upgrade() 中添加:
```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")

    op.create_table(
        "knowledge_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_slug", sa.String(255), unique=True, nullable=False),
        sa.Column("path", None, nullable=False),  # ltree 列，sa 无原生类型，用 raw SQL
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("level", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("core_concept", sa.Text(), nullable=False),
        sa.Column("applicable_scenarios", sa.Text(), nullable=True),
        sa.Column("algorithm_steps", sa.Text(), nullable=True),
        sa.Column("code_template_cpp", sa.Text(), nullable=True),
        sa.Column("code_template_py", sa.Text(), nullable=True),
        sa.Column("code_template_java", sa.Text(), nullable=True),
        sa.Column("time_complexity", sa.String(100), nullable=True),
        sa.Column("space_complexity", sa.String(100), nullable=True),
        sa.Column("common_mistakes", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    # ltree 列手动添加（sqlalchemy 不支持 ltree 类型直接定义）
    op.execute("ALTER TABLE knowledge_nodes ADD COLUMN IF NOT EXISTS path ltree NOT NULL")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_nodes_path ON knowledge_nodes USING GIST (path)")
    op.create_index("idx_knowledge_nodes_category", "knowledge_nodes", ["category", "order_index"])
    op.create_index("idx_knowledge_nodes_published", "knowledge_nodes", ["is_published"])

    op.create_table(
        "knowledge_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("from_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("to_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("edge_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_knowledge_edges_from", "knowledge_edges", ["from_node_id", "edge_type"])
    op.create_index("idx_knowledge_edges_to", "knowledge_edges", ["to_node_id", "edge_type"])

    op.create_table(
        "knowledge_problem_associations",
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("difficulty_level", sa.SmallInteger(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("knowledge_node_id", "problem_id"),
    )

    op.create_table(
        "user_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("practice_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "knowledge_node_id"),
    )
    op.create_index("idx_user_progress_user", "user_progress", ["user_id", "status"])
    op.create_index("idx_user_progress_node", "user_progress", ["knowledge_node_id"])

def downgrade() -> None:
    op.drop_table("user_progress")
    op.drop_table("knowledge_problem_associations")
    op.drop_table("knowledge_edges")
    op.execute("DROP INDEX IF EXISTS idx_knowledge_nodes_path")
    op.drop_table("knowledge_nodes")
    op.execute("DROP EXTENSION IF EXISTS ltree")
```

- [ ] **Step 3: 执行迁移**

```bash
conda run -n ai_code_assistant_env alembic upgrade head
```
Expected: 输出 `INFO  [alembic.runtime.migration] Running upgrade ... -> xxxx, ltree_knowledge_graph`

---

### Task 2: SQLAlchemy 模型

- [ ] **Step 1: 创建 `backend/app/models/knowledge.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, SmallInteger, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    title_slug = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    level = Column(SmallInteger, nullable=False, default=1)
    description = Column(Text, nullable=False)
    core_concept = Column(Text, nullable=False)
    applicable_scenarios = Column(Text, nullable=True)
    algorithm_steps = Column(Text, nullable=True)
    code_template_cpp = Column(Text, nullable=True)
    code_template_py = Column(Text, nullable=True)
    code_template_java = Column(Text, nullable=True)
    time_complexity = Column(String(100), nullable=True)
    space_complexity = Column(String(100), nullable=True)
    common_mistakes = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, nullable=False, default=False)
    estimated_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ltree path 列在迁移中手工添加，模型中用 Column 占位
    path = Column(String(500), nullable=False)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    to_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    edge_type = Column(String(20), nullable=False)  # prerequisite / next / related
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    from_node = relationship("KnowledgeNode", foreign_keys=[from_node_id])
    to_node = relationship("KnowledgeNode", foreign_keys=[to_node_id])


class KnowledgeProblemAssociation(Base):
    __tablename__ = "knowledge_problem_associations"

    knowledge_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), primary_key=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True)
    difficulty_level = Column(SmallInteger, nullable=False, default=1)  # 1:入门 2:进阶 3:挑战
    order_index = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "knowledge_node_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    status = Column(String(20), nullable=False, default="not_started")  # not_started/in_progress/completed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    practice_count = Column(SmallInteger, nullable=False, default=0)
    last_practiced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

- [ ] **Step 2: 更新 `backend/app/models/__init__.py`**

```python
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, KnowledgeProblemAssociation, UserProgress
```

- [ ] **Step 3: 验证模型可导入**

```bash
conda run -n ai_code_assistant_env python -c "from app.models.knowledge import KnowledgeNode, KnowledgeEdge, KnowledgeProblemAssociation, UserProgress; print('OK')"
```
Expected: `OK`

---

## Phase 2: 后端业务逻辑

### Task 3: Pydantic Schemas

- [ ] **Step 1: 创建 `backend/app/schemas/knowledge.py`**

```python
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── 知识节点 ──

class KnowledgeNodeBrief(BaseModel):
    """树节点摘要（用于列表和嵌套）"""
    id: UUID
    title: str
    title_slug: str
    category: str
    level: int
    order_index: int

    class Config:
        from_attributes = True


class KnowledgeNodeTreeItem(KnowledgeNodeBrief):
    """树节点（含 children 和用户状态）"""
    user_status: str = "not_started"
    children: list["KnowledgeNodeTreeItem"] = []


class KnowledgeNodeDetail(BaseModel):
    """节点完整详情"""
    id: UUID
    title: str
    title_slug: str
    category: str
    level: int
    description: str
    core_concept: str
    applicable_scenarios: Optional[str] = None
    algorithm_steps: Optional[str] = None
    code_template_cpp: Optional[str] = None
    code_template_py: Optional[str] = None
    code_template_java: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    common_mistakes: Optional[str] = None
    estimated_minutes: Optional[int] = None
    order_index: int

    class Config:
        from_attributes = True


# ── 关联 ──

class KnowledgeNodeNeighbor(BaseModel):
    """邻居节点摘要"""
    id: UUID
    title: str
    title_slug: str
    edge_type: str  # prerequisite / next / related

    class Config:
        from_attributes = True


class ProblemAssociationItem(BaseModel):
    """关联题目摘要"""
    problem_id: UUID
    title: str
    title_slug: str
    difficulty: int
    difficulty_level: int  # 1:入门 2:进阶 3:挑战
    is_required: bool

    class Config:
        from_attributes = True


# ── 聚合响应 ──

class KnowledgeNodeDetailResponse(BaseModel):
    """节点详情完整响应"""
    node: KnowledgeNodeDetail
    prerequisites: list[KnowledgeNodeNeighbor] = []
    next_nodes: list[KnowledgeNodeNeighbor] = []
    related_nodes: list[KnowledgeNodeNeighbor] = []
    problems: list[ProblemAssociationItem] = []
    user_progress: Optional["UserProgressResponse"] = None


class KnowledgeTreeResponse(BaseModel):
    """知识树响应"""
    children: list[KnowledgeNodeTreeItem] = []


# ── 用户进度 ──

class UserProgressCreate(BaseModel):
    knowledge_node_id: UUID
    status: str = Field(..., pattern=r"^(in_progress|completed)$")


class UserProgressResponse(BaseModel):
    status: str
    practice_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProgressSummary(BaseModel):
    """进度总览"""
    total_nodes: int = 0
    completed_nodes: int = 0
    in_progress_nodes: int = 0
    items: list["UserProgressItem"] = []


class UserProgressItem(BaseModel):
    node_id: UUID
    node_title: str
    node_slug: str
    status: str
    practice_count: int

    class Config:
        from_attributes = True
```

---

### Task 4: KnowledgeService

- [ ] **Step 1: 创建 `backend/app/services/knowledge_service.py`**

```python
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, KnowledgeProblemAssociation, UserProgress
from app.models.problem import Problem
from app.schemas.knowledge import (
    KnowledgeNodeTreeItem, KnowledgeNodeDetailResponse, KnowledgeNodeDetail,
    KnowledgeNodeNeighbor, ProblemAssociationItem, UserProgressResponse,
    UserProgressSummary, UserProgressItem,
)


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── 树构建 ──

    async def get_tree(self, user_id: Optional[uuid.UUID] = None) -> list[KnowledgeNodeTreeItem]:
        """获取完整知识树，可选合并用户进度"""
        result = await self.db.execute(
            select(KnowledgeNode)
            .where(KnowledgeNode.is_published == True)
            .order_by(KnowledgeNode.category, KnowledgeNode.path)
        )
        nodes = result.scalars().all()

        # 获取用户进度（如果登录）
        user_progress_map = {}
        if user_id:
            progress_result = await self.db.execute(
                select(UserProgress).where(UserProgress.user_id == user_id)
            )
            for p in progress_result.scalars().all():
                user_progress_map[p.knowledge_node_id] = p.status

        # path → 层级映射: "sorting" → 根, "sorting.bubble" → 子
        id_map = {str(n.id): KnowledgeNodeTreeItem(
            id=n.id, title=n.title, title_slug=n.title_slug,
            category=n.category, level=n.level, order_index=n.order_index,
            user_status=user_progress_map.get(n.id, "not_started"),
            children=[]
        ) for n in nodes}

        roots = []
        for node in nodes:
            item = id_map[str(node.id)]
            path_parts = node.path.split(".")
            if len(path_parts) == 1:
                roots.append(item)
            else:
                # 找父节点：parent_path = path 去掉最后一段
                parent_path = ".".join(path_parts[:-1])
                parent = next((id_map[str(n.id)] for n in nodes if n.path == parent_path), None)
                if parent:
                    parent.children.append(item)

        # 按 order_index 排序
        for item in id_map.values():
            item.children.sort(key=lambda c: c.order_index)
        roots.sort(key=lambda r: r.order_index)

        return roots

    # ── 节点详情 ──

    async def get_node_detail(
        self, slug: str, user_id: Optional[uuid.UUID] = None
    ) -> Optional[KnowledgeNodeDetailResponse]:
        """获取节点完整详情 + 邻居 + 关联题目 + 用户进度"""
        result = await self.db.execute(
            select(KnowledgeNode).where(KnowledgeNode.title_slug == slug)
        )
        node = result.scalar_one_or_none()
        if not node:
            return None

        # 邻居（knowledge_edges）
        prerequisites = await self._get_neighbors(node.id, "prerequisite")
        next_nodes = await self._get_neighbors(node.id, "next", reverse=True)
        related = await self._get_neighbors(node.id, "related")
        related += await self._get_neighbors(node.id, "related", reverse=True)

        # 关联题目
        problems = await self._get_problems(node.id)

        # 用户进度
        user_progress = None
        if user_id:
            p_result = await self.db.execute(
                select(UserProgress).where(
                    UserProgress.user_id == user_id,
                    UserProgress.knowledge_node_id == node.id,
                )
            )
            p = p_result.scalar_one_or_none()
            if p:
                user_progress = UserProgressResponse(
                    status=p.status,
                    practice_count=p.practice_count,
                    started_at=p.started_at,
                    completed_at=p.completed_at,
                )

        return KnowledgeNodeDetailResponse(
            node=KnowledgeNodeDetail.model_validate(node),
            prerequisites=prerequisites,
            next_nodes=next_nodes,
            related_nodes=related,
            problems=problems,
            user_progress=user_progress,
        )

    async def _get_neighbors(
        self, node_id: uuid.UUID, edge_type: str, reverse: bool = False
    ) -> list[KnowledgeNodeNeighbor]:
        """获取邻居节点"""
        if reverse:
            stmt = (
                select(KnowledgeEdge, KnowledgeNode)
                .join(KnowledgeNode, KnowledgeEdge.from_node_id == KnowledgeNode.id)
                .where(KnowledgeEdge.to_node_id == node_id, KnowledgeEdge.edge_type == edge_type)
            )
        else:
            stmt = (
                select(KnowledgeEdge, KnowledgeNode)
                .join(KnowledgeNode, KnowledgeEdge.to_node_id == KnowledgeNode.id)
                .where(KnowledgeEdge.from_node_id == node_id, KnowledgeEdge.edge_type == edge_type)
            )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            KnowledgeNodeNeighbor(
                id=n.id, title=n.title, title_slug=n.title_slug, edge_type=edge.edge_type
            )
            for edge, n in rows
        ]

    async def _get_problems(self, node_id: uuid.UUID) -> list[ProblemAssociationItem]:
        """获取关联题目"""
        result = await self.db.execute(
            select(KnowledgeProblemAssociation, Problem)
            .join(Problem, KnowledgeProblemAssociation.problem_id == Problem.id)
            .where(KnowledgeProblemAssociation.knowledge_node_id == node_id)
            .order_by(KnowledgeProblemAssociation.order_index)
        )
        rows = result.all()
        return [
            ProblemAssociationItem(
                problem_id=p.id,
                title=p.title,
                title_slug=p.title_slug,
                difficulty=p.difficulty,
                difficulty_level=assoc.difficulty_level,
                is_required=assoc.is_required,
            )
            for assoc, p in rows
        ]

    # ── 进度 ──

    async def upsert_progress(
        self, user_id: uuid.UUID, knowledge_node_id: uuid.UUID, status: str
    ) -> UserProgress:
        """更新或创建用户进度"""
        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user_id,
                UserProgress.knowledge_node_id == knowledge_node_id,
            )
        )
        progress = result.scalar_one_or_none()

        now = datetime.utcnow()
        if progress:
            progress.status = status
            progress.updated_at = now
            if status == "in_progress" and not progress.started_at:
                progress.started_at = now
            if status == "completed":
                progress.completed_at = now
            progress.practice_count += 1
            progress.last_practiced_at = now
        else:
            progress = UserProgress(
                user_id=user_id,
                knowledge_node_id=knowledge_node_id,
                status=status,
                started_at=now if status == "in_progress" else None,
                completed_at=now if status == "completed" else None,
                practice_count=1,
                last_practiced_at=now,
            )
            self.db.add(progress)

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def get_user_progress_summary(self, user_id: uuid.UUID) -> UserProgressSummary:
        """获取用户学习进度总览"""
        # 总节点数
        total_result = await self.db.execute(
            select(KnowledgeNode).where(KnowledgeNode.is_published == True)
        )
        total_nodes = len(total_result.scalars().all())

        # 用户进度
        result = await self.db.execute(
            select(UserProgress, KnowledgeNode)
            .join(KnowledgeNode, UserProgress.knowledge_node_id == KnowledgeNode.id)
            .where(UserProgress.user_id == user_id)
            .order_by(KnowledgeNode.category, KnowledgeNode.path)
        )
        rows = result.all()

        completed = sum(1 for p, _ in rows if p.status == "completed")
        in_progress = sum(1 for p, _ in rows if p.status == "in_progress")
        items = [
            UserProgressItem(
                node_id=p.knowledge_node_id,
                node_title=n.title,
                node_slug=n.title_slug,
                status=p.status,
                practice_count=p.practice_count,
            )
            for p, n in rows
        ]

        return UserProgressSummary(
            total_nodes=total_nodes,
            completed_nodes=completed,
            in_progress_nodes=in_progress,
            items=items,
        )
```

---

### Task 5: Knowledge Router

- [ ] **Step 1: 创建 `backend/app/routers/knowledge.py`**

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.rate_limit import limiter
from app.schemas.knowledge import (
    KnowledgeTreeResponse, KnowledgeNodeDetailResponse,
    UserProgressCreate, UserProgressResponse, UserProgressSummary,
)
from app.services.knowledge_service import KnowledgeService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识图谱"])


@router.get("/tree", response_model=KnowledgeTreeResponse)
@limiter.limit("30/minute")
async def get_tree(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_safe),
):
    """获取知识树"""
    service = KnowledgeService(db)
    user_id = current_user.id if current_user else None
    children = await service.get_tree(user_id)
    return KnowledgeTreeResponse(children=children)


@router.get("/nodes/{slug}", response_model=KnowledgeNodeDetailResponse)
@limiter.limit("30/minute")
async def get_node(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_safe),
):
    """获取节点详情"""
    service = KnowledgeService(db)
    user_id = current_user.id if current_user else None
    detail = await service.get_node_detail(slug, user_id)
    if not detail:
        raise HTTPException(status_code=404, detail="知识点未找到")
    return detail


@router.post("/progress", response_model=UserProgressResponse)
@limiter.limit("20/minute")
async def update_progress(
    data: UserProgressCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """更新学习进度"""
    service = KnowledgeService(db)
    progress = await service.upsert_progress(current_user.id, data.knowledge_node_id, data.status)
    return UserProgressResponse(
        status=progress.status,
        practice_count=progress.practice_count,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
    )


@router.get("/progress", response_model=UserProgressSummary)
@limiter.limit("20/minute")
async def get_progress(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取用户进度总览"""
    service = KnowledgeService(db)
    return await service.get_user_progress_summary(current_user.id)
```

**注意**: 需要 `get_current_user_safe` 依赖——一个不强制登录的版本。在 `app/utils/security.py` 末尾添加:

```python
async def get_current_user_safe(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户（可选登录）"""
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    from app.models.user import User
    from uuid import UUID as _UUID
    result = await db.execute(select(User).where(User.id == _UUID(user_id)))
    return result.scalar_one_or_none()
```

- [ ] **Step 2: 更新 `backend/app/routers/__init__.py`**

```python
from app.routers import auth, tags, problems, knowledge
```

- [ ] **Step 3: 更新 `backend/app/main.py`，注册路由**

在 router 注册区添加:
```python
app.include_router(knowledge.router)
```

- [ ] **Step 4: 验证路由注册**

```bash
conda run -n ai_code_assistant_env python -c "from app.main import app; print(len(app.routes))"
```
Expected: 路由数量增加（比之前多 5 个知识图谱端点）

---

## Phase 3: 种子数据

### Task 6: 种子数据生成

- [ ] **Step 1: 创建 `backend/app/data_seed.py`**

文件内容为 20 个知识点的完整数据（含 title / slug / path / description / core_concept / algorithm_steps / code_templates / time_complexity / common_mistakes）。知识点列表见设计文档第四节。

核心插入逻辑:

```python
import asyncio
from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeNode, KnowledgeEdge

SEED_NODES = [
    {
        "title": "时间复杂度分析",
        "title_slug": "time-complexity",
        "path": "basics.time_complexity",
        "category": "基础",
        "level": 1,
        "description": "...",
        "core_concept": "...",
        "code_template_cpp": "...",
        "code_template_py": "...",
        "time_complexity": "O(1) ~ O(n!)",
        "common_mistakes": "...",
        "order_index": 1,
    },
    # ... 其余 19 个
]

SEED_EDGES = [
    # (from_slug, to_slug, edge_type)
    ("time-complexity", "bubble-sort", "prerequisite"),
    ("bubble-sort", "selection-sort", "next"),
    ("bubble-sort", "insertion-sort", "next"),
    ("insertion-sort", "quick-sort", "next"),
    ("quick-sort", "merge-sort", "next"),
    ("binary-search", "dfs", "related"),
    ("stack-queue", "bfs", "prerequisite"),
    ("recursion", "dp-intro", "prerequisite"),
    ("dp-intro", "knapsack", "next"),
    ("dp-intro", "lcs", "next"),
    ("greedy-intro", "interval-scheduling", "next"),
    ("dijkstra", "bfs", "related"),
    # ... 完整边列表
]

async def seed():
    async with AsyncSessionLocal() as db:
        # 插入节点
        slug_map = {}
        for data in SEED_NODES:
            node = KnowledgeNode(**data, is_published=True)
            db.add(node)
            slug_map[data["title_slug"]] = node

        await db.flush()

        # 插入边
        for from_slug, to_slug, edge_type in SEED_EDGES:
            edge = KnowledgeEdge(
                from_node_id=slug_map[from_slug].id,
                to_node_id=slug_map[to_slug].id,
                edge_type=edge_type,
            )
            db.add(edge)

        await db.commit()
        print(f"Seeded {len(SEED_NODES)} nodes and {len(SEED_EDGES)} edges")

if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 2: 运行种子脚本**

```bash
conda run -n ai_code_assistant_env python -m app.data_seed
```
Expected: `Seeded 20 nodes and XX edges`

---

## Phase 4: 前端

### Task 7: 完善 knowledgeStore

- [ ] **Step 1: 重写 `frontend/src/stores/knowledgeStore.ts`**，对照设计文档 API

补全 `fetchTree`, `fetchNode`, `updateProgress`, `fetchProgress` actions，使用 `api` 实例（已有 Token 和 401 处理）。

### Task 8: KnowledgeTree 组件

- [ ] **Step 1: 创建 `frontend/src/components/KnowledgeTree.tsx`**

递归组件，渲染 `KnowledgeNodeTreeItem[]`：
- 展开/折叠箭头
- 状态图标（○ not_started / ◐ in_progress / ● completed）
- 点击选中，调用 `onSelect(slug)`

```tsx
import { useState } from 'react'
import type { KnowledgeNodeTreeItem } from '../stores/knowledgeStore'

interface Props {
  items: KnowledgeNodeTreeItem[]
  selectedSlug: string | null
  onSelect: (slug: string) => void
  level?: number
}

export default function KnowledgeTree({ items, selectedSlug, onSelect, level = 0 }: Props) {
  return (
    <ul className={`${level > 0 ? 'ml-4' : ''}`}>
      {items.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          isSelected={item.title_slug === selectedSlug}
          onSelect={onSelect}
          level={level}
        />
      ))}
    </ul>
  )
}
```

### Task 9: KnowledgeTreePage 主页面

- [ ] **Step 1: 创建 `frontend/src/pages/KnowledgeTreePage.tsx`**

布局: 左侧 `w-80` 树组件 + 右侧 `flex-1` 详情面板（Tab: 讲解/题集/关联知识）。

详情面板:
- 讲解 Tab: Markdown 渲染 + 代码模板（语言切换）
- 题集 Tab: 题目卡片列表 + 难度标签 + 必做标记
- 关联知识 Tab: 前置/后续/相关知识链接 + 迷你 D3 图

"标记完成"按钮调用 `updateProgress()`。

### Task 10: 路由 + 导航

- [ ] **Step 1: 更新 `frontend/src/App.tsx`**

```tsx
import KnowledgeTreePage from './pages/KnowledgeTreePage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage'

// 在 <Route element={<Layout />}> 内添加：
<Route path="/knowledge" element={<KnowledgeTreePage />} />
<Route path="/knowledge/graph" element={<KnowledgeGraphPage />} />
```

- [ ] **Step 2: 更新 `frontend/src/components/Navbar.tsx`**

添加导航链接: `<Link to="/knowledge">知识图谱</Link>`

---

### Task 11: KnowledgeGraphPage 全图（D3）

- [ ] **Step 1: 安装 d3**

```bash
npm install d3 @types/d3
```

- [ ] **Step 2: 创建 `frontend/src/pages/KnowledgeGraphPage.tsx`**

D3 力导向图：
- API `GET /api/v1/knowledge/tree` 获取节点列表
- API `GET /api/v1/knowledge/nodes/{slug}` 获取边（对每个节点查邻居）
- d3.forceSimulation 布局
- 点击节点弹出 tooltip

- [ ] **Step 3: 创建 `frontend/src/components/KnowledgeNeighborGraph.tsx`**

迷你版 D3 图（width=300, height=200），用于详情页"关联知识" Tab。

---

## Phase 5: 验证

### Task 12: 端到端验证

- [ ] **Step 1: 验证后端 API**

```bash
# 启动服务
conda activate ai_code_assistant_env
uvicorn app.main:app --port 8000 &

# 测试知识树
curl http://localhost:8000/api/v1/knowledge/tree | python -m json.tool

# 测试节点详情
curl http://localhost:8000/api/v1/knowledge/nodes/bubble-sort | python -m json.tool

# 测试进度更新（需先登录获取 token）
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

NODE_ID=$(curl -s http://localhost:8000/api/v1/knowledge/tree | python -c "import sys,json; print(json.load(sys.stdin)['children'][0]['id'])")

curl -X POST http://localhost:8000/api/v1/knowledge/progress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"knowledge_node_id\": \"$NODE_ID\", \"status\": \"in_progress\"}"
```

- [ ] **Step 2: 前端构建验证**

```bash
cd frontend
npm run build
```
Expected: Build 成功，无 TS 错误。

---

> **实现顺序**: Phase 1 → 2 → 3 → 4 → 5。Phase 1-2 可按 Task 粒度顺序执行，Phase 4 中 Task 7-10 可并行。
>
> **总规约**: 每次 Python 命令前确认虚拟环境已激活。不跨越 Phase 边界（下一 Phase 依赖上一 Phase 的产出）。
