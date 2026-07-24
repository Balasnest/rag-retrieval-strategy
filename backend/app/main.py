"""
RAG Explorer backend — FastAPI app.

Phase 1 status: skeleton only. Every route below except `/health` returns
a clearly-labeled stub response (`implemented: false`) — see
docs/PHASES.md for what's real vs. planned.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import documents, chunk, index, query, compare, metrics

app = FastAPI(
    title="RAG Explorer API",
    description="Educational RAG debugger backend. Not a production API.",
    version="0.1.0-phase1",
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
    """The one real endpoint in Phase 1 — proves the frontend <-> backend
    wiring works before any retrieval logic exists."""
    return {
        "status": "ok",
        "phase": 1,
        "message": "FastAPI skeleton is running. No retrieval logic implemented yet.",
    }


app.include_router(documents.router)
app.include_router(chunk.router)
app.include_router(index.router)
app.include_router(query.router)
app.include_router(compare.router)
app.include_router(metrics.router)
