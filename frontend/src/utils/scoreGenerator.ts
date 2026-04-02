import { SiteScore } from '../store'

export function generateScore(businessType: string): SiteScore {
  // Base factor values influenced by business type
  const baseFactors = {
    retail: {
      accessibility: 85,
      infrastructure: 78,
      demographics: 82,
      competition: 65,
      regulations: 72,
      logistics: 70,
    },
    food: {
      accessibility: 88,
      infrastructure: 75,
      demographics: 80,
      competition: 70,
      regulations: 68,
      logistics: 72,
    },
    cafe: {
      accessibility: 90,
      infrastructure: 80,
      demographics: 85,
      competition: 60,
      regulations: 75,
      logistics: 65,
    },
    office: {
      accessibility: 78,
      infrastructure: 85,
      demographics: 75,
      competition: 72,
      regulations: 80,
      logistics: 68,
    },
    industrial: {
      accessibility: 65,
      infrastructure: 82,
      demographics: 60,
      competition: 75,
      regulations: 70,
      logistics: 85,
    },
  }

  const baseType = businessType as keyof typeof baseFactors
  const factors = baseFactors[baseType] || baseFactors.retail

  // Add some randomness to simulate actual evaluation variance
  const randomizedFactors = Object.entries(factors).reduce((acc, [key, value]) => {
    const variance = (Math.random() - 0.5) * 20 // ±10 variance
    const finalValue = Math.max(0, Math.min(100, value + variance))
    acc[key as keyof typeof factors] = Math.round(finalValue)
    return acc
  }, {} as Record<string, number>)

  // Calculate overall score as weighted average
  const weights = {
    accessibility: 0.20,
    infrastructure: 0.18,
    demographics: 0.18,
    competition: 0.16,
    regulations: 0.15,
    logistics: 0.13,
  }

  let totalScore = 0
  Object.entries(randomizedFactors).forEach(([key, value]) => {
    totalScore += value * (weights[key as keyof typeof weights] || 0)
  })

  const score = Math.round(totalScore)

  return {
    score: Math.min(100, Math.max(0, score)),
    factors: randomizedFactors as any,
  }
}
