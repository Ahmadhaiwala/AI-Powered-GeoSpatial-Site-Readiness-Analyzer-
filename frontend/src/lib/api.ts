/**
 * API client — connects to the FastAPI backend.
 * Base URL defaults to localhost:8000, override via VITE_API_URL env var.
 */

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

// ── Types mirroring backend schemas ────────────────────────────────────────

export interface ScoreBreakdown {
  population: number
  transport: number
  competition: number
  zoning: number
  risk: number
  demand: number
}

export interface Explanation {
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
}

export interface EvaluateResponse {
  lat: number
  lng: number
  business_type: string
  total_score: number
  breakdown: ScoreBreakdown
  weights_used: ScoreBreakdown
  explanation: Explanation
}

export interface RecommendedLocation {
  h3_index: string
  lat: number
  lng: number
  score: number
  rank: number
}

export interface RecommendResponse {
  business_type: string
  locations: RecommendedLocation[]
}

export interface VoteResponse {
  success: boolean
  total_votes_in_area: number
  message: string
}

export interface Vote {
  lat: number
  lng: number
  category: string
  comment?: string
  timestamp: string
}

export interface Hotspot {
  lat: number
  lng: number
  category: string
  count: number
}

export interface ChatResponse {
  reply: string
  detected_business_type: string | null
  detected_location: string | null
  results: RecommendedLocation[] | null
}

export interface BusinessType {
  key: string
  label: string
  weights: ScoreBreakdown
}

// ── API calls ────────────────────────────────────────────────────────────────

export const api = {
  /** Evaluate a single location for a business type. */
  evaluate(lat: number, lng: number, businessType: string, radiusKm = 2.0): Promise<EvaluateResponse> {
    return request<EvaluateResponse>('/api/evaluate', {
      method: 'POST',
      body: JSON.stringify({ lat, lng, business_type: businessType, radius_km: radiusKm }),
    })
  },

  /** Get top recommended locations in a bounding box. */
  recommend(
    businessType: string,
    minLat: number,
    maxLat: number,
    minLng: number,
    maxLng: number,
    topN = 10,
  ): Promise<RecommendResponse> {
    return request<RecommendResponse>('/api/recommend', {
      method: 'POST',
      body: JSON.stringify({
        business_type: businessType,
        min_lat: minLat,
        max_lat: maxLat,
        min_lng: minLng,
        max_lng: maxLng,
        top_n: topN,
      }),
    })
  },

  /** Cast a demand vote. */
  vote(lat: number, lng: number, category: string, comment?: string): Promise<VoteResponse> {
    return request<VoteResponse>('/api/vote', {
      method: 'POST',
      body: JSON.stringify({ lat, lng, category, comment }),
    })
  },

  /** Get all demand votes. */
  getVotes(): Promise<Vote[]> {
    return request<Vote[]>('/api/votes')
  },

  /** Get aggregated demand hotspots. */
  getHotspots(): Promise<Hotspot[]> {
    return request<Hotspot[]>('/api/hotspots')
  },

  /** Send a natural language chat message. */
  chat(message: string): Promise<ChatResponse> {
    return request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    })
  },

  /** Get all supported business types. */
  getBusinessTypes(): Promise<BusinessType[]> {
    return request<BusinessType[]>('/api/business-types')
  },
}
