"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    lat: float = Field(..., description="Latitude of location to evaluate")
    lng: float = Field(..., description="Longitude of location to evaluate")
    business_type: str = Field(
        "default", description="Business category (e.g. salon, ev_charging, warehouse)"
    )
    radius_km: float = Field(2.0, description="Analysis radius in km")


class RecommendRequest(BaseModel):
    business_type: str = Field(
        "default", description="Business category"
    )
    # Bounding box for the area to analyze
    min_lat: float = Field(..., description="South boundary")
    max_lat: float = Field(..., description="North boundary")
    min_lng: float = Field(..., description="West boundary")
    max_lng: float = Field(..., description="East boundary")
    top_n: int = Field(10, description="Number of top locations to return")


class VoteRequest(BaseModel):
    lat: float
    lng: float
    category: str = Field(..., description="What the user wants (e.g. 'salon', 'gym')")
    comment: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language query")


# ──────────────────────────────────────────────
# Response Models
# ──────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    population: float = Field(..., description="Population sub-score 0-1")
    transport: float = Field(..., description="Transport sub-score 0-1")
    competition: float = Field(..., description="Competition sub-score 0-1")
    zoning: float = Field(..., description="Zoning sub-score 0-1")
    risk: float = Field(..., description="Risk sub-score 0-1")
    demand: float = Field(..., description="Demand sub-score 0-1")


class Explanation(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class EvaluateResponse(BaseModel):
    lat: float
    lng: float
    business_type: str
    total_score: float = Field(..., description="Final score 0-100")
    breakdown: ScoreBreakdown
    weights_used: Dict[str, float]
    explanation: Explanation


class RecommendedLocation(BaseModel):
    lat: float
    lng: float
    h3_index: str
    score: float
    rank: int


class RecommendResponse(BaseModel):
    business_type: str
    locations: List[RecommendedLocation]


class VoteResponse(BaseModel):
    success: bool
    total_votes_in_area: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    detected_business_type: Optional[str] = None
    detected_location: Optional[str] = None
    results: Optional[List[RecommendedLocation]] = None


class BusinessTypeInfo(BaseModel):
    key: str
    label: str
    weights: Dict[str, float]
