import { Location } from '../store'
import { MapPin, ChevronDown, ChevronUp, Loader2, AlertCircle, X, Star } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useMapStore } from '../store'
import { api, type RecommendedLocation } from '../lib/api'

interface RecommendationsListProps {
  location: Location
}

export function RecommendationsList({ location }: RecommendationsListProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [results, setResults] = useState<RecommendedLocation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const businessType = useMapStore((s) => s.businessType)
  const toggleRecommendations = useMapStore((s) => s.toggleRecommendations)

  useEffect(() => {
    if (!location) return
    const delta = 0.05
    setLoading(true)
    setError(null)
    setResults([])

    api
      .recommend(
        businessType,
        location.lat - delta,
        location.lat + delta,
        location.lng - delta,
        location.lng + delta,
        10,
      )
      .then((res) => setResults(res.locations))
      .catch((err) => {
        console.error('Recommend error:', err)
        setError('Could not fetch recommendations.')
      })
      .finally(() => setLoading(false))
  }, [location.lat, location.lng, businessType])

  const scoreGradient = (score: number) => {
    if (score >= 75) return 'from-emerald-500 to-emerald-400'
    if (score >= 55) return 'from-blue-500 to-blue-400'
    if (score >= 40) return 'from-amber-500 to-amber-400'
    return 'from-red-500 to-red-400'
  }

  const scoreTextColor = (score: number) => {
    if (score >= 75) return 'text-emerald-400'
    if (score >= 55) return 'text-blue-400'
    if (score >= 40) return 'text-amber-400'
    return 'text-red-400'
  }

  return (
    <div
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
      onPointerDown={(e) => e.stopPropagation()}
      style={{ zIndex: 1000, pointerEvents: 'auto' }}
      className="absolute bottom-4 left-4 w-[300px] rounded-xl shadow-2xl overflow-hidden border border-white/10"
    >
      {/* Header */}
      <div
        onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded) }}
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
        style={{ background: 'rgba(15,23,42,0.92)', backdropFilter: 'blur(12px)' }}
      >
        <div className="flex items-center gap-2">
          <MapPin size={16} className="text-emerald-400" />
          <span className="text-sm font-semibold text-white">Top Locations</span>
          {results.length > 0 && !loading && (
            <span className="px-1.5 py-0.5 rounded-full bg-slate-700 text-slate-300 text-[11px] font-medium">
              {results.length}
            </span>
          )}
          {loading && <Loader2 size={12} className="animate-spin text-slate-400" />}
        </div>
        <div className="flex items-center gap-1">
          {isExpanded
            ? <ChevronUp size={15} className="text-slate-400" />
            : <ChevronDown size={15} className="text-slate-400" />}
          <button
            onClick={(e) => { e.stopPropagation(); toggleRecommendations() }}
            className="ml-1 p-0.5 rounded hover:bg-white/10 text-slate-500 hover:text-white transition-colors"
          >
            <X size={13} />
          </button>
        </div>
      </div>

      {/* Body */}
      {isExpanded && (
        <div
          className="px-3 pt-2 pb-3 space-y-1.5 max-h-72 overflow-y-auto"
          style={{ background: 'rgba(15,23,42,0.88)', backdropFilter: 'blur(12px)' }}
        >
          {loading && (
            <div className="flex flex-col items-center justify-center gap-2 py-6 text-slate-400">
              <Loader2 size={20} className="animate-spin text-emerald-500" />
              <span className="text-xs">Scanning area for best locations…</span>
            </div>
          )}

          {error && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-red-950/50 border border-red-900/60 text-red-400">
              <AlertCircle size={13} className="mt-0.5 flex-shrink-0" />
              <p className="text-xs leading-relaxed">{error}</p>
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <p className="text-center text-xs text-slate-500 py-5">No results found nearby.</p>
          )}

          {results.map((rec, idx) => (
            <div
              key={rec.h3_index}
              className="rounded-lg p-2.5 border border-white/5 transition-all hover:border-white/10"
              style={{ background: 'rgba(30,41,59,0.7)' }}
            >
              <div className="flex items-center justify-between gap-2">
                {/* Rank badge */}
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                      idx === 0 ? 'bg-yellow-500 text-yellow-950' : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {idx === 0 ? <Star size={11} /> : rec.rank}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-slate-200 font-medium truncate">
                      {rec.lat.toFixed(4)}, {rec.lng.toFixed(4)}
                    </p>
                    <p className="text-[10px] text-slate-500 font-mono truncate">
                      {rec.h3_index.slice(0, 12)}…
                    </p>
                  </div>
                </div>

                {/* Score pill */}
                <div className="flex flex-col items-end flex-shrink-0">
                  <span className={`text-base font-bold leading-none ${scoreTextColor(rec.score)}`}>
                    {rec.score}
                  </span>
                  {/* Mini bar */}
                  <div className="w-12 h-1 rounded-full bg-slate-700 mt-1 overflow-hidden">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${scoreGradient(rec.score)}`}
                      style={{ width: `${rec.score}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}

          {!loading && results.length > 0 && (
            <p className="text-[10px] text-slate-600 text-center pt-1">
              Showing top {results.length} spots for{' '}
              <span className="text-slate-400">{businessType.replace(/_/g, ' ')}</span>
            </p>
          )}
        </div>
      )}
    </div>
  )
}
