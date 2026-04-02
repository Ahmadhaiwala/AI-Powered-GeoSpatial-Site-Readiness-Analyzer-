import { useCallback } from 'react'
import { useMapStore, type Location } from '../store'
import { api } from '../lib/api'

export function useLocationEval() {
  const setLoading = useMapStore((state) => state.setLoading)
  const scoreLocation = useMapStore((state) => state.scoreLocation)
  const setError = useMapStore((state) => state.setError)

  const evaluateLocation = useCallback(
    async (location: Location) => {
      try {
        setLoading(true)
        setError(null)

        const result = await api.evaluate(location.lat, location.lng, location.businessType)

        scoreLocation(location, {
          score: result.total_score,
          factors: {
            population: Math.round(result.breakdown.population * 100),
            transport: Math.round(result.breakdown.transport * 100),
            competition: Math.round(result.breakdown.competition * 100),
            zoning: Math.round(result.breakdown.zoning * 100),
            risk: Math.round(result.breakdown.risk * 100),
            demand: Math.round(result.breakdown.demand * 100),
          },
          explanation: result.explanation,
        })
      } catch (err) {
        setError('Failed to evaluate location. Is the backend running?')
        console.error('Evaluation error:', err)
      } finally {
        setLoading(false)
      }
    },
    [setLoading, scoreLocation, setError],
  )

  return { evaluateLocation }
}
