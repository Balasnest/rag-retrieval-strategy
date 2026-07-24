# RAG Explorer

An **educational RAG debugger**, not a chatbot. Every stage of retrieval —
chunking, embedding, dense search, BM25, hybrid fusion, prompt
construction — is visible and inspectable in the UI, so you can see
*why* an answer was retrieved (or wasn't).

This is a learning tool, not a production system.

## Stack
- **Frontend**: React (Vite) + TypeScript + Tailwind + shadcn/ui + TanStack Query + Recharts
- **Backend**: FastAPI + SQLAlchemy
- **Storage**: PostgreSQL + pgvector (dense vectors) + Elasticsearch (BM25)
- **LLM**: OpenAI API (embeddings + chat)
- **Infra**: Docker Compose

## Structure
```
/backend        FastAPI app, SQLAlchemy models, retrieval logic
/frontend       React + Vite + TS app
/docker-compose.yml
/scripts        data generation / indexing scripts
/sample_data    generated synthetic enterprise knowledge base
/docs           phase plan, architecture notes
```

## Running it
```
cp .env.example .env   # add your OPENAI_API_KEY
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend docs (Swagger): http://localhost:8000/docs

## Build plan
This project is being built **incrementally, in confirmed phases** — see
[`docs/PHASES.md`](docs/PHASES.md) for what's done and what's next.

1. React UI + FastAPI skeleton
2. Document ingestion + chunking
3. Dense retrieval with pgvector
4. BM25 with Elasticsearch
5. Hybrid comparison page
