import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.query import QueryRequest, QueryResponse, ChunkResult
from app.core import embedder

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def run_query(req: QueryRequest, db: Session = Depends(get_db)):
    if req.mode != "dense":
        raise HTTPException(
            status_code=400,
            detail=f"mode='{req.mode}' not supported yet. Only 'dense' is available in Phase 3.",
        )

    start = time.perf_counter()

    query_vector = embedder.embed(req.question)

    # Cosine distance search via pgvector — lower distance = more similar
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

    context = "\n\n---\n\n".join(chunk.content for chunk, _ in rows)
    answer = embedder.generate_answer(req.question, context)
    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    doc_cache: dict = {}
    chunk_results = []
    for chunk, dist in rows:
        if chunk.document_id not in doc_cache:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            doc_cache[chunk.document_id] = doc.title if doc else None
        chunk_results.append(
            ChunkResult(
                id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                strategy=chunk.strategy,
                token_count=chunk.token_count,
                score=round(1 - float(dist), 4),
                document_title=doc_cache[chunk.document_id],
            )
        )

    return QueryResponse(
        question=req.question,
        answer=answer,
        mode=req.mode,
        chunks=chunk_results,
        latency_ms=latency_ms,
    )
