from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import DocumentResponse, ChunkResponse
from app.core import chunker, bm25_search

router = APIRouter(tags=["documents"])


def _doc_response(doc: Document, db: Session) -> DocumentResponse:
    chunk_count = db.query(func.count(Chunk.id)).filter(Chunk.document_id == doc.id).scalar()
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        title=doc.title,
        word_count=doc.word_count,
        chunk_count=chunk_count or 0,
        created_at=doc.created_at,
    )


@router.post("/documents/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename or "").endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported in Phase 2.")

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")

    title = (file.filename or "untitled").rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    doc = Document(filename=file.filename, title=title, raw_text=text, word_count=len(text.split()))
    db.add(doc)
    db.flush()

    chunks_text = chunker.chunk_fixed(text)
    for i, chunk_text in enumerate(chunks_text):
        db.add(Chunk(
            document_id=doc.id,
            content=chunk_text,
            chunk_index=i,
            strategy="fixed",
            chunk_size=300,
            overlap=50,
            token_count=chunker.token_count(chunk_text),
        ))

    db.commit()
    db.refresh(doc)
    return _doc_response(doc, db)


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [_doc_response(doc, db) for doc in docs]


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    db.delete(doc)
    db.commit()
    bm25_search.delete_document(document_id)


@router.get("/chunks", response_model=list[ChunkResponse])
def list_chunks(document_id: str, strategy: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Chunk).filter(Chunk.document_id == document_id)
    if strategy:
        q = q.filter(Chunk.strategy == strategy)
    return q.order_by(Chunk.chunk_index).all()
