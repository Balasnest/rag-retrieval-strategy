from fastapi import APIRouter
from app.schemas.common import StubResponse

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=StubResponse)
def list_documents():
    """Will return the full document list with metadata (title, category,
    department, product, version, date) once Phase 2 (ingestion +
    chunking) lands. For now: stub."""
    return StubResponse(
        phase_planned="Phase 2 — Document ingestion + chunking",
        message="Not implemented yet. This will list all ingested documents once ingestion is built.",
        data=[],
    )


@router.get("/chunks", response_model=StubResponse)
def list_chunks(document_id: str | None = None):
    """Will return the chunks for a given document_id (or all chunks) once
    Phase 2 lands."""
    return StubResponse(
        phase_planned="Phase 2 — Document ingestion + chunking",
        message="Not implemented yet. This will list chunks for a document once chunking is built.",
        data=[],
    )
