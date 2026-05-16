import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, SmallInteger, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    title_slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    estimated_days = Column(Integer, nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"
    __table_args__ = (UniqueConstraint("path_id", "knowledge_node_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    knowledge_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LearningPathProgress(Base):
    __tablename__ = "learning_path_progress"
    __table_args__ = (UniqueConstraint("user_id", "path_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    status = Column(String(20), nullable=False, default="not_started")
    completed_nodes = Column(SmallInteger, nullable=False, default=0)
    total_nodes = Column(SmallInteger, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
