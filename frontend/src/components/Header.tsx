import { Globe2, Zap } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-slate-700 px-6 py-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg">
            <Globe2 size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              GeoSpatial Analyzer
              <Zap size={20} className="text-amber-400" />
            </h1>
            <p className="text-xs text-slate-400">AI-Powered Site Readiness Evaluation</p>
          </div>
        </div>
        <div className="text-sm text-slate-400">
          <span className="inline-flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            System Online
          </span>
        </div>
      </div>
    </header>
  )
}
