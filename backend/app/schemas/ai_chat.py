from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    knowledge_node_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    title: Optional[str] = "新对话"


class ConversationBrief(BaseModel):
    id: UUID
    title: str
    knowledge_node_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StreamRequest(BaseModel):
    content: str


class MessageItem(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
