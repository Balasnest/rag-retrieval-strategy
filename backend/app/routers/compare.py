import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.query import CompareRequest, CompareResponse, ChunkResult, QueryResponse
from app.core import embedder, bm25_search

router = APIRouter(tags=["compare"])


def _doc_title(document_id, cache: dict, db: Session) -> str | None:
    if document_id not in cache:
        doc = db.query(Document).filter(Document.id == document_id).first()
        cache[document_id] = doc.title if doc else None
    return cache[document_id]


@router.post("/compare", response_model=CompareResponse)
def compare_retrieval(req: CompareRequest, db: Session = Depends(get_db)):
    """Run the same question through dense (pgvector) and BM25 (Elasticsearch)
    and return both result sets with overlap analysis."""

    doc_cache: dict = {}

    # ── Dense retrieval ───────────────────────────────────────────────────────
    dense_start = time.perf_counter()
    query_vector = embedder.embed(req.question)

    distance = Chunk.vector.cosine_distance(query_vector).label("distance")
    dense_rows = (
        db.query(Chunk, distance)
        .filter(Chunk.vector.isnot(None))
        .order_by(distance)
        .limit(req.top_k)
        .all()
    )
    dense_chunks = [
        ChunkResult(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            strategy=chunk.strategy,
            token_count=chunk.token_count,
            score=round(1 - float(dist), 4),
            document_title=_doc_title(chunk.document_id, doc_cache, db),
        )
        for chunk, dist in dense_rows
    ]
    dense_latency = round((time.perf_counter() - dense_start) * 1000, 1)

    # ── BM25 retrieval ────────────────────────────────────────────────────────
    bm25_start = time.perf_counter()
    hits = bm25_search.search(req.question, req.top_k)
    bm25_chunks = [
        ChunkResult(
            id=hit["chunk_id"],
            document_id=hit["document_id"],
            content=hit["content"],
            chunk_index=hit["chunk_index"],
            strategy=hit["strategy"],
            token_count=hit["token_count"],
            score=round(hit["score"], 4),
            document_title=hit.get("document_title"),
        )
        for hit in hits
    ]
    bm25_latency = round((time.perf_counter() - bm25_start) * 1000, 1)

    # ── Generate answers ──────────────────────────────────────────────────────
    def answer_from(chunks: list[ChunkResult], fallback: str) -> str:
        if not chunks:
            return fallback
        return embedder.generate_answer(req.question, "\n\n---\n\n".join(c.content for c in chunks))

    dense_answer = answer_from(dense_chunks, "No indexed chunks found. Run Build Index first.")
    bm25_answer  = answer_from(bm25_chunks,  "No BM25 indexed chunks found. Run Build Index first.")

    # ── Overlap ───────────────────────────────────────────────────────────────
    dense_ids   = {str(c.id) for c in dense_chunks}
    bm25_ids    = {str(c.id) for c in bm25_chunks}
    overlap_ids = list(dense_ids & bm25_ids)

    return CompareResponse(
        question=req.question,
        dense=QueryResponse(question=req.question, answer=dense_answer, mode="dense",
                            chunks=dense_chunks, latency_ms=dense_latency),
        bm25=QueryResponse(question=req.question,  answer=bm25_answer,  mode="bm25",
                           chunks=bm25_chunks,  latency_ms=bm25_latency),
        overlap_count=len(overlap_ids),
        overlap_ids=overlap_ids,
    )
