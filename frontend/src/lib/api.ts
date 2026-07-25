const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

// ── Phase 2 types ────────────────────────────────────────────────────────────

export interface DocumentResponse {
  id: string
  filename: string
  title: string
  word_count: number
  chunk_count: number
  created_at: string
}

export interface ChunkResponse {
  id: string
  document_id: string
  content: string
  chunk_index: number
  strategy: string
  chunk_size: number | null
  overlap: number | null
  token_count: number
  created_at: string
}

export interface RechunkRequest {
  document_id: string
  strategy: string
  chunk_size?: number
  overlap?: number
}

// ── Stub type for Phase 3+ endpoints ────────────────────────────────────────

export interface StubResponse<T = unknown> {
  implemented: boolean
  phase_planned: string
  message: string
  data: T | null
}

// ── Fetch helper ─────────────────────────────────────────────────────────────

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, options)
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// ── API client ───────────────────────────────────────────────────────────────

export const api = {
  health: () =>
    request<{ status: string; phase: number; message: string }>("/health"),

  // Documents (Phase 2)
  uploadDocument: (file: File) => {
    const form = new FormData()
    form.append("file", file)
    return request<DocumentResponse>("/documents/upload", { method: "POST", body: form })
  },
  listDocuments: () => request<DocumentResponse[]>("/documents"),
  deleteDocument: (id: string) => request<void>(`/documents/${id}`, { method: "DELETE" }),

  // Chunks (Phase 2)
  listChunks: (documentId: string, strategy?: string) =>
    request<ChunkResponse[]>(
      `/chunks?document_id=${documentId}${strategy ? `&strategy=${strategy}` : ""}`
    ),
  rechunk: (body: RechunkRequest) =>
    request<ChunkResponse[]>("/chunk", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }),

  // Stubs — Phase 3+
  buildIndex: (body: { reset?: boolean } = {}) =>
    request<StubResponse>("/index", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }),
  query: (body: { question: string; mode: string; top_k?: number }) =>
    request<StubResponse>("/query", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }),
  compare: (question: string) =>
    request<StubResponse>("/compare", {
      method: "POST",
      body: JSON.stringify({ question }),
      headers: { "Content-Type": "application/json" },
    }),
  metrics: () =>
    request<StubResponse>("/metrics", { method: "POST" }),
}
