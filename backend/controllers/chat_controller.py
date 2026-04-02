"""
Chat controller — handles chatbot requests.
"""
from fastapi import APIRouter

from backend.models.schemas import ChatRequest, ChatResponse, RecommendedLocation
from backend.services.chatbot_service import parse_chat_message
from backend.services.scoring_service import compute_score
from backend.services.recommendation_service import recommend_locations

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Process a natural language query."""
    parsed = parse_chat_message(req.message)

    results = None
    if parsed["needs_action"] and parsed["business_type"] and parsed["location"]:
        loc = parsed["location"]

        if parsed["intent"] == "evaluate":
            # Evaluate the specific location
            score_result = compute_score(
                lat=loc["lat"],
                lng=loc["lng"],
                business_type=parsed["business_type"],
            )
            parsed["reply"] += (
                f"\n\n**Score: {score_result['total_score']}/100**"
                f"\n- Population: {score_result['breakdown']['population']:.2f}"
                f"\n- Transport: {score_result['breakdown']['transport']:.2f}"
                f"\n- Competition: {score_result['breakdown']['competition']:.2f}"
                f"\n- Zoning: {score_result['breakdown']['zoning']:.2f}"
                f"\n- Risk: {score_result['breakdown']['risk']:.2f}"
                f"\n- Demand: {score_result['breakdown']['demand']:.2f}"
            )
        else:
            # Recommend top locations
            delta = 0.03  # ~3km bounding box around location
            recs = recommend_locations(
                business_type=parsed["business_type"],
                min_lat=loc["lat"] - delta,
                max_lat=loc["lat"] + delta,
                min_lng=loc["lng"] - delta,
                max_lng=loc["lng"] + delta,
                top_n=5,
            )
            results = [RecommendedLocation(**r) for r in recs]

            if recs:
                parsed["reply"] += "\n\n**Top Locations:**"
                for r in recs:
                    parsed["reply"] += f"\n{r['rank']}. Score: {r['score']} — ({r['lat']}, {r['lng']})"

    return ChatResponse(
        reply=parsed["reply"],
        detected_business_type=parsed["business_type"],
        detected_location=parsed["location"].get("label") if parsed["location"] else None,
        results=results,
    )
