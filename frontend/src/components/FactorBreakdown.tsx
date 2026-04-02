import { SiteScore } from '../store'

interface FactorBreakdownProps {
  factors: SiteScore['factors']
}

const factorLabels: Record<keyof SiteScore['factors'], string> = {
  population: 'Population',
  transport: 'Transport',
  competition: 'Competition',
  zoning: 'Zoning',
  risk: 'Risk (lower=worse)',
  demand: 'Demand',
}

const factorColors: Record<keyof SiteScore['factors'], string> = {
  population: 'from-blue-500 to-blue-400',
  transport: 'from-emerald-500 to-emerald-400',
  competition: 'from-amber-500 to-amber-400',
  zoning: 'from-purple-500 to-purple-400',
  risk: 'from-rose-500 to-rose-400',
  demand: 'from-cyan-500 to-cyan-400',
}

export function FactorBreakdown({ factors }: FactorBreakdownProps) {
  const entries = Object.entries(factors) as [keyof typeof factors, number][]

  return (
    <div className="p-4 rounded-lg bg-slate-700/50 border border-slate-600">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">Factor Breakdown</h3>
      <div className="space-y-3">
        {entries.map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-medium text-slate-400">
                {factorLabels[key]}
              </label>
              <span className="text-xs font-bold text-slate-200">{value}%</span>
            </div>
            <div className="w-full bg-slate-600 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${factorColors[key]} transition-all duration-500`}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
