"""
Embedding + answer generation for Phase 3 dense retrieval.

Embeddings:  sentence-transformers (all-MiniLM-L6-v2) — free, runs locally.
LLM answers: Anthropic Claude  →  set LLM_PROVIDER=anthropic in .env
             OpenAI GPT        →  set LLM_PROVIDER=openai   in .env

Switch providers by changing LLM_PROVIDER — no code change required.
All clients are lazy so the backend starts cleanly before any key is set.
"""
from __future__ import annotations
from sentence_transformers import SentenceTransformer
from app.config import settings

EMBED_DIM = 384  # all-MiniLM-L6-v2 output dimension

_embed_model: SentenceTransformer | None = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(settings.embedding_model)
    return _embed_model


def embed(text: str) -> list[float]:
    return _get_embed_model().encode(text).tolist()


def embed_batch(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    model = _get_embed_model()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        vectors.extend(model.encode(texts[i : i + batch_size]).tolist())
    return vectors


def generate_answer(question: str, context: str) -> str:
    if settings.llm_provider == "openai":
        return _answer_openai(question, context)
    return _answer_anthropic(question, context)


def _answer_anthropic(question: str, context: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
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


def _answer_openai(question: str, context: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
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
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content or ""
