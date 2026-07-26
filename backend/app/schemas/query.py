from pydantic import BaseModel
from uuid import UUID


class IndexRequest(BaseModel):
    document_id: str | None = None
    strategy: str = "fixed"


class IndexResponse(BaseModel):
    indexed: int
    already_embedded: int
    es_indexed: int
    document_ids: list[str]


class ChunkResult(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    strategy: str
    token_count: int
    score: float
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


class CompareRequest(BaseModel):
    question: str
    top_k: int = 5


class CompareResponse(BaseModel):
    question: str
    dense: QueryResponse
    bm25: QueryResponse
    overlap_count: int
    overlap_ids: list[str]
