import { useMapStore } from '../store'
import { Lightbulb, Navigation, Trash2, MessageCircle } from 'lucide-react'

export function ControlPanel() {
  const selectedLocation = useMapStore((state) => state.selectedLocation)
  const showExplanation = useMapStore((state) => state.showExplanation)
  const showRecommendations = useMapStore((state) => state.showRecommendations)
  const showChat = useMapStore((state) => state.showChat)
  const toggleExplanation = useMapStore((state) => state.toggleExplanation)
  const toggleRecommendations = useMapStore((state) => state.toggleRecommendations)
  const toggleChat = useMapStore((state) => state.toggleChat)
  const clearLocations = useMapStore((state) => state.clearLocations)
  const locations = useMapStore((state) => state.locations)

  return (
    <div className="space-y-2">
      {selectedLocation && (
        <>
          <button
            onClick={toggleExplanation}
            className={`w-full p-2.5 rounded-lg flex items-center gap-2 font-medium text-sm transition-all ${
              showExplanation
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Lightbulb size={18} />
            <span>AI Insights</span>
          </button>

          <button
            onClick={toggleRecommendations}
            className={`w-full p-2.5 rounded-lg flex items-center gap-2 font-medium text-sm transition-all ${
              showRecommendations
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Navigation size={18} />
            <span>Top Locations</span>
          </button>
        </>
      )}

      <button
        onClick={toggleChat}
        className={`w-full p-2.5 rounded-lg flex items-center gap-2 font-medium text-sm transition-all ${
          showChat
            ? 'bg-blue-600 text-white'
            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
        }`}
      >
        <MessageCircle size={18} />
        <span>AI Chat</span>
      </button>

      {locations.length > 0 && (
        <button
          onClick={clearLocations}
          className="w-full p-2.5 rounded-lg flex items-center gap-2 font-medium text-sm bg-slate-700 text-slate-300 hover:bg-red-600/20 transition-all"
        >
          <Trash2 size={18} />
          <span>Clear All</span>
        </button>
      )}
    </div>
  )
}
