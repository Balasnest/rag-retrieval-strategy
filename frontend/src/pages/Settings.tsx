import { StubNotice } from '@/components/StubNotice'

export function Settings() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">
          Configure embedding models, retrieval parameters, and API keys
        </p>
      </div>
      <StubNotice
        phasePlanned="Phase 3 — Dense retrieval with pgvector"
        message="Settings will be configurable once the embedding and retrieval pipeline is built. Not built yet."
      />
    </div>
  )
}
