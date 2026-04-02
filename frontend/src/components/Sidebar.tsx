import { useState } from 'react'
import { useMapStore } from '../store'
import { ScoreCard } from './ScoreCard'
import { BusinessTypeSelector } from './BusinessTypeSelector'
import { FactorBreakdown } from './FactorBreakdown'
import { ControlPanel } from './ControlPanel'
import { ChevronRight, ChevronLeft } from 'lucide-react'

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const selectedLocation = useMapStore((state) => state.selectedLocation)
  const isLoading = useMapStore((state) => state.isLoading)

  return (
    <div className={`bg-slate-800 border-l border-slate-700 shadow-xl transition-all duration-300 flex flex-col overflow-hidden ${isCollapsed ? 'w-16' : 'w-80'}`}>
      {/* Header with toggle */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        {!isCollapsed && <h2 className="text-lg font-semibold text-white">Analysis</h2>}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors"
        >
          {isCollapsed ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {isCollapsed ? (
          <div className="p-2 flex flex-col gap-2">
            <div className="w-full h-12 bg-slate-700 rounded-lg animate-pulse"></div>
            <div className="w-full h-12 bg-slate-700 rounded-lg animate-pulse"></div>
            <div className="w-full h-12 bg-slate-700 rounded-lg animate-pulse"></div>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            <BusinessTypeSelector />

            {selectedLocation ? (
              <>
                {isLoading && (
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <div className="text-center">
                      <div className="inline-block">
                        <div className="w-8 h-8 border-4 border-slate-500 border-t-emerald-500 rounded-full animate-spin"></div>
                      </div>
                      <p className="text-sm text-slate-300 mt-2">Evaluating location...</p>
                    </div>
                  </div>
                )}
                {selectedLocation.score && (
                  <>
                    <ScoreCard location={selectedLocation} />
                    <FactorBreakdown factors={selectedLocation.score.factors} />
                  </>
                )}
              </>
            ) : (
              <div className="p-6 bg-slate-700 rounded-lg text-center">
                <p className="text-slate-300 text-sm">Click on the map to evaluate a location</p>
              </div>
            )}

            <ControlPanel />
          </div>
        )}
      </div>
    </div>
  )
}
