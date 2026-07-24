from fastapi import APIRouter
from app.schemas.common import StubResponse

router = APIRouter(tags=["metrics"])


@router.post("/metrics", response_model=StubResponse)
def get_metrics():
    """Will return embedding time, retrieval time, LLM latency, total
    latency, prompt/completion tokens, and estimated cost for recent
    queries, once there are real queries to measure (Phase 3 onward)."""
    return StubResponse(
        phase_planned="Phase 3 onward — populated as real retrieval runs happen",
        message="Not implemented yet.",
        data=None,
    )
