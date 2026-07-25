"""
Embedding + answer generation for Phase 3 dense retrieval.

Embeddings: sentence-transformers (all-MiniLM-L6-v2) — runs locally, no API key.
Answer generation: Anthropic Claude — requires ANTHROPIC_API_KEY in .env.

Both clients are lazy so the backend starts cleanly even before any key is set.
"""
from __future__ import annotations
from sentence_transformers import SentenceTransformer
import anthropic
from app.config import settings

EMBED_DIM = 384  # all-MiniLM-L6-v2 output dimension

_embed_model: SentenceTransformer | None = None
_anthropic_client: anthropic.Anthropic | None = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(settings.embedding_model)
    return _embed_model


def _get_anthropic_client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


def embed(text: str) -> list[float]:
    return _get_embed_model().encode(text).tolist()


def embed_batch(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    model = _get_embed_model()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        vectors.extend(model.encode(texts[i : i + batch_size]).tolist())
    return vectors


def generate_answer(question: str, context: str) -> str:
    msg = _get_anthropic_client().messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=(
            "You are a helpful assistant. Answer the user's question using only "
            "the provided context. If the context does not contain enough "
            "information to answer confidently, say so clearly. Be concise."
        ),
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return msg.content[0].text
