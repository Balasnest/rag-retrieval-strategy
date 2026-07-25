"""
Three chunking strategies used by Phase 2.

All three return list[str] with the same interface so callers can
swap strategies without changing how they store or count chunks.
"""
import re
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def token_count(text: str) -> int:
    return len(_enc.encode(text))


def chunk_fixed(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Slide a window of chunk_size tokens across the text, stepping back
    by overlap tokens each iteration so context at boundaries is preserved."""
    tokens = _enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(_enc.decode(tokens[start:end]))
        if end >= len(tokens):
            break
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]


def chunk_sentence(text: str, max_tokens: int = 150) -> list[str]:
    """Split on sentence boundaries (.!?), then group sentences until
    max_tokens is reached. Prevents micro-chunks from very short sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        t = token_count(sentence)
        if current_tokens + t > max_tokens and current:
            chunks.append(" ".join(current))
            current = [sentence]
            current_tokens = t
        else:
            current.append(sentence)
            current_tokens += t

    if current:
        chunks.append(" ".join(current))

    return [c for c in chunks if c.strip()]


def chunk_paragraph(text: str) -> list[str]:
    """Split on blank lines. Each non-empty paragraph becomes one chunk."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]
