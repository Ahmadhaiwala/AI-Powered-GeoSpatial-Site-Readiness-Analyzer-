import { MapContainer } from './components/MapContainer'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { useMapStore } from './store'
import { ExplanationPanel } from './components/ExplanationPanel'
import { RecommendationsList } from './components/RecommendationsList'
import { ChatPanel } from './components/ChatPanel'

export default function App() {
  const selectedLocation = useMapStore((state) => state.selectedLocation)
  const showExplanation = useMapStore((state) => state.showExplanation)
  const showRecommendations = useMapStore((state) => state.showRecommendations)
  const showChat = useMapStore((state) => state.showChat)

  return (
    <div className="w-full h-screen flex flex-col bg-slate-900">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 relative">
          <MapContainer />
          {selectedLocation && (
            <>
              {showExplanation && <ExplanationPanel location={selectedLocation} />}
              {showRecommendations && <RecommendationsList location={selectedLocation} />}
            </>
          )}
          {showChat && <ChatPanel />}
        </div>
        <Sidebar />
      </div>
    </div>
  )
}
