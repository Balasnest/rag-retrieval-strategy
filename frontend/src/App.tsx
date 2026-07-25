import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { DatasetExplorer } from '@/pages/DatasetExplorer'
import { ChunkExplorer } from '@/pages/ChunkExplorer'
import { RetrievalPlayground } from '@/pages/RetrievalPlayground'
import { CompareRetrieval } from '@/pages/CompareRetrieval'
import { MetricsDashboard } from '@/pages/MetricsDashboard'
import { Settings } from '@/pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dataset" replace />} />
          <Route path="dataset" element={<DatasetExplorer />} />
          <Route path="chunks" element={<ChunkExplorer />} />
          <Route path="retrieval" element={<RetrievalPlayground />} />
          <Route path="compare" element={<CompareRetrieval />} />
          <Route path="metrics" element={<MetricsDashboard />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
