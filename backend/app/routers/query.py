from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from app.schemas.common import StubResponse

router = APIRouter(tags=["query"])


class QueryRequest(BaseModel):
    question: str
    mode: Literal["no_rag", "stuff_kb", "dense", "bm25", "hybrid"] = "dense"
    top_k: int = 5


@router.post("/query", response_model=StubResponse)
def run_query(req: QueryRequest):
    """This is the Retrieval Playground's main endpoint: question ->
    embedding -> retrieval (per `mode`) -> prompt -> LLM answer, with
    every stage returned for display. Built incrementally:
      - "no_rag" / "stuff_kb": Phase 2 (once documents exist to stuff)
      - "dense": Phase 3 (pgvector)
      - "bm25": Phase 4 (Elasticsearch)
      - "hybrid": Phase 5
    """
    return StubResponse(
        phase_planned="Phases 2-5, depending on `mode`",
        message=f"Not implemented yet. Would run mode='{req.mode}' for question: {req.question!r}",
        data=None,
    )
