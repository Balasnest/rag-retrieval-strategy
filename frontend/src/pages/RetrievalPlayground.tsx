import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Search, Zap } from 'lucide-react'
import { api, type ChunkResult } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function RetrievalPlayground() {
  const [question, setQuestion] = useState('')
  const [selectedDocId, setSelectedDocId] = useState('')
  const [result, setResult] = useState<{ answer: string; chunks: ChunkResult[]; latency_ms: number } | null>(null)

  const { data: documents = [] } = useQuery({
    queryKey: ['documents'],
    queryFn: api.listDocuments,
  })

  const indexMutation = useMutation({
    mutationFn: () => api.buildIndex({ document_id: selectedDocId || undefined }),
  })

  const queryMutation = useMutation({
    mutationFn: () => api.query({ question, top_k: 5 }),
    onSuccess: (data) => setResult(data),
  })

  const handleSearch = () => {
    if (question.trim()) queryMutation.mutate()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Retrieval Playground</h1>
        <p className="text-sm text-slate-500 mt-1">
          Dense semantic search — embed your documents, then ask questions
        </p>
      </div>

      {/* Step 1 — Index */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-xs text-white font-bold">1</span>
            Index documents
          </CardTitle>
          <CardDescription>
            Embed chunks using OpenAI text-embedding-3-small and store vectors in pgvector
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center gap-3">
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="flex-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900"
          >
            <option value="">All documents</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>{doc.title}</option>
            ))}
          </select>
          <Button
            variant="outline"
            onClick={() => indexMutation.mutate()}
            disabled={indexMutation.isPending}
          >
            <Zap size={14} />
            {indexMutation.isPending ? 'Indexing…' : 'Build Index'}
          </Button>
          {indexMutation.isSuccess && (
            <span className="text-xs text-emerald-600 font-medium">
              ✓ {indexMutation.data.indexed} embedded
              {indexMutation.data.already_embedded > 0 &&
                `, ${indexMutation.data.already_embedded} already done`}
            </span>
          )}
          {indexMutation.isError && (
            <span className="text-xs text-red-600">
              {(indexMutation.error as Error).message}
            </span>
          )}
        </CardContent>
      </Card>

      {/* Step 2 — Ask */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-xs text-white font-bold">2</span>
            Ask a question
          </CardTitle>
          <CardDescription>
            Your question is embedded and matched against stored chunk vectors by cosine similarity
          </CardDescription>
        </CardHeader>
        <CardContent className="flex gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g. How do I resolve a sync conflict?"
            className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900"
          />
          <Button onClick={handleSearch} disabled={!question.trim() || queryMutation.isPending}>
            <Search size={14} />
            {queryMutation.isPending ? 'Searching…' : 'Search'}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {queryMutation.isError && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {(queryMutation.error as Error).message}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Answer */}
          <Card className="border-slate-200">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Answer</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{result.latency_ms} ms</Badge>
                  <Badge variant="outline">dense</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-800 leading-relaxed">{result.answer}</p>
            </CardContent>
          </Card>

          {/* Source chunks */}
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Source chunks ({result.chunks.length})
            </p>
            {result.chunks.map((chunk, i) => (
              <Card key={chunk.id} className="border-slate-100">
                <CardHeader className="py-2 px-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">#{i + 1}</span>
                      {chunk.document_title && (
                        <Badge variant="outline" className="text-xs">{chunk.document_title}</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">{chunk.token_count} tokens</span>
                      <Badge
                        variant={chunk.score > 0.8 ? 'success' : 'secondary'}
                        className="tabular-nums"
                      >
                        {(chunk.score * 100).toFixed(1)}% match
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="px-4 pb-4 pt-0">
                  <p className="text-sm text-slate-700 font-mono-code leading-relaxed whitespace-pre-wrap">
                    {chunk.content}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
