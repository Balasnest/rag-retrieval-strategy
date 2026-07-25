import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    strategy = Column(String(50), nullable=False)   # "fixed" | "sentence" | "paragraph"
    chunk_size = Column(Integer, nullable=True)      # null for sentence/paragraph
    overlap = Column(Integer, nullable=True)         # null for sentence/paragraph
    token_count = Column(Integer, nullable=False)
    vector = Column(Vector(1536), nullable=True)     # populated by POST /index (Phase 3)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="chunks")
