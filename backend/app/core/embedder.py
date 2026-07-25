"""
OpenAI embeddings + chat completion helpers for Phase 3 dense retrieval.

The client is created lazily on first use so the backend starts cleanly
even if OPENAI_API_KEY is not yet set.
"""
from __future__ import annotations
from openai import OpenAI
from app.config import settings

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def embed(text: str) -> list[float]:
    resp = _get_client().embeddings.create(model=settings.openai_embedding_model, input=text)
    return resp.data[0].embedding


def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed texts in batches to stay within the API's per-request token limit."""
    client = _get_client()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=settings.openai_embedding_model, input=batch)
        vectors.extend([d.embedding for d in sorted(resp.data, key=lambda x: x.index)])
    return vectors


def generate_answer(question: str, context: str) -> str:
    resp = _get_client().chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the user's question using only "
                    "the provided context. If the context does not contain enough "
                    "information to answer confidently, say so clearly. Be concise."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    return resp.choices[0].message.content or ""
