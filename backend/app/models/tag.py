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
