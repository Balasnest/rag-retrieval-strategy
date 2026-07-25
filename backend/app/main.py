from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db import engine, Base
import app.models  # noqa: F401 — registers Document + Chunk with Base
from app.routers import documents, chunk, index, query, compare, metrics


@asynccontextmanager
async def lifespan(_: FastAPI):
    with engine.connect() as conn:
        # Enable pgvector extension (required before using vector columns)
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Create tables that don't exist yet
    Base.metadata.create_all(bind=engine)

    # Idempotent migration: add vector column if table was created before Phase 3
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS vector vector(384)"
        ))
        conn.commit()

    yield


app = FastAPI(
    title="RAG Explorer API",
    description="Educational RAG debugger backend.",
    version="0.3.0-phase3",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 3, "message": "Dense retrieval with pgvector live."}


app.include_router(documents.router)
app.include_router(chunk.router)
app.include_router(index.router)
app.include_router(query.router)
app.include_router(compare.router)
app.include_router(metrics.router)
