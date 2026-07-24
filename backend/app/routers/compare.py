from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import StubResponse

router = APIRouter(tags=["compare"])


class CompareRequest(BaseModel):
    question: str


@router.post("/compare", response_model=StubResponse)
def compare_strategies(req: CompareRequest):
    """The Compare Retrieval page: runs No RAG / Dense / BM25 / Hybrid for
    the SAME question side by side (retrieved chunks, answer, latency,
    success/failure). Lands in Phase 5, after each strategy exists on its
    own (Phases 2-4)."""
    return StubResponse(
        phase_planned="Phase 5 — Hybrid comparison page",
        message=f"Not implemented yet. Would compare all 4 strategies for: {req.question!r}",
        data=None,
    )
