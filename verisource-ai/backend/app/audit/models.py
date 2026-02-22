from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    document_id = Column(UUID(as_uuid=True), nullable=False)

    mode = Column(String, nullable=False)

    query_hash = Column(String, nullable=False)

    decision = Column(String, nullable=False)

    confidence_score = Column(Float, nullable=False)
    
    conflict_detected = Column(Boolean, default=False, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)