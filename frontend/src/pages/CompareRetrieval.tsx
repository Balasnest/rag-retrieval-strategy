import { StubNotice } from '@/components/StubNotice'

export function CompareRetrieval() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Compare Retrieval</h1>
        <p className="text-sm text-slate-500 mt-1">
          Run the same question through dense and BM25 retrieval side by side
        </p>
      </div>
      <StubNotice
        phasePlanned="Phase 5 — Hybrid comparison"
        message="This page will show pgvector vs. Elasticsearch BM25 results side by side with overlap analysis. Not built yet."
      />
    </div>
  )
}
