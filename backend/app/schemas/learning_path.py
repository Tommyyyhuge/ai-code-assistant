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
