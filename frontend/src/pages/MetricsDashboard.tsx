import { StubNotice } from '@/components/StubNotice'

export function MetricsDashboard() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Metrics Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Aggregate latency, retrieval overlap, and query statistics across sessions
        </p>
      </div>
      <StubNotice
        phasePlanned="Phase 5 — Hybrid comparison"
        message="This page will display retrieval performance metrics once both dense and BM25 paths are built. Not built yet."
      />
    </div>
  )
}
