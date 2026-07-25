import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type Strategy = 'fixed' | 'sentence' | 'paragraph'

const STRATEGIES: Strategy[] = ['fixed', 'sentence', 'paragraph']

export function ChunkExplorer() {
  const queryClient = useQueryClient()
  const [selectedDocId, setSelectedDocId] = useState('')
  const [strategy, setStrategy] = useState<Strategy>('fixed')
  const [chunkSize, setChunkSize] = useState(300)
  const [overlap, setOverlap] = useState(50)

  const { data: documents = [] } = useQuery({
    queryKey: ['documents'],
    queryFn: api.listDocuments,
  })

  const { data: chunks = [], isLoading: chunksLoading } = useQuery({
    queryKey: ['chunks', selectedDocId, strategy],
    queryFn: () => api.listChunks(selectedDocId, strategy),
    enabled: !!selectedDocId,
  })

  const rechunkMutation = useMutation({
    mutationFn: api.rechunk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chunks', selectedDocId, strategy] })
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const avgTokens = chunks.length
    ? Math.round(chunks.reduce((s, c) => s + c.token_count, 0) / chunks.length)
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Chunk Explorer</h1>
        <p className="text-sm text-slate-500 mt-1">
          Compare how different chunking strategies split your documents
        </p>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4 space-y-4">
          {/* Document selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-700">Document</label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900"
            >
              <option value="">Select a document…</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.title}
                </option>
              ))}
            </select>
          </div>

          {/* Strategy toggle */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-700">Chunking Strategy</label>
            <div className="flex gap-2">
              {STRATEGIES.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setStrategy(s)}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    strategy === s
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Fixed-only params */}
          {strategy === 'fixed' && (
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-700">
                  Chunk Size{' '}
                  <span className="font-normal text-slate-400">({chunkSize} tokens)</span>
                </label>
                <input
                  type="range"
                  min={50} max={800} step={50}
                  value={chunkSize}
                  onChange={(e) => setChunkSize(Number(e.target.value))}
                  className="w-full accent-slate-900"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-700">
                  Overlap{' '}
                  <span className="font-normal text-slate-400">({overlap} tokens)</span>
                </label>
                <input
                  type="range"
                  min={0} max={200} step={10}
                  value={overlap}
                  onChange={(e) => setOverlap(Number(e.target.value))}
                  className="w-full accent-slate-900"
                />
              </div>
            </div>
          )}

          <Button
            size="sm"
            onClick={() =>
              rechunkMutation.mutate({
                document_id: selectedDocId,
                strategy,
                ...(strategy === 'fixed' ? { chunk_size: chunkSize, overlap } : {}),
              })
            }
            disabled={!selectedDocId || rechunkMutation.isPending}
          >
            {rechunkMutation.isPending ? 'Chunking…' : 'Re-chunk'}
          </Button>
        </CardContent>
      </Card>

      {/* Chunk results */}
      {!selectedDocId ? (
        <p className="text-center text-sm text-slate-400 py-12">
          Select a document above to view its chunks
        </p>
      ) : chunksLoading ? (
        <p className="text-sm text-slate-400">Loading chunks…</p>
      ) : chunks.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-sm text-slate-500">
            No <span className="font-medium">{strategy}</span> chunks for this document yet.
          </p>
          <p className="text-xs text-slate-400 mt-1">Click Re-chunk to generate them.</p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-700">
              {chunks.length} chunks
              <span className="ml-2 font-normal text-slate-400">· {strategy} strategy</span>
            </p>
            <p className="text-xs text-slate-400">{avgTokens} avg tokens / chunk</p>
          </div>

          <div className="grid gap-3">
            {chunks.map((chunk) => (
              <Card key={chunk.id}>
                <CardHeader className="py-2 px-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xs text-slate-400 font-normal">
                      Chunk {chunk.chunk_index + 1}
                    </CardTitle>
                    <Badge variant="outline">{chunk.token_count} tokens</Badge>
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
