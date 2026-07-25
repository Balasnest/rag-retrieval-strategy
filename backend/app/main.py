from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import engine, Base
import app.models  # noqa: F401 — registers Document + Chunk with Base
from app.routers import documents, chunk, index, query, compare, metrics


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RAG Explorer API",
    description="Educational RAG debugger backend.",
    version="0.2.0-phase2",
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
    return {"status": "ok", "phase": 2, "message": "Document ingestion + chunking live."}


app.include_router(documents.router)
app.include_router(chunk.router)
app.include_router(index.router)
app.include_router(query.router)
app.include_router(compare.router)
app.include_router(metrics.router)
