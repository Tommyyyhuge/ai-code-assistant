from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    problem_id: UUID
    code: str = Field(..., min_length=1)
    language: str = Field(..., pattern=r'^(cpp|py)$')


class SubmissionResultItem(BaseModel):
    test_case_order: int
    status: str
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    actual_output: Optional[str] = None
    
    class Config:
        from_attributes = True


class SubmissionInDB(BaseModel):
    id: UUID
    problem_id: UUID
    code: str
    language: str
    status: str
    score: Optional[int] = None
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None
    error_message: Optional[str] = None
    submitted_at: datetime
    judged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubmissionListItem(BaseModel):
    id: UUID
    problem_id: UUID
    language: str
    status: str
    score: Optional[int] = None
    runtime_ms: Optional[int] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None
    submitted_at: datetime
    
    class Config:
        from_attributes = True
