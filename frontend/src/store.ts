import { create } from 'zustand'
import type { RecommendedLocation, Hotspot } from './lib/api'

// ── Score shape mirrors the backend ────────────────────────────────────────
export interface SiteScore {
  score: number          // total_score 0-100
  factors: {
    population: number
    transport: number
    competition: number
    zoning: number
    risk: number
    demand: number
  }
  explanation?: {
    strengths: string[]
    weaknesses: string[]
    suggestions: string[]
  }
}

export interface Location {
  lat: number
  lng: number
  name: string
  businessType: string
  score: SiteScore | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  results?: RecommendedLocation[] | null
}

export interface MapState {
  // Map
  locations: Location[]
  selectedLocation: Location | null
  mapCenter: [number, number]
  mapZoom: number

  // Business type
  businessType: string

  // UI panels
  showExplanation: boolean
  showRecommendations: boolean
  showChat: boolean

  // Recommendations from /api/recommend
  recommendations: RecommendedLocation[]

  // Demand hotspots from /api/hotspots
  hotspots: Hotspot[]

  // Chat messages
  chatMessages: ChatMessage[]

  // Async state
  isLoading: boolean
  isRecommending: boolean
  isChatLoading: boolean
  error: string | null

  // Actions
  addLocation: (location: Location) => void
  selectLocation: (location: Location | null) => void
  updateMapView: (center: [number, number], zoom: number) => void
  setBusinessType: (type: string) => void
  toggleExplanation: () => void
  toggleRecommendations: () => void
  toggleChat: () => void
  scoreLocation: (location: Location, score: SiteScore) => void
  setLoading: (loading: boolean) => void
  setRecommending: (loading: boolean) => void
  setChatLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearLocations: () => void
  setRecommendations: (recs: RecommendedLocation[]) => void
  setHotspots: (hotspots: Hotspot[]) => void
  addChatMessage: (message: ChatMessage) => void
  clearChat: () => void
}

// Ahmedabad city center
const AHMEDABAD_CENTER: [number, number] = [23.0225, 72.5714]

export const useMapStore = create<MapState>((set) => ({
  locations: [],
  selectedLocation: null,
  mapCenter: AHMEDABAD_CENTER,
  mapZoom: 12,
  businessType: 'retail_store',
  showExplanation: false,
  showRecommendations: false,
  showChat: false,
  recommendations: [],
  hotspots: [],
  chatMessages: [],
  isLoading: false,
  isRecommending: false,
  isChatLoading: false,
  error: null,

  addLocation: (location) =>
    // Don't auto-select — keeps panels stable for the previously selected location
    set((state) => ({
      locations: [...state.locations, location],
    })),

  selectLocation: (location) => set({ selectedLocation: location }),

  updateMapView: (center, zoom) => set({ mapCenter: center, mapZoom: zoom }),

  setBusinessType: (type) => set({ businessType: type }),

  toggleExplanation: () =>
    set((state) => ({ showExplanation: !state.showExplanation })),

  toggleRecommendations: () =>
    set((state) => ({ showRecommendations: !state.showRecommendations })),

  toggleChat: () => set((state) => ({ showChat: !state.showChat })),

  scoreLocation: (location, score) =>
    set((state) => ({
      locations: state.locations.map((loc) =>
        loc.lat === location.lat && loc.lng === location.lng
          ? { ...loc, score }
          : loc,
      ),
      selectedLocation:
        state.selectedLocation?.lat === location.lat &&
        state.selectedLocation?.lng === location.lng
          ? { ...location, score }
          : state.selectedLocation,
    })),

  setLoading: (loading) => set({ isLoading: loading }),
  setRecommending: (loading) => set({ isRecommending: loading }),
  setChatLoading: (loading) => set({ isChatLoading: loading }),
  setError: (error) => set({ error }),

  clearLocations: () => set({ locations: [], selectedLocation: null }),

  setRecommendations: (recs) => set({ recommendations: recs }),
  setHotspots: (hotspots) => set({ hotspots }),

  addChatMessage: (message) =>
    set((state) => ({ chatMessages: [...state.chatMessages, message] })),

  clearChat: () => set({ chatMessages: [] }),
}))
