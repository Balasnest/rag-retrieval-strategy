const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export interface StubResponse<T = unknown> {
  implemented: boolean
  phase_planned: string
  message: string
  data: T | null
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  return res.json()
}

export const api = {
  health: () => request<{ status: string; phase: number; message: string }>("/health"),

  // Every call below hits a real, live endpoint — it just returns a
  // StubResponse with implemented=false until its phase lands. The
  // frontend renders that state explicitly rather than pretending it's
  // real data (see components/StubNotice.tsx).
  listDocuments: () => request<StubResponse>("/documents"),
  listChunks: (documentId?: string) =>
    request<StubResponse>(`/chunks${documentId ? `?document_id=${documentId}` : ""}`),
  chunkDocument: (body: { document_id: string; chunk_size?: number; overlap?: number }) =>
    request<StubResponse>("/chunk", { method: "POST", body: JSON.stringify(body) }),
  buildIndex: (body: { reset?: boolean } = {}) =>
    request<StubResponse>("/index", { method: "POST", body: JSON.stringify(body) }),
  embed: (text: string) =>
    request<StubResponse>("/embed", { method: "POST", body: JSON.stringify({ text }) }),
  query: (body: { question: string; mode: string; top_k?: number }) =>
    request<StubResponse>("/query", { method: "POST", body: JSON.stringify(body) }),
  compare: (question: string) =>
    request<StubResponse>("/compare", { method: "POST", body: JSON.stringify({ question }) }),
  metrics: () => request<StubResponse>("/metrics", { method: "POST" }),
}
