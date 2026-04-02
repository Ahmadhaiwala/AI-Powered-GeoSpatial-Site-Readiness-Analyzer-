import { Location } from '../store'
import { Brain, ChevronDown, ChevronUp, Lightbulb, Loader2, X } from 'lucide-react'
import { useState } from 'react'
import { useMapStore } from '../store'

interface ExplanationPanelProps {
  location: Location
}

export function ExplanationPanel({ location }: ExplanationPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const toggleExplanation = useMapStore((s) => s.toggleExplanation)
  const isLoading = useMapStore((s) => s.isLoading)

  const { score, explanation } = location.score ?? {}

  return (
    <div
      // Stop ALL pointer events from reaching the Leaflet map below
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
      onPointerDown={(e) => e.stopPropagation()}
      style={{ zIndex: 1000, pointerEvents: 'auto' }}
      className="absolute bottom-4 right-4 w-[300px] rounded-xl shadow-2xl overflow-hidden border border-white/10"
    >
      {/* Glass header */}
      <div
        onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded) }}
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
        style={{ background: 'rgba(15,23,42,0.92)', backdropFilter: 'blur(12px)' }}
      >
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-emerald-400" />
          <span className="text-sm font-semibold text-white">AI Insights</span>
          {score !== undefined && (
            <span
              className="px-2 py-0.5 rounded-full text-[11px] font-bold"
              style={{
                background: score >= 70 ? '#065f46' : score >= 50 ? '#1e3a8a' : '#7f1d1d',
                color: score >= 70 ? '#6ee7b7' : score >= 50 ? '#93c5fd' : '#fca5a5',
              }}
            >
              {score}/100
            </span>
          )}
          {isLoading && <Loader2 size={12} className="animate-spin text-slate-400" />}
        </div>
        <div className="flex items-center gap-1">
          {isExpanded
            ? <ChevronUp size={15} className="text-slate-400" />
            : <ChevronDown size={15} className="text-slate-400" />}
          <button
            onClick={(e) => { e.stopPropagation(); toggleExplanation() }}
            className="ml-1 p-0.5 rounded hover:bg-white/10 text-slate-500 hover:text-white transition-colors"
          >
            <X size={13} />
          </button>
        </div>
      </div>

      {/* Body */}
      {isExpanded && (
        <div
          className="px-3 pt-3 pb-3 space-y-2 max-h-64 overflow-y-auto"
          style={{ background: 'rgba(15,23,42,0.88)', backdropFilter: 'blur(12px)' }}
        >
          {/* Loading state */}
          {isLoading && !score && (
            <div className="flex items-center justify-center gap-2 py-4 text-slate-400">
              <Loader2 size={14} className="animate-spin text-emerald-400" />
              <span className="text-xs">Evaluating location…</span>
            </div>
          )}

          {/* Score bar */}
          {score !== undefined && (
            <div className="mb-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs text-slate-400">Site Readiness</span>
                <span className="text-xs font-bold text-white">{score}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-700 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${score}%`,
                    background: score >= 70
                      ? 'linear-gradient(90deg, #10b981, #34d399)'
                      : score >= 50
                        ? 'linear-gradient(90deg, #3b82f6, #60a5fa)'
                        : 'linear-gradient(90deg, #ef4444, #f87171)',
                  }}
                />
              </div>
            </div>
          )}

          {/* Strengths */}
          {explanation?.strengths && explanation.strengths.length > 0 && (
            <div className="rounded-lg overflow-hidden border border-emerald-900/60">
              <div className="px-3 py-1.5 bg-emerald-950/60">
                <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Strengths</span>
              </div>
              <ul className="px-3 py-2 space-y-1">
                {explanation.strengths.map((s, i) => (
                  <li key={i} className="text-xs text-slate-300 leading-relaxed">{s}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {explanation?.weaknesses && explanation.weaknesses.length > 0 && (
            <div className="rounded-lg overflow-hidden border border-amber-900/60">
              <div className="px-3 py-1.5 bg-amber-950/60">
                <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">Weaknesses</span>
              </div>
              <ul className="px-3 py-2 space-y-1">
                {explanation.weaknesses.map((w, i) => (
                  <li key={i} className="text-xs text-slate-300 leading-relaxed">{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggestions */}
          {explanation?.suggestions && explanation.suggestions.length > 0 && (
            <div className="rounded-lg overflow-hidden border border-blue-900/60">
              <div className="px-3 py-1.5 bg-blue-950/60 flex items-center gap-1">
                <Lightbulb size={11} className="text-blue-400" />
                <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider">Suggestions</span>
              </div>
              <ul className="px-3 py-2 space-y-1">
                {explanation.suggestions.map((s, i) => (
                  <li key={i} className="text-xs text-slate-300 leading-relaxed">{s}</li>
                ))}
              </ul>
            </div>
          )}

          {!isLoading && !explanation && (
            <p className="text-xs text-slate-500 text-center py-3">
              Click on the map to evaluate a location.
            </p>
          )}

          <p className="text-[10px] text-slate-600 text-center pt-1">
            Powered by real Ahmedabad OSM data
          </p>
        </div>
      )}
    </div>
  )
}
