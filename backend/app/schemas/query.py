from pydantic import BaseModel
from uuid import UUID


class IndexRequest(BaseModel):
    document_id: str | None = None
    strategy: str = "fixed"


class IndexResponse(BaseModel):
    indexed: int
    already_embedded: int
    document_ids: list[str]


class ChunkResult(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    strategy: str
    token_count: int
    score: float          # cosine similarity 0–1 (1 = identical)
    document_title: str | None = None

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    question: str
    mode: str = "dense"
    top_k: int = 5


class QueryResponse(BaseModel):
    question: str
    answer: str
    mode: str
    chunks: list[ChunkResult]
    latency_ms: float
