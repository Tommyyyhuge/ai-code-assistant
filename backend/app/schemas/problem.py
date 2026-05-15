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
