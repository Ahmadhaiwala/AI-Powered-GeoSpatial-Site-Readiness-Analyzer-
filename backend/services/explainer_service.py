"""
Explainable AI layer.
Converts raw score breakdowns into human-readable explanations
with strengths, weaknesses, and improvement suggestions.
"""
from typing import Dict, List, Tuple


# Thresholds for classifying sub-scores
HIGH_THRESHOLD = 0.7
LOW_THRESHOLD = 0.4

# Human-readable labels and explanations
FACTOR_LABELS = {
    "population": {
        "name": "Population Density",
        "high": "High population density — strong customer base nearby",
        "medium": "Moderate population density",
        "low": "Low population density — limited foot traffic",
        "improve": "Consider locations closer to residential/commercial hubs",
    },
    "transport": {
        "name": "Transportation & Accessibility",
        "high": "Excellent road connectivity and highway access",
        "medium": "Moderate transportation access",
        "low": "Poor road connectivity — hard to reach",
        "improve": "Move closer to major highways or well-connected roads",
    },
    "competition": {
        "name": "Competition Level",
        "high": "Healthy competition level — established market with room for more",
        "medium": "Moderate competition density",
        "low": "Too much or too little competition in the area",
        "improve": "Look for areas with 2-3 similar businesses (proven demand, not oversaturated)",
    },
    "zoning": {
        "name": "Zoning Compliance",
        "high": "Zone is fully compatible with this business type",
        "medium": "Zone may have some restrictions",
        "low": "Zoning is restrictive or incompatible — permits may be difficult",
        "improve": "Check for commercially zoned or mixed-use areas",
    },
    "risk": {
        "name": "Environmental Safety",
        "high": "No significant environmental risks detected",
        "medium": "Some environmental concerns in the area",
        "low": "High environmental risk (flood/pollution) — significant concern",
        "improve": "Avoid flood-prone and high-pollution zones",
    },
    "demand": {
        "name": "Community Demand",
        "high": "Strong community demand signal for this type of business",
        "medium": "Some community interest recorded",
        "low": "No significant community demand signals yet",
        "improve": "This factor improves as more community votes come in",
    },
}


def explain_score(breakdown: Dict, weights: Dict) -> Dict:
    """
    Generate a human-readable explanation of the score.

    Args:
        breakdown: dict with sub-scores (0-1) for each factor
        weights: dict with weight values for each factor

    Returns:
        dict with strengths, weaknesses, and suggestions
    """
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []

    # Classify each factor and build explanations
    scored_factors: List[Tuple[str, float, float]] = []
    for factor, score in breakdown.items():
        weight = weights.get(factor, 0)
        scored_factors.append((factor, score, weight))

    # Sort by weighted impact (descending)
    scored_factors.sort(key=lambda x: x[1] * x[2], reverse=True)

    for factor, score, weight in scored_factors:
        labels = FACTOR_LABELS.get(factor)
        if not labels:
            continue

        impact = "high" if weight >= 0.20 else "moderate" if weight >= 0.10 else "low"
        weight_note = f" (impact: {impact})"

        if score >= HIGH_THRESHOLD:
            strengths.append(f"✔ {labels['high']}{weight_note}")
        elif score >= LOW_THRESHOLD:
            # Medium — only note if it has significant weight
            if weight >= 0.15:
                weaknesses.append(f"⚠ {labels['medium']}{weight_note}")
        else:
            weaknesses.append(f"✖ {labels['low']}{weight_note}")
            if weight >= 0.10:
                suggestions.append(f"💡 {labels['improve']}")

    # Add overall summary suggestion if score is improvable
    if not suggestions and weaknesses:
        suggestions.append("💡 Consider nearby locations to improve weaker factors")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
    }
