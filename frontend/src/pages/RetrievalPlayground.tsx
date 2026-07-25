import { StubNotice } from '@/components/StubNotice'

export function RetrievalPlayground() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Retrieval Playground</h1>
        <p className="text-sm text-slate-500 mt-1">
          Ask questions and retrieve relevant chunks using dense semantic search
        </p>
      </div>
      <StubNotice
        phasePlanned="Phase 3 — Dense retrieval with pgvector"
        message="This page will let you query documents using OpenAI embeddings + pgvector ANN search. Not built yet."
      />
    </div>
  )
}
