from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import StubResponse

router = APIRouter(tags=["chunking"])


class ChunkRequest(BaseModel):
    document_id: str
    chunk_size: int = 300
    overlap: int = 50


@router.post("/chunk", response_model=StubResponse)
def chunk_document(req: ChunkRequest):
    """Will re-chunk a document on demand (used by the Chunk Explorer's
    'change chunk size / overlap, regenerate instantly' control) once
    Phase 2 lands."""
    return StubResponse(
        phase_planned="Phase 2 — Document ingestion + chunking",
        message=f"Not implemented yet. Would chunk document_id={req.document_id} "
                f"with chunk_size={req.chunk_size}, overlap={req.overlap}.",
        data=None,
    )
