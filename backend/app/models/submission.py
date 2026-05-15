import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="Pending")
    score = Column(Integer, nullable=True)
    runtime_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    passed_count = Column(SmallInteger, nullable=True)
    total_count = Column(SmallInteger, nullable=True)
    error_message = Column(Text, nullable=True)
    judge_log = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    judged_at = Column(DateTime, nullable=True)

    results = relationship("SubmissionResult", back_populates="submission", cascade="all, delete-orphan")
