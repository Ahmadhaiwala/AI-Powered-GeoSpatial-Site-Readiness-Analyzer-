import { Location } from '../store'
import { TrendingUp } from 'lucide-react'

interface ScoreCardProps {
  location: Location
}

export function ScoreCard({ location }: ScoreCardProps) {
  if (!location.score) return null

  const score = location.score.score
  let scoreColor = 'text-emerald-400'
  let bgColor = 'bg-emerald-900/30'
  let borderColor = 'border-emerald-700'

  if (score < 40) {
    scoreColor = 'text-red-400'
    bgColor = 'bg-red-900/30'
    borderColor = 'border-red-700'
  } else if (score < 60) {
    scoreColor = 'text-amber-400'
    bgColor = 'bg-amber-900/30'
    borderColor = 'border-amber-700'
  } else if (score < 80) {
    scoreColor = 'text-blue-400'
    bgColor = 'bg-blue-900/30'
    borderColor = 'border-blue-700'
  }

  return (
    <div className={`p-4 rounded-lg border ${borderColor} ${bgColor}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-1">{location.name}</h3>
          <p className="text-xs text-slate-500">{location.businessType}</p>
        </div>
        <TrendingUp size={20} className="text-slate-400" />
      </div>

      <div className="flex items-baseline gap-2">
        <span className={`text-4xl font-bold ${scoreColor}`}>{score}</span>
        <span className="text-slate-400 text-sm">/100</span>
      </div>

      <div className="mt-3 w-full bg-slate-700 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ease-out ${scoreColor.replace('text', 'bg')}`}
          style={{ width: `${score}%` }}
        />
      </div>

      <p className="text-xs text-slate-400 mt-3">
        {score >= 80 && '✓ Excellent site potential'}
        {score >= 60 && score < 80 && '~ Good site potential'}
        {score >= 40 && score < 60 && '⚠ Moderate site potential'}
        {score < 40 && '✗ Poor site potential'}
      </p>
    </div>
  )
}
