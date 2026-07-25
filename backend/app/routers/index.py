from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.chunk import Chunk
from app.schemas.query import IndexRequest, IndexResponse
from app.core import embedder

router = APIRouter(tags=["indexing"])


@router.post("/index", response_model=IndexResponse)
def build_index(req: IndexRequest, db: Session = Depends(get_db)):
    """Embed chunks and store their vectors in Postgres.

    Targets chunks matching the given strategy (default: fixed).
    Skips chunks that already have a vector — safe to call repeatedly.
    If document_id is provided, only that document's chunks are processed.
    """
    q = db.query(Chunk).filter(Chunk.strategy == req.strategy)
    if req.document_id:
        q = q.filter(Chunk.document_id == req.document_id)

    all_chunks = q.all()
    to_embed = [c for c in all_chunks if c.vector is None]
    already_done = len(all_chunks) - len(to_embed)

    if not to_embed:
        return IndexResponse(indexed=0, already_embedded=already_done, document_ids=[])

    vectors = embedder.embed_batch([c.content for c in to_embed])
    for chunk, vector in zip(to_embed, vectors):
        chunk.vector = vector

    db.commit()

    doc_ids = list({str(c.document_id) for c in to_embed})
    return IndexResponse(indexed=len(to_embed), already_embedded=already_done, document_ids=doc_ids)
