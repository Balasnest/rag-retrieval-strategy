# RAG Retrieval Strategy — Learning Plan

This document captures the *why* behind every build decision, phase by phase.
The goal is not just to ship features but to build a working mental model of
how RAG systems are constructed and where each component fits.

---

## Phase 0 — Project Scaffold
**Status:** ✅ Done

### What was built
- Folder structure: `backend/`, `frontend/`, `sample_data/`, `docs/`, `scripts/`
- `docker-compose.yml` with four services: Postgres (pgvector image), Elasticsearch, FastAPI backend, Vite frontend
- `.env` / `.env.example` for secrets
- `.gitignore` excluding `.env`, `node_modules`, `__pycache__`, `.claude/`

### Concepts introduced
| Concept | Why it matters here |
|---------|---------------------|
| Docker Compose multi-service setup | All three data stores (Postgres, Elasticsearch, app) need to talk to each other on a private network — Compose handles that without manual networking |
| `pgvector` image vs plain Postgres | pgvector adds a vector column type and ANN index operators; using it from the start avoids a painful migration later |
| Health checks on services | The backend `depends_on` with `condition: service_healthy` prevents race conditions where FastAPI boots before Postgres is ready |
| `.env.example` pattern | Keeps secrets out of git while documenting every required variable |

---

## Phase 1 — React UI + FastAPI Skeleton
**Status:** ✅ Done (frontend shell deferred — completed in Phase 2)

### What was built
**Backend**
- FastAPI app with CORS, config via env vars, `/health` endpoint
- Stub routers for every planned endpoint: `/documents`, `/chunks`, `/chunk`, `/query`, `/compare`, `/index`, `/embed`, `/metrics`
- `StubResponse` schema: a uniform envelope (`implemented`, `phase_planned`, `message`, `data`) so the frontend can wire real UI before real logic exists
- SQLAlchemy engine + session factory — configured but not yet queried

**Frontend**
- Vite + React + TypeScript project
- Tailwind CSS + shadcn/ui component primitives installed
- TanStack Query installed
- `lib/api.ts` — typed fetch client with one function per endpoint
- `lib/utils.ts` — `cn()` helper for conditional Tailwind classes
- `components/ui/` — Button, Card, Badge
- `components/StubNotice.tsx` — renders when `implemented === false`

### Concepts introduced
| Concept | Why it matters here |
|---------|---------------------|
| Stub contract pattern | Lets UI and backend evolve in parallel; the `StubResponse` envelope is a real API shape, not a mock — the frontend learns to handle "not built yet" as a first-class state |
| SQLAlchemy `pool_pre_ping` | Sends a cheap probe before reusing a pooled connection; guards against stale connections after Postgres restarts |
| TanStack Query | Manages server state (loading / error / stale / refetch) so page components stay focused on rendering, not fetch lifecycle |
| shadcn/ui | Components are copied into the repo (not a runtime dependency) — you own and can modify every pixel |

---

## Phase 2 — Document Ingestion + Chunking
**Status:** 🔄 In progress

### Goal
Upload `.txt` documents, store them in Postgres, chunk them three different
ways, and visualize the difference — all without embeddings or search yet.

### What will be built

#### Backend

**`app/models/document.py`**
```
Document
  id            UUID  PK
  filename      str
  title         str
  raw_text      str   (full document text)
  word_count    int
  created_at    datetime
```

**`app/models/chunk.py`**
```
Chunk
  id            UUID  PK
  document_id   UUID  FK → Document.id  (cascade delete)
  content       str
  chunk_index   int   (order within document)
  strategy      str   ("fixed" | "sentence" | "paragraph")
  chunk_size    int   (target size used; null for sentence/paragraph)
  overlap       int   (overlap used; null for sentence/paragraph)
  token_count   int   (actual token count via tiktoken)
  vector        nullable  (placeholder; populated in Phase 3)
  created_at    datetime
```

**`app/core/chunker.py`** — three strategies, same interface
- `fixed(text, chunk_size, overlap)` — uses `tiktoken` to count tokens, slides a window of `chunk_size` tokens with `overlap` step-back
- `sentence(text)` — regex split on `.`, `!`, `?` boundaries; merges short sentences to avoid micro-chunks
- `paragraph(text)` — split on `\n\n`; trims whitespace; drops empty blocks

**Real endpoints replacing stubs**
| Method | Path | What it does |
|--------|------|--------------|
| `POST` | `/documents/upload` | Multipart `.txt` upload → parse → store Document + default chunks |
| `GET` | `/documents` | List all documents with word count + chunk count |
| `DELETE` | `/documents/{id}` | Remove document + all its chunks (cascade) |
| `GET` | `/chunks` | List chunks filtered by `document_id` and/or `strategy` |
| `POST` | `/chunk` | Re-chunk a document with new strategy/size → replace existing chunks |

**New dependency:** `python-multipart` (FastAPI file upload requirement)

#### Frontend

**Finish Phase 1 shell (deferred)**
- `main.tsx` — wrap in `QueryClientProvider`
- `App.tsx` — replace Vite default with sidebar layout + `react-router-dom` routes

**`src/components/layout/Sidebar.tsx`**
- Nav links to all 6 sections with active-state highlight

**`src/pages/DatasetExplorer.tsx`**
- File dropzone (`.txt`)
- Document table: filename, word count, chunk count, upload date, delete button
- On upload: `POST /documents/upload` → invalidate document list query

**`src/pages/ChunkExplorer.tsx`**
- Document selector dropdown
- Strategy toggle: `fixed` / `sentence` / `paragraph`
- Chunk size + overlap sliders (enabled only for `fixed` strategy)
- "Re-chunk" button → `POST /chunk` → refresh chunk list
- Chunk cards: index number, token count badge, content text

**Remaining pages stay as stubs** — Retrieval Playground, Compare Retrieval, Metrics Dashboard, Settings

**`api.ts` additions**
```ts
uploadDocument(file: File): Promise<DocumentResponse>
listDocuments(): Promise<DocumentResponse[]>
deleteDocument(id: string): Promise<void>
listChunks(documentId: string, strategy?: string): Promise<ChunkResponse[]>
rechunk(body: RechunkRequest): Promise<ChunkResponse[]>
```

#### Sample data
Three `.txt` files in `sample_data/` (~1000 words each):
- `product_manual.txt` — structured with headers and lists (tests paragraph chunking)
- `policy_document.txt` — dense prose (tests sentence chunking)
- `technical_article.txt` — mixed code references and explanation (tests fixed chunking)

### Concepts introduced
| Concept | Why it matters here |
|---------|---------------------|
| Chunking strategy comparison | The core thesis of this app: different strategies produce very different chunk shapes — fixed gives uniform size, sentence preserves semantic boundaries, paragraph mirrors document structure |
| Token counting with tiktoken | Embedding models have token limits; counting by tokens (not characters) gives accurate size estimates that match what the model will see |
| Overlap in fixed chunking | Overlap ensures context at chunk boundaries isn't lost — a sentence split across two chunks is partially present in both |
| Cascade delete | Deleting a document must remove its chunks atomically; SQLAlchemy `cascade="all, delete-orphan"` handles this at the ORM level |
| Multipart file upload in FastAPI | `UploadFile` + `python-multipart` is the FastAPI pattern; file bytes are streamed, not loaded whole into memory |
| TanStack Query cache invalidation | After upload or rechunk, `queryClient.invalidateQueries()` triggers a refetch — the UI stays in sync without manual state management |

### Deliverable checkpoint
> Docker Compose up → visit localhost:5173 → upload a `.txt` file →
> see it in Dataset Explorer → open Chunk Explorer → toggle between
> `fixed / sentence / paragraph` → chunk cards update in real time.
> No embeddings. No search. Just chunking.

---

## Phase 3 — Dense Retrieval with pgvector
**Status:** ⬜ Not started

### Goal
Embed every chunk using OpenAI `text-embedding-3-small`, store vectors in
Postgres, and answer questions by finding the nearest neighbour chunks.

### What will be built (preview)
- Populate the `vector` column on `Chunk` using the OpenAI Embeddings API
- `POST /index` — embed all chunks for a document and store vectors
- `POST /query` — embed the question, run `<=>` cosine similarity search via pgvector, return top-k chunks + the LLM answer
- Retrieval Playground page goes live

### Concepts introduced (preview)
| Concept | Why it matters here |
|---------|---------------------|
| Dense embeddings | Map text to a point in high-dimensional space; semantically similar text lands nearby regardless of exact word overlap |
| pgvector `<=>` operator | Cosine distance in SQL — enables ANN search inside Postgres without a separate vector DB |
| HNSW index | Approximate Nearest Neighbour index that makes vector search sub-linear; created with `CREATE INDEX ... USING hnsw` |
| Embedding batch size limits | OpenAI embeddings API has per-request token limits; chunking (Phase 2) directly controls whether you can embed in one call or must batch |

---

## Phase 4 — BM25 with Elasticsearch
**Status:** ⬜ Not started

### Goal
Index the same documents in Elasticsearch and answer questions using
keyword-based BM25 retrieval — no embeddings involved.

### What will be built (preview)
- `POST /index` extended to also index chunks in Elasticsearch
- `POST /query` extended with `mode=bm25` to hit Elasticsearch instead
- BM25 retrieval path returns top-k chunks + LLM answer

### Concepts introduced (preview)
| Concept | Why it matters here |
|---------|---------------------|
| BM25 | Probabilistic keyword ranking: scores chunks by term frequency (TF) + inverse document frequency (IDF) — exact word matches score high |
| BM25 vs dense retrieval | Dense retrieval wins on paraphrase and semantic similarity; BM25 wins on exact keyword matches and named entities — the comparison in Phase 5 makes this visible |
| Elasticsearch mappings | Defines how text fields are analyzed (tokenized, stemmed, lowercased) before indexing — affects what queries will match |

---

## Phase 5 — Hybrid Comparison Page
**Status:** ⬜ Not started

### Goal
Run the same question through both retrieval paths simultaneously and display
the results side by side with overlap analysis and latency metrics.

### What will be built (preview)
- `POST /compare` — fan out to both pgvector and Elasticsearch, merge results, return unified response
- Compare Retrieval page: side-by-side chunk lists, overlap badge, latency bar
- Metrics Dashboard: aggregate stats across sessions (avg latency, avg overlap, top queries)

### Concepts introduced (preview)
| Concept | Why it matters here |
|---------|---------------------|
| Hybrid retrieval | Combining dense + sparse signals often outperforms either alone; Reciprocal Rank Fusion (RRF) is the standard merging strategy |
| Retrieval overlap analysis | Chunks that appear in both results are strong candidates; chunks unique to one method reveal where the strategies diverge |
| Latency as a first-class metric | Dense search requires an embedding API call (network round-trip); BM25 is local — latency difference is significant and measurable |

---

## Running the project

```bash
# Start all services
docker compose up --build

# Backend only (for fast iteration)
cd backend && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm run dev
```

URLs:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Elasticsearch: http://localhost:9200
