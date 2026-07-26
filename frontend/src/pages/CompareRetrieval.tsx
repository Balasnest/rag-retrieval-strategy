import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { GitCompare } from 'lucide-react'
import { api, type QueryResponse } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

function ResultColumn({ result, label }: { result: QueryResponse; label: string }) {
  const accentClass = label === 'Dense' ? 'border-blue-200 bg-blue-50' : 'border-orange-200 bg-orange-50'
  const badgeClass  = label === 'Dense' ? 'bg-blue-100 text-blue-800 border-blue-200' : 'bg-orange-100 text-orange-800 border-orange-200'

  return (
    <div className="flex-1 min-w-0 space-y-3">
      <div className={`flex items-center justify-between rounded-md border px-3 py-2 ${accentClass}`}>
        <span className={`text-xs font-semibold uppercase tracking-wide ${label === 'Dense' ? 'text-blue-700' : 'text-orange-700'}`}>
          {label} retrieval
        </span>
        <div className="flex gap-1.5">
          <Badge variant="outline" className={`text-xs ${badgeClass}`}>{result.latency_ms} ms</Badge>
          <Badge variant="outline" className={`text-xs ${badgeClass}`}>{result.chunks.length} chunks</Badge>
        </div>
      </div>

      {/* Answer */}
      <Card>
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-xs text-slate-500 font-normal">Answer</CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4 pt-0">
          <p className="text-sm text-slate-800 leading-relaxed">{result.answer}</p>
        </CardContent>
      </Card>

      {/* Chunks */}
      <div className="space-y-2">
        {result.chunks.map((chunk, i) => (
          <Card key={String(chunk.id)} className="border-slate-100">
            <CardHeader className="py-2 px-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-400">#{i + 1}</span>
                  {chunk.document_title && (
                    <Badge variant="outline" className="text-xs">{chunk.document_title}</Badge>
                  )}
                </div>
                <span className="text-xs tabular-nums text-slate-500">
                  {label === 'Dense'
                    ? `${(chunk.score * 100).toFixed(1)}% sim`
                    : `score ${chunk.score.toFixed(2)}`}
                </span>
              </div>
            </CardHeader>
            <CardContent className="px-3 pb-3 pt-0">
              <p className="text-xs text-slate-600 font-mono-code leading-relaxed line-clamp-4">
                {chunk.content}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export function CompareRetrieval() {
  const [question, setQuestion] = useState('')

  const compareMutation = useMutation({
    mutationFn: (q: string) => api.compare({ question: q, top_k: 5 }),
  })

  const result = compareMutation.data

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Compare Retrieval</h1>
        <p className="text-sm text-slate-500 mt-1">
          Same question — dense semantic search vs BM25 keyword search, side by side
        </p>
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && question.trim() && compareMutation.mutate(question)}
          placeholder="e.g. What is the sync conflict resolution process?"
          className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900"
        />
        <Button
          onClick={() => compareMutation.mutate(question)}
          disabled={!question.trim() || compareMutation.isPending}
        >
          <GitCompare size={14} />
          {compareMutation.isPending ? 'Comparing…' : 'Compare'}
        </Button>
      </div>

      {compareMutation.isError && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {(compareMutation.error as Error).message}
        </div>
      )}

      {/* Overlap badge */}
      {result && (
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm ${
            result.overlap_count > 0
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : 'border-slate-200 bg-slate-50 text-slate-500'
          }`}>
            <span className="font-semibold">{result.overlap_count}</span>
            <span className="text-xs">
              {result.overlap_count === 1 ? 'chunk' : 'chunks'} retrieved by both methods
            </span>
          </div>
          {result.overlap_count === 0 && (
            <span className="text-xs text-slate-400">Methods retrieved completely different chunks</span>
          )}
        </div>
      )}

      {/* Side-by-side columns */}
      {result && (
        <div className="flex gap-4">
          <ResultColumn result={result.dense} label="Dense" />
          <ResultColumn result={result.bm25}  label="BM25" />
        </div>
      )}
    </div>
  )
}
