from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import StubResponse

router = APIRouter(tags=["indexing"])


class IndexRequest(BaseModel):
    reset: bool = False


@router.post("/index", response_model=StubResponse)
def build_index(req: IndexRequest):
    """Will run the full ingestion pipeline: load sample_data -> chunk ->
    embed -> write to pgvector -> write to Elasticsearch. Split across
    Phase 2 (ingest+chunk), Phase 3 (pgvector write), Phase 4 (ES write)."""
    return StubResponse(
        phase_planned="Phases 2-4 — ingestion, pgvector, Elasticsearch",
        message="Not implemented yet.",
        data=None,
    )


class EmbedRequest(BaseModel):
    text: str


@router.post("/embed", response_model=StubResponse)
def embed_text(req: EmbedRequest):
    """Will call the OpenAI embeddings API once Phase 3 (dense retrieval)
    lands."""
    return StubResponse(
        phase_planned="Phase 3 — Dense retrieval with pgvector",
        message=f"Not implemented yet. Would embed {len(req.text)} characters of text.",
        data=None,
    )
