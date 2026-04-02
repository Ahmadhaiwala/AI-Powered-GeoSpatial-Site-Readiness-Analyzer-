"""
Demand controller — handles voting and demand hotspot requests.
"""
from fastapi import APIRouter
from typing import List

from backend.models.schemas import VoteRequest, VoteResponse
from backend.services.demand_service import add_vote, get_all_votes, get_demand_hotspots

router = APIRouter(prefix="/api", tags=["demand"])


@router.post("/vote", response_model=VoteResponse)
async def cast_vote(req: VoteRequest):
    """Cast a demand vote for a location."""
    result = add_vote(
        lat=req.lat,
        lng=req.lng,
        category=req.category,
        comment=req.comment,
    )
    return VoteResponse(**result)


@router.get("/votes")
async def get_votes():
    """Get all demand votes for heatmap display."""
    return get_all_votes()


@router.get("/hotspots")
async def get_hotspots():
    """Get aggregated demand hotspots."""
    return get_demand_hotspots()
