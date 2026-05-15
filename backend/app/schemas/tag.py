from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(default=None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_lanqiao_special: bool = False


class TagCreate(TagBase):
    parent_id: Optional[UUID] = None


class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(default=None, pattern=r'^#[0-9A-Fa-f]{6}$')
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
