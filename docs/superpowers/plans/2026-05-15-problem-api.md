# 题目 API + 标签体系实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现后端题目 CRUD API 和标签体系，包括数据模型、数据库迁移、Service 层、API 路由和筛选分页，使前端能够切换至真实数据。

**Architecture:** 采用传统分层扩展，在现有 FastAPI + SQLAlchemy 架构下新增 models/schemas/services/routers 模块。题目与标签通过关联表实现多对多关系。筛选逻辑在 Service 层动态构建 SQLAlchemy 查询。

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Alembic, Pydantic, pytest

---

## 文件结构

### 新建文件

| 文件 | 职责 |
|------|------|
| `backend/app/models/problem.py` | Problem SQLAlchemy 模型 |
| `backend/app/models/tag.py` | Tag SQLAlchemy 模型（树状结构） |
| `backend/app/models/problem_tag_association.py` | 多对多关联表模型 |
| `backend/app/schemas/problem.py` | Problem Pydantic Schema |
| `backend/app/schemas/tag.py` | Tag Pydantic Schema |
| `backend/app/services/problem_service.py` | 题目业务逻辑（CRUD + 筛选分页） |
| `backend/app/services/tag_service.py` | 标签业务逻辑 |
| `backend/app/routers/problems.py` | 题目 API 路由 |
| `backend/app/routers/tags.py` | 标签 API 路由 |
| `backend/alembic/versions/20260515_add_problems_and_tags.py` | 数据库迁移 |
| `backend/tests/test_problems.py` | 题目 API 测试 |
| `backend/tests/test_tags.py` | 标签 API 测试 |

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `backend/app/models/__init__.py` | 导出 Problem, Tag, ProblemTagAssociation |
| `backend/app/schemas/__init__.py` | 导出 Problem 和 Tag schemas |
| `backend/app/routers/__init__.py` | 导出 problems 和 tags routers |
| `backend/app/services/__init__.py` | 导出 ProblemService, TagService |
| `backend/app/main.py` | 注册 /problems 和 /tags 路由 |

---

## Task 1: 数据库迁移脚本

**Files:**
- Create: `backend/alembic/versions/20260515_add_problems_and_tags.py`

**依赖:** 无（基于现有 users 表迁移）

- [ ] **Step 1: 创建迁移脚本**

创建文件 `backend/alembic/versions/20260515_add_problems_and_tags.py`：

```python
"""add problems and tags tables

Revision ID: 20260515_add_problems_and_tags
Revises: a88ab1bf29d6
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260515_add_problems_and_tags'
down_revision: Union[str, None] = 'a88ab1bf29d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 tags 表
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_slug', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_lanqiao_special', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('name_slug'),
        sa.ForeignKeyConstraint(['parent_id'], ['tags.id'], ondelete='SET NULL')
    )
    op.create_index('idx_tags_category', 'tags', ['category'])
    op.create_index('idx_tags_parent', 'tags', ['parent_id'])

    # 创建 problems 表
    op.create_table(
        'problems',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('title_slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_format', sa.Text(), nullable=False),
        sa.Column('output_format', sa.Text(), nullable=False),
        sa.Column('constraints', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('time_limit_ms', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('memory_limit_mb', sa.Integer(), nullable=False, server_default='256'),
        sa.Column('source_oj', sa.String(50), nullable=True),
        sa.Column('source_problem_id', sa.String(100), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title_slug'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('difficulty >= 1 AND difficulty <= 10', name='check_difficulty_range')
    )
    op.create_index('idx_problems_difficulty', 'problems', ['difficulty'])
    op.create_index('idx_problems_source_oj', 'problems', ['source_oj'])
    op.create_index('idx_problems_published', 'problems', ['is_published', 'created_at'])

    # 创建 problem_tag_associations 表
    op.create_table(
        'problem_tag_associations',
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('problem_id', 'tag_id'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('problem_tag_associations')
    op.drop_table('problems')
    op.drop_table('tags')
```

- [ ] **Step 2: 运行迁移**

```bash
cd D:\AI_code_assistant\backend
alembic upgrade head
```

Expected: 迁移成功执行，数据库中新增 problems、tags、problem_tag_associations 三张表。

- [ ] **Step 3: 验证迁移结果**

```bash
alembic current
```

Expected: 显示当前 revision 为 `20260515_add_problems_and_tags`。

- [ ] **Step 4: Commit**

```bash
cd D:\AI_code_assistant
git add backend/alembic/versions/20260515_add_problems_and_tags.py
git commit -m "feat(db): add problems, tags, and problem_tag_associations tables"
```

---

## Task 2: 数据模型

**Files:**
- Create: `backend/app/models/problem.py`
- Create: `backend/app/models/tag.py`
- Create: `backend/app/models/problem_tag_association.py`
- Modify: `backend/app/models/__init__.py`

**依赖:** Task 1（数据库表已创建）

- [ ] **Step 1: 创建 Problem 模型**

创建文件 `backend/app/models/problem.py`：

```python
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Text, SmallInteger, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    title_slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    input_format = Column(Text, nullable=False)
    output_format = Column(Text, nullable=False)
    constraints = Column(Text, nullable=True)
    difficulty = Column(SmallInteger, nullable=False, default=1)
    time_limit_ms = Column(Integer, nullable=False, default=1000)
    memory_limit_mb = Column(Integer, nullable=False, default=256)
    source_oj = Column(String(50), nullable=True)
    source_problem_id = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tags = relationship("Tag", secondary="problem_tag_associations", back_populates="problems")
    creator = relationship("User", back_populates="problems")
```

- [ ] **Step 2: 创建 Tag 模型**

创建文件 `backend/app/models/tag.py`：

```python
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    name_slug = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    is_lanqiao_special = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    problems = relationship("Problem", secondary="problem_tag_associations", back_populates="tags")
    children = relationship("Tag", backref=backref("parent", remote_side="Tag.id"))
```

- [ ] **Step 3: 创建 ProblemTagAssociation 模型**

创建文件 `backend/app/models/problem_tag_association.py`：

```python
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class ProblemTagAssociation(Base):
    __tablename__ = "problem_tag_associations"
    
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 4: 更新 models/__init__.py**

修改文件 `backend/app/models/__init__.py`：

```python
from app.models.user import User
from app.models.problem import Problem
from app.models.tag import Tag
from app.models.problem_tag_association import ProblemTagAssociation

__all__ = ["User", "Problem", "Tag", "ProblemTagAssociation"]
```

- [ ] **Step 5: 在 User 模型中添加反向关系**

修改文件 `backend/app/models/user.py`，在 `User` 类中添加：

```python
from sqlalchemy.orm import relationship  # 如果还没有导入

class User(Base):
    # ... 现有字段 ...
    
    # 添加反向关系
    problems = relationship("Problem", back_populates="creator")
```

- [ ] **Step 6: Commit**

```bash
cd D:\AI_code_assistant
git add backend/app/models/
git commit -m "feat(models): add Problem, Tag, and ProblemTagAssociation models"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/problem.py`
- Create: `backend/app/schemas/tag.py`
- Modify: `backend/app/schemas/__init__.py`

**依赖:** Task 2（模型已定义）

- [ ] **Step 1: 创建 Problem Schemas**

创建文件 `backend/app/schemas/problem.py`：

```python
from datetime import datetime
from typing import List, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, Field


class TagBrief(BaseModel):
    """标签精简信息（用于题目关联）"""
    id: UUID
    name: str
    color: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProblemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    input_format: str = Field(..., min_length=1)
    output_format: str = Field(..., min_length=1)
    constraints: Optional[str] = None
    difficulty: int = Field(..., ge=1, le=10)
    time_limit_ms: int = Field(default=1000, ge=100)
    memory_limit_mb: int = Field(default=256, ge=16)
    source_oj: Optional[str] = Field(default=None, max_length=50)
    source_problem_id: Optional[str] = Field(default=None, max_length=100)
    source_url: Optional[str] = Field(default=None, max_length=500)


class ProblemCreate(ProblemBase):
    tag_ids: Optional[List[UUID]] = []


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    difficulty: Optional[int] = Field(default=None, ge=1, le=10)
    time_limit_ms: Optional[int] = Field(default=None, ge=100)
    memory_limit_mb: Optional[int] = Field(default=None, ge=16)
    source_oj: Optional[str] = Field(default=None, max_length=50)
    source_problem_id: Optional[str] = Field(default=None, max_length=100)
    source_url: Optional[str] = Field(default=None, max_length=500)
    tag_ids: Optional[List[UUID]] = None


class ProblemInDB(ProblemBase):
    id: UUID
    title_slug: str
    is_published: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagBrief] = []
    
    class Config:
        from_attributes = True


class ProblemListItem(BaseModel):
    """列表页精简数据"""
    id: UUID
    title: str
    title_slug: str
    difficulty: int
    source_oj: Optional[str] = None
    tags: List[TagBrief] = []
    
    class Config:
        from_attributes = True


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应通用结构"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

- [ ] **Step 2: 创建 Tag Schemas**

创建文件 `backend/app/schemas/tag.py`：

```python
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(default=None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_lanqiao_special: bool = False


class TagCreate(TagBase):
    parent_id: Optional[UUID] = None


class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(default=None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_lanqiao_special: Optional[bool] = None
    parent_id: Optional[UUID] = None


class TagInDB(TagBase):
    id: UUID
    name_slug: str
    parent_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagBrief(BaseModel):
    """标签精简信息"""
    id: UUID
    name: str
    color: Optional[str] = None
    
    class Config:
        from_attributes = True
```

- [ ] **Step 3: 更新 schemas/__init__.py**

修改文件 `backend/app/schemas/__init__.py`：

```python
from app.schemas.problem import (
    ProblemBase,
    ProblemCreate,
    ProblemUpdate,
    ProblemInDB,
    ProblemListItem,
    PaginatedResponse,
    TagBrief
)
from app.schemas.tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagInDB,
    TagBrief
)

__all__ = [
    "ProblemBase",
    "ProblemCreate",
    "ProblemUpdate",
    "ProblemInDB",
    "ProblemListItem",
    "PaginatedResponse",
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagInDB",
    "TagBrief"
]
```

- [ ] **Step 4: Commit**

```bash
cd D:\AI_code_assistant
git add backend/app/schemas/
git commit -m "feat(schemas): add Problem and Tag Pydantic schemas"
```

---

## Task 4: Tag Service + Router

**Files:**
- Create: `backend/app/services/tag_service.py`
- Create: `backend/app/routers/tags.py`
- Modify: `backend/app/services/__init__.py`
- Modify: `backend/app/routers/__init__.py`
- Create: `backend/tests/test_tags.py`

**依赖:** Task 3（Schemas 已定义）

- [ ] **Step 1: 创建 TagService**

创建文件 `backend/app/services/tag_service.py`：

```python
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    @staticmethod
    async def get_tags(
        db: AsyncSession,
        category: Optional[str] = None
    ) -> List[Tag]:
        query = select(Tag)
        if category:
            query = query.where(Tag.category == category)
        query = query.order_by(Tag.name)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_tag(db: AsyncSession, tag_id: UUID) -> Optional[Tag]:
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tags_by_ids(db: AsyncSession, tag_ids: List[UUID]) -> List[Tag]:
        if not tag_ids:
            return []
        result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
        from app.utils.security import slugify  # 需要确认是否存在，否则自己实现
        
        tag = Tag(
            name=data.name,
            name_slug=slugify(data.name),
            category=data.category,
            description=data.description,
            color=data.color,
            is_lanqiao_special=data.is_lanqiao_special,
            parent_id=data.parent_id
        )
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: UUID, data: TagUpdate) -> Optional[Tag]:
        tag = await TagService.get_tag(db, tag_id)
        if not tag:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            from app.utils.security import slugify
            update_data["name_slug"] = slugify(update_data["name"])
        
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        await db.flush()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: UUID) -> bool:
        tag = await TagService.get_tag(db, tag_id)
        if not tag:
            return False
        await db.delete(tag)
        await db.flush()
        return True
```

- [ ] **Step 2: 添加 slugify 工具函数**

如果不存在，在 `backend/app/utils/security.py` 末尾添加：

```python
import re

def slugify(text: str) -> str:
    """将文本转换为 URL 友好的 slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:100]
```

- [ ] **Step 3: 创建 Tag Router**

创建文件 `backend/app/routers/tags.py`：

```python
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.tag import TagCreate, TagInDB, TagUpdate
from app.services.tag_service import TagService
from app.utils.security import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagInDB])
async def list_tags(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取标签列表"""
    return await TagService.get_tags(db, category=category)


@router.get("/{tag_id}", response_model=TagInDB)
async def get_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取标签详情"""
    tag = await TagService.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.post("", response_model=TagInDB, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建标签（仅管理员）"""
    return await TagService.create_tag(db, data)


@router.patch("/{tag_id}", response_model=TagInDB)
async def update_tag(
    tag_id: UUID,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新标签（仅管理员）"""
    tag = await TagService.update_tag(db, tag_id, data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除标签（仅管理员）"""
    success = await TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
```

- [ ] **Step 4: 更新 __init__.py 文件**

修改 `backend/app/services/__init__.py`：

```python
from app.services.tag_service import TagService

__all__ = ["TagService"]
```

修改 `backend/app/routers/__init__.py`：

```python
from app.routers.tags import router as tags_router

__all__ = ["tags_router"]
```

- [ ] **Step 5: 创建 Tag 测试**

创建文件 `backend/tests/test_tags.py`：

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.tag import Tag

client = TestClient(app)


@pytest.fixture
async def test_tag(db: AsyncSession):
    """创建测试标签"""
    tag = Tag(
        name="动态规划",
        name_slug="dong-tai-gui-hua",
        category="algorithm",
        description="Dynamic Programming"
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


def test_list_tags():
    """测试获取标签列表"""
    response = client.get("/api/v1/tags")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_tags_with_category():
    """测试按分类筛选标签"""
    response = client.get("/api/v1/tags?category=algorithm")
    assert response.status_code == 200
    data = response.json()
    for tag in data:
        assert tag["category"] == "algorithm"
```

- [ ] **Step 6: 运行 Tag 测试**

```bash
cd D:\AI_code_assistant\backend
pytest tests/test_tags.py -v
```

Expected: 测试通过。

- [ ] **Step 7: Commit**

```bash
cd D:\AI_code_assistant
git add backend/app/services/tag_service.py backend/app/routers/tags.py backend/app/services/__init__.py backend/app/routers/__init__.py backend/tests/test_tags.py
git commit -m "feat(tags): implement Tag service and API routes"
```

---

## Task 5: Problem Service（基础 CRUD）

**Files:**
- Create: `backend/app/services/problem_service.py`
- Modify: `backend/app/services/__init__.py`
- Create: `backend/tests/test_problem_service.py`

**依赖:** Task 4（TagService 已完成）

- [ ] **Step 1: 创建 ProblemService**

创建文件 `backend/app/services/problem_service.py`：

```python
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem
from app.models.tag import Tag
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.services.tag_service import TagService


class ProblemService:
    @staticmethod
    async def get_problem(db: AsyncSession, problem_id: UUID) -> Optional[Problem]:
        """获取题目详情（含标签）"""
        result = await db.execute(
            select(Problem)
            .where(Problem.id == problem_id)
            .options(selectinload(Problem.tags))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_problem(
        db: AsyncSession,
        data: ProblemCreate,
        user_id: UUID
    ) -> Problem:
        """创建题目"""
        from app.utils.security import slugify
        
        # 生成唯一 slug
        base_slug = slugify(data.title)
        slug = base_slug
        counter = 1
        while True:
            existing = await db.execute(
                select(Problem).where(Problem.title_slug == slug)
            )
            if not existing.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # 创建题目
        problem = Problem(
            title=data.title,
            title_slug=slug,
            description=data.description,
            input_format=data.input_format,
            output_format=data.output_format,
            constraints=data.constraints,
            difficulty=data.difficulty,
            time_limit_ms=data.time_limit_ms,
            memory_limit_mb=data.memory_limit_mb,
            source_oj=data.source_oj,
            source_problem_id=data.source_problem_id,
            source_url=data.source_url,
            created_by=user_id,
            is_published=False  # 默认未发布
        )
        db.add(problem)
        await db.flush()
        
        # 关联标签
        if data.tag_ids:
            tags = await TagService.get_tags_by_ids(db, data.tag_ids)
            problem.tags = tags
        
        await db.flush()
        await db.refresh(problem)
        return problem
    
    @staticmethod
    async def update_problem(
        db: AsyncSession,
        problem_id: UUID,
        data: ProblemUpdate
    ) -> Optional[Problem]:
        """更新题目"""
        problem = await ProblemService.get_problem(db, problem_id)
        if not problem:
            return None
        
        # 更新非 None 字段
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果更新标题，重新生成 slug
        if "title" in update_data:
            from app.utils.security import slugify
            base_slug = slugify(update_data["title"])
            slug = base_slug
            counter = 1
            while True:
                existing = await db.execute(
                    select(Problem).where(
                        and_(Problem.title_slug == slug, Problem.id != problem_id)
                    )
                )
                if not existing.scalar_one_or_none():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
            update_data["title_slug"] = slug
        
        # 如果更新标签
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                tags = await TagService.get_tags_by_ids(db, tag_ids)
                problem.tags = tags
        
        for field, value in update_data.items():
            setattr(problem, field, value)
        
        await db.flush()
        await db.refresh(problem)
        return problem
    
    @staticmethod
    async def delete_problem(db: AsyncSession, problem_id: UUID) -> bool:
        """删除题目"""
        problem = await ProblemService.get_problem(db, problem_id)
        if not problem:
            return False
        await db.delete(problem)
        await db.flush()
        return True
```

- [ ] **Step 2: 更新 services/__init__.py**

修改 `backend/app/services/__init__.py`：

```python
from app.services.tag_service import TagService
from app.services.problem_service import ProblemService

__all__ = ["TagService", "ProblemService"]
```

- [ ] **Step 3: Commit**

```bash
cd D:\AI_code_assistant
git add backend/app/services/
git commit -m "feat(problems): implement Problem service with CRUD operations"
```

---

## Task 6: Problem Router + 筛选分页

**Files:**
- Create: `backend/app/routers/problems.py`
- Modify: `backend/app/routers/__init__.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_problems.py`

**依赖:** Task 5（ProblemService 已完成）

- [ ] **Step 1: 完善 ProblemService 的列表查询**

修改 `backend/app/services/problem_service.py`，添加 `list_problems` 方法：

```python
    @staticmethod
    async def list_problems(
        db: AsyncSession,
        search: Optional[str] = None,
        difficulty_min: Optional[int] = None,
        difficulty_max: Optional[int] = None,
        source_oj: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Problem], int]:
        """获取题目列表（支持筛选和分页）"""
        # 基础查询：只返回已发布的题目
        query = select(Problem).where(Problem.is_published == True)
        
        # 关键词搜索
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Problem.title.ilike(search_term),
                    Problem.description.ilike(search_term)
                )
            )
        
        # 难度范围
        if difficulty_min is not None:
            query = query.where(Problem.difficulty >= difficulty_min)
        if difficulty_max is not None:
            query = query.where(Problem.difficulty <= difficulty_max)
        
        # 来源筛选
        if source_oj:
            query = query.where(Problem.source_oj == source_oj)
        
        # 标签筛选（AND 关系）
        if tag_ids:
            for tag_id in tag_ids:
                query = query.where(
                    Problem.tags.any(Tag.id == tag_id)
                )
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        query = (
            query
            .options(selectinload(Problem.tags))
            .order_by(Problem.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total
```

需要在文件顶部导入 `or_`：

```python
from sqlalchemy import select, func, and_, or_
```

- [ ] **Step 2: 创建 Problem Router**

创建文件 `backend/app/routers/problems.py`：

```python
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.problem import (
    ProblemCreate,
    ProblemInDB,
    ProblemListItem,
    ProblemUpdate,
    PaginatedResponse
)
from app.services.problem_service import ProblemService
from app.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=PaginatedResponse[ProblemListItem])
async def list_problems(
    search: Optional[str] = None,
    difficulty_min: Optional[int] = Query(None, ge=1, le=10),
    difficulty_max: Optional[int] = Query(None, ge=1, le=10),
    source_oj: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取题目列表（支持筛选和分页）"""
    items, total = await ProblemService.list_problems(
        db,
        search=search,
        difficulty_min=difficulty_min,
        difficulty_max=difficulty_max,
        source_oj=source_oj,
        tag_ids=tag_ids,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{problem_id}", response_model=ProblemInDB)
async def get_problem(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取题目详情"""
    problem = await ProblemService.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem


@router.post("", response_model=ProblemInDB, status_code=status.HTTP_201_CREATED)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建题目"""
    return await ProblemService.create_problem(db, data, current_user.id)


@router.patch("/{problem_id}", response_model=ProblemInDB)
async def update_problem(
    problem_id: UUID,
    data: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新题目"""
    # TODO: 检查权限（创建者或管理员）
    problem = await ProblemService.update_problem(db, problem_id, data)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除题目（仅管理员）"""
    success = await ProblemService.delete_problem(db, problem_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
```

- [ ] **Step 3: 更新 routers/__init__.py**

修改 `backend/app/routers/__init__.py`：

```python
from app.routers.tags import router as tags_router
from app.routers.problems import router as problems_router

__all__ = ["tags_router", "problems_router"]
```

- [ ] **Step 4: 注册路由到 main.py**

修改 `backend/app/main.py`：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, tags, problems  # 修改导入

app = FastAPI(
    title="AI_code_assisstant API",
    description="AI 编程学习平台后端 API",
    version="0.1.0"
)

# CORS 配置（保持不变）
# ...

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")      # 新增
app.include_router(problems.router, prefix="/api/v1")  # 新增

# 健康检查（保持不变）
# ...
```

- [ ] **Step 5: 创建 Problem 测试**

创建文件 `backend/tests/test_problems.py`：

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.problem import Problem
from app.models.tag import Tag

client = TestClient(app)


@pytest.fixture
async def test_problem(db: AsyncSession):
    """创建测试题目"""
    problem = Problem(
        title="两数之和",
        title_slug="liang-shu-zhi-he",
        description="给定一个整数数组 nums 和一个整数目标值 target...",
        input_format="第一行包含两个整数 n 和 target...",
        output_format="输出两个整数的下标...",
        difficulty=3,
        is_published=True
    )
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem


def test_list_problems():
    """测试获取题目列表"""
    response = client.get("/api/v1/problems")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_list_problems_with_filter():
    """测试筛选题目"""
    response = client.get("/api/v1/problems?difficulty_min=1&difficulty_max=5")
    assert response.status_code == 200
    data = response.json()
    for problem in data["items"]:
        assert 1 <= problem["difficulty"] <= 5


def test_get_problem(test_problem):
    """测试获取题目详情"""
    response = client.get(f"/api/v1/problems/{test_problem.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "两数之和"
    assert data["difficulty"] == 3


def test_get_problem_not_found():
    """测试获取不存在的题目"""
    response = client.get("/api/v1/problems/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
```

- [ ] **Step 6: 运行 Problem 测试**

```bash
cd D:\AI_code_assistant\backend
pytest tests/test_problems.py -v
```

Expected: 测试通过。

- [ ] **Step 7: Commit**

```bash
cd D:\AI_code_assistant
git add backend/app/routers/problems.py backend/app/routers/__init__.py backend/app/main.py backend/tests/test_problems.py
git commit -m "feat(problems): implement Problem API routes with filtering and pagination"
```

---

## Task 7: 集成测试与验证

**Files:**
- Modify: 无（仅运行测试）

**依赖:** Task 6（所有路由已注册）

- [ ] **Step 1: 运行全部测试**

```bash
cd D:\AI_code_assistant\backend
pytest tests/ -v
```

Expected: 所有测试通过（包括原有 test_security.py + 新增 test_tags.py + test_problems.py）。

- [ ] **Step 2: 启动服务并手动验证**

```bash
cd D:\AI_code_assistant\backend
uvicorn app.main:app --reload
```

在另一个终端测试 API：

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试标签列表
curl http://localhost:8000/api/v1/tags

# 测试题目列表
curl http://localhost:8000/api/v1/problems

# 测试题目筛选
curl "http://localhost:8000/api/v1/problems?difficulty_min=1&difficulty_max=5&page=1&page_size=10"
```

Expected: 所有接口返回 200 和正确格式的 JSON。

- [ ] **Step 3: Commit（最终）**

```bash
cd D:\AI_code_assistant
git add -A
git commit -m "feat(api): complete Problem and Tag API implementation with tests"
```

---

## 自审检查清单

**1. Spec 覆盖检查：**

| Spec 需求 | 对应任务 | 状态 |
|-----------|----------|------|
| problems 表 CRUD | Task 2, 5, 6 | ✅ |
| tags 表 CRUD | Task 2, 4 | ✅ |
| problem_tag_associations 关联 | Task 2, 5 | ✅ |
| 题目列表 API + 筛选 | Task 6 | ✅ |
| 题目详情 API | Task 6 | ✅ |
| 标签列表 API | Task 4 | ✅ |
| 分页格式 | Task 6 | ✅ |
| 权限控制 | Task 4, 6 | ✅ |
| 数据库迁移 | Task 1 | ✅ |
| 测试覆盖 | Task 4, 6, 7 | ✅ |

**2. Placeholder 扫描：**
- 无 TBD/TODO/"implement later"/"similar to Task X"
- 所有步骤包含完整代码和命令

**3. 类型一致性检查：**
- `ProblemService.create_problem` 参数签名一致
- `TagBrief` schema 在 problem.py 和 tag.py 中定义一致
- 路由前缀 `/api/v1` 与现有 auth 路由一致

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-05-15-problem-api.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints for review

**Which approach?**
