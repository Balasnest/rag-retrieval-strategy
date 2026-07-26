from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.query import IndexRequest, IndexResponse
from app.core import embedder, bm25_search

router = APIRouter(tags=["indexing"])


@router.post("/index", response_model=IndexResponse)
def build_index(req: IndexRequest, db: Session = Depends(get_db)):
    """Embed chunks into pgvector AND index content into Elasticsearch.

    pgvector: skips chunks that already have a vector (safe to re-run).
    Elasticsearch: always upserts — idempotent.
    """
    q = db.query(Chunk).filter(Chunk.strategy == req.strategy)
    if req.document_id:
        q = q.filter(Chunk.document_id == req.document_id)

    all_chunks = q.all()
    to_embed = [c for c in all_chunks if c.vector is None]
    already_done = len(all_chunks) - len(to_embed)

    # ── pgvector embeddings ───────────────────────────────────────────────────
    if to_embed:
        vectors = embedder.embed_batch([c.content for c in to_embed])
        for chunk, vector in zip(to_embed, vectors):
            chunk.vector = vector
        db.commit()

    # ── Elasticsearch BM25 index ──────────────────────────────────────────────
    doc_cache: dict = {}
    es_docs = []
    for chunk in all_chunks:
        if chunk.document_id not in doc_cache:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            doc_cache[chunk.document_id] = doc.title if doc else None
        es_docs.append({
            "chunk_id":       str(chunk.id),
            "document_id":    str(chunk.document_id),
            "document_title": doc_cache[chunk.document_id],
            "content":        chunk.content,
            "chunk_index":    chunk.chunk_index,
            "strategy":       chunk.strategy,
            "token_count":    chunk.token_count,
        })

    es_indexed = bm25_search.index_chunks(es_docs) if es_docs else 0

    doc_ids = list({str(c.document_id) for c in all_chunks})
    return IndexResponse(
        indexed=len(to_embed),
        already_embedded=already_done,
        es_indexed=es_indexed,
        document_ids=doc_ids,
    )
