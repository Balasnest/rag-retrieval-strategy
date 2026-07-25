from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    title: str
    word_count: int
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    strategy: str
    chunk_size: int | None
    overlap: int | None
    token_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RechunkRequest(BaseModel):
    document_id: str
    strategy: str
    chunk_size: int = 300
    overlap: int = 50
