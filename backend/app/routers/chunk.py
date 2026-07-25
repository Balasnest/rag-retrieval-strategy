from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import ChunkResponse, RechunkRequest
from app.core import chunker

router = APIRouter(tags=["chunking"])


@router.post("/chunk", response_model=list[ChunkResponse])
def rechunk(req: RechunkRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if req.strategy not in ("fixed", "sentence", "paragraph"):
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy}. Use fixed, sentence, or paragraph.")

    # Replace existing chunks for this (document, strategy) pair
    db.query(Chunk).filter(
        Chunk.document_id == req.document_id,
        Chunk.strategy == req.strategy,
    ).delete()

    if req.strategy == "fixed":
        chunks_text = chunker.chunk_fixed(doc.raw_text, req.chunk_size, req.overlap)
        chunk_size, overlap = req.chunk_size, req.overlap
    elif req.strategy == "sentence":
        chunks_text = chunker.chunk_sentence(doc.raw_text)
        chunk_size, overlap = None, None
    else:
        chunks_text = chunker.chunk_paragraph(doc.raw_text)
        chunk_size, overlap = None, None

    new_chunks = []
    for i, text in enumerate(chunks_text):
        c = Chunk(
            document_id=req.document_id,
            content=text,
            chunk_index=i,
            strategy=req.strategy,
            chunk_size=chunk_size,
            overlap=overlap,
            token_count=chunker.token_count(text),
        )
        db.add(c)
        new_chunks.append(c)

    db.commit()
    for c in new_chunks:
        db.refresh(c)

    return new_chunks
