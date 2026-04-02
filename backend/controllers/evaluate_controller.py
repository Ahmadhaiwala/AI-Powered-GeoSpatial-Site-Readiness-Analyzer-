"""
Evaluate controller — handles location evaluation requests.
"""
from fastapi import APIRouter

from backend.models.schemas import EvaluateRequest, EvaluateResponse, ScoreBreakdown, Explanation
from backend.services.scoring_service import compute_score
from backend.services.explainer_service import explain_score

router = APIRouter(prefix="/api", tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_location(req: EvaluateRequest):
    """Evaluate a single location for a given business type."""
    result = compute_score(
        lat=req.lat,
        lng=req.lng,
        business_type=req.business_type,
        radius_km=req.radius_km,
    )

    explanation = explain_score(result["breakdown"], result["weights"])

    return EvaluateResponse(
        lat=req.lat,
        lng=req.lng,
        business_type=req.business_type,
        total_score=result["total_score"],
        breakdown=ScoreBreakdown(**result["breakdown"]),
        weights_used=result["weights"],
        explanation=Explanation(**explanation),
    )
