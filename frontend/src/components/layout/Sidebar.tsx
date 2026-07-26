import { NavLink } from 'react-router-dom'
import { Database, Scissors, Search, GitCompare, BarChart2, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/dataset',   icon: Database,    label: 'Dataset Explorer' },
  { to: '/chunks',    icon: Scissors,    label: 'Chunk Explorer' },
  { to: '/retrieval', icon: Search,      label: 'Retrieval Playground' },
  { to: '/compare',   icon: GitCompare,  label: 'Compare Retrieval' },
  { to: '/metrics',   icon: BarChart2,   label: 'Metrics Dashboard' },
  { to: '/settings',  icon: Settings,    label: 'Settings' },
]

export function Sidebar() {
  return (
    <aside className="w-56 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col">
      <div className="p-4 border-b border-slate-200">
        <h1 className="text-sm font-semibold text-slate-900">RAG Explorer</h1>
        <p className="text-xs text-slate-400 mt-0.5">Retrieval Strategy Lab</p>
      </div>
      <nav className="flex-1 p-2 space-y-0.5">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-slate-100">
        <p className="text-xs text-slate-300">Phase 4 — BM25 + Compare</p>
      </div>
    </aside>
  )
}
