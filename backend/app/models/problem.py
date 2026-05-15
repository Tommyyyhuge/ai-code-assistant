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
