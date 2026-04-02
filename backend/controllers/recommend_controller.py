"""
Recommend controller — handles area recommendation requests.
"""
from fastapi import APIRouter
from typing import List

from backend.models.schemas import RecommendRequest, RecommendResponse, RecommendedLocation
from backend.services.recommendation_service import recommend_locations

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(req: RecommendRequest):
    """Get top recommended locations within a bounding box."""
    locations = recommend_locations(
        business_type=req.business_type,
        min_lat=req.min_lat,
        max_lat=req.max_lat,
        min_lng=req.min_lng,
        max_lng=req.max_lng,
        top_n=req.top_n,
    )

    return RecommendResponse(
        business_type=req.business_type,
        locations=[RecommendedLocation(**loc) for loc in locations],
    )
