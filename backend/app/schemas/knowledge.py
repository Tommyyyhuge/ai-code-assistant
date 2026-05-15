from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── 知识节点 ──

class KnowledgeNodeBrief(BaseModel):
    id: UUID
    title: str
    title_slug: str
    category: str
    level: int
    order_index: int

    class Config:
        from_attributes = True


class KnowledgeNodeTreeItem(KnowledgeNodeBrief):
    user_status: str = "not_started"
    children: list["KnowledgeNodeTreeItem"] = []


class KnowledgeNodeDetail(BaseModel):
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
    id: UUID
    title: str
    title_slug: str
    edge_type: str

    class Config:
        from_attributes = True


class ProblemAssociationItem(BaseModel):
    problem_id: UUID
    title: str
    title_slug: str
    difficulty: int
    difficulty_level: int
    is_required: bool

    class Config:
        from_attributes = True


# ── 聚合响应 ──

class KnowledgeNodeDetailResponse(BaseModel):
    node: KnowledgeNodeDetail
    prerequisites: list[KnowledgeNodeNeighbor] = []
    next_nodes: list[KnowledgeNodeNeighbor] = []
    related_nodes: list[KnowledgeNodeNeighbor] = []
    problems: list[ProblemAssociationItem] = []
    user_progress: Optional["UserProgressResponse"] = None


class KnowledgeTreeResponse(BaseModel):
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
