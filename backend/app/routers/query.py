import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.query import QueryRequest, QueryResponse, ChunkResult
from app.core import embedder, bm25_search

router = APIRouter(tags=["query"])


def _doc_title(document_id, cache: dict, db: Session) -> str | None:
    if document_id not in cache:
        doc = db.query(Document).filter(Document.id == document_id).first()
        cache[document_id] = doc.title if doc else None
    return cache[document_id]


@router.post("/query", response_model=QueryResponse)
def run_query(req: QueryRequest, db: Session = Depends(get_db)):
    if req.mode not in ("dense", "bm25"):
        raise HTTPException(
            status_code=400,
            detail=f"mode='{req.mode}' not supported. Use 'dense' or 'bm25'.",
        )

    start = time.perf_counter()

    if req.mode == "dense":
        query_vector = embedder.embed(req.question)
        distance = Chunk.vector.cosine_distance(query_vector).label("distance")
        rows = (
            db.query(Chunk, distance)
            .filter(Chunk.vector.isnot(None))
            .order_by(distance)
            .limit(req.top_k)
            .all()
        )

        if not rows:
            return QueryResponse(
                question=req.question,
                answer="No indexed chunks found. Use POST /index to embed your documents first.",
                mode=req.mode,
                chunks=[],
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )

        doc_cache: dict = {}
        chunks = [
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
            for chunk, dist in rows
        ]

    else:  # bm25
        hits = bm25_search.search(req.question, req.top_k)

        if not hits:
            return QueryResponse(
                question=req.question,
                answer="No BM25 indexed chunks found. Use POST /index first.",
                mode=req.mode,
                chunks=[],
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )

        chunks = [
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

    context = "\n\n---\n\n".join(c.content for c in chunks)
    answer = embedder.generate_answer(req.question, context)

    return QueryResponse(
        question=req.question,
        answer=answer,
        mode=req.mode,
        chunks=chunks,
        latency_ms=round((time.perf_counter() - start) * 1000, 1),
    )
