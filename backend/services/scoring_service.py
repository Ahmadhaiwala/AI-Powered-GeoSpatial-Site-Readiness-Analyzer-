"""
Core scoring engine.
Computes a 0-100 site readiness score using six weighted factors.
"""
import math
from typing import Dict, Tuple

from backend.config import BUSINESS_WEIGHTS, DEFAULT_RADIUS_KM, DEMAND_BOOST_FACTOR
from backend.models.database import db
from backend.utils.geo import (
    haversine_km,
    points_within_radius,
    min_distance_to_points,
    sigmoid_saturation,
    exponential_decay,
    gaussian_score,
    point_in_polygon,
)


def _get_weights(business_type: str) -> Dict[str, float]:
    """Get scoring weights for a business type."""
    return BUSINESS_WEIGHTS.get(business_type, BUSINESS_WEIGHTS["default"])


# ──────────────────────────────────────────────
# Sub-score functions (each returns 0.0 – 1.0)
# ──────────────────────────────────────────────

def _population_score(lat: float, lng: float, radius_km: float) -> Tuple[float, dict]:
    """Score based on population density within radius."""
    nearby = points_within_radius(lat, lng, db.population_centers, radius_km)
    total_pop = sum(p.get("population", 0) for p in nearby)

    # Sigmoid saturation: midpoint at 10k people
    score = sigmoid_saturation(total_pop, midpoint=10000, steepness=3.0)

    details = {
        "nearby_centers": len(nearby),
        "total_population": total_pop,
        "raw_score": round(score, 3),
    }
    return score, details


def _transport_score(lat: float, lng: float) -> Tuple[float, dict]:
    """Score based on road/highway proximity and road density."""
    highways = [r for r in db.roads if r.get("type") == "highway"]
    all_roads = db.roads

    # Distance to nearest highway
    dist_highway = min_distance_to_points(lat, lng, highways)
    highway_score = exponential_decay(dist_highway, decay_rate=3.0)

    # Road density: count roads within 1km
    nearby_roads = points_within_radius(lat, lng, all_roads, 1.0)
    density_score = sigmoid_saturation(len(nearby_roads), midpoint=5, steepness=2.0)

    # Combine 60% highway proximity + 40% road density
    score = 0.6 * highway_score + 0.4 * density_score

    details = {
        "dist_to_highway_km": round(dist_highway, 2),
        "nearby_roads_1km": len(nearby_roads),
        "raw_score": round(score, 3),
    }
    return score, details


def _competition_score(lat: float, lng: float, business_type: str, radius_km: float) -> Tuple[float, dict]:
    """Score based on competitor density — Gaussian (some is good, too many is bad)."""
    # Map business type to competitor categories
    category_map = {
        "salon": "salon",
        "restaurant": "restaurant",
        "gym": "gym",
        "retail_store": "retail_store",
        "ev_charging": "ev_charging",
        "hospital": "hospital",
        "warehouse": "warehouse",
        "default": None,  # count all
    }
    category = category_map.get(business_type)

    if category:
        relevant = [c for c in db.competitors if c["category"] == category]
    else:
        relevant = db.competitors

    nearby = points_within_radius(lat, lng, relevant, radius_km)
    count = len(nearby)

    # Gaussian: optimal is 2-3 competitors nearby
    score = gaussian_score(count, optimal=2, sigma=3.0)

    details = {
        "competitor_count": count,
        "category_searched": category or "all",
        "raw_score": round(score, 3),
    }
    return score, details


def _zoning_score(lat: float, lng: float, business_type: str) -> Tuple[float, dict]:
    """Score based on zoning compatibility."""
    # Which zone types are allowed for each business
    allowed_zones = {
        "retail_store": ["commercial", "mixed"],
        "ev_charging": ["commercial", "mixed", "industrial"],
        "warehouse": ["industrial", "mixed"],
        "salon": ["commercial", "mixed", "residential"],
        "restaurant": ["commercial", "mixed"],
        "hospital": ["commercial", "mixed", "residential"],
        "gym": ["commercial", "mixed", "residential"],
        "default": ["commercial", "mixed"],
    }

    allowed = allowed_zones.get(business_type, allowed_zones["default"])

    # Check which zone the point falls in
    matched_zone = None
    for zone in db.zoning:
        if point_in_polygon(lat, lng, zone["polygon"]):
            matched_zone = zone
            break

    if matched_zone is None:
        # No zoning data — neutral score
        score = 0.7
        zone_type = "unzoned"
    elif matched_zone["type"] in allowed:
        score = 1.0
        zone_type = matched_zone["type"]
    elif matched_zone["type"] == "restricted":
        score = 0.0
        zone_type = "restricted"
    else:
        score = 0.3
        zone_type = matched_zone["type"]

    details = {
        "zone_type": zone_type,
        "allowed_types": allowed,
        "raw_score": round(score, 3),
    }
    return score, details


def _risk_score(lat: float, lng: float) -> Tuple[float, dict]:
    """Score based on environmental risks (flood, pollution). Lower risk = higher score."""
    max_penalty = 0.0
    risk_details = []

    for rz in db.risk_zones:
        dist = haversine_km(lat, lng, rz["lat"], rz["lng"])
        if dist <= rz["radius_km"]:
            # Within risk zone
            # Penalty proportional to severity and proximity
            proximity = 1.0 - (dist / rz["radius_km"])
            penalty = rz["severity"] * proximity
            max_penalty = max(max_penalty, penalty)
            risk_details.append({
                "type": rz["type"],
                "severity": round(rz["severity"], 2),
                "distance_km": round(dist, 2),
                "penalty": round(penalty, 2),
            })

    score = max(0.0, 1.0 - max_penalty)

    details = {
        "risks_found": len(risk_details),
        "max_penalty": round(max_penalty, 2),
        "risk_details": risk_details,
        "raw_score": round(score, 3),
    }
    return score, details


def _demand_score(lat: float, lng: float, business_type: str, radius_km: float) -> Tuple[float, dict]:
    """Score based on crowdsourced demand votes."""
    relevant_votes = [
        v for v in db.votes
        if v.get("category", "").lower() == business_type.lower()
    ]
    nearby_votes = points_within_radius(lat, lng, relevant_votes, radius_km)
    count = len(nearby_votes)

    # More votes = higher demand signal, with saturation
    score = sigmoid_saturation(count, midpoint=5, steepness=2.0)

    details = {
        "nearby_votes": count,
        "raw_score": round(score, 3),
    }
    return score, details


# ──────────────────────────────────────────────
# Main scoring function
# ──────────────────────────────────────────────

def compute_score(
    lat: float,
    lng: float,
    business_type: str = "default",
    radius_km: float = DEFAULT_RADIUS_KM,
) -> Dict:
    """
    Compute the full site readiness score.

    Returns:
        dict with total_score (0-100), breakdown, weights, and details.
    """
    weights = _get_weights(business_type)

    # Compute each sub-score
    pop_score, pop_details = _population_score(lat, lng, radius_km)
    trans_score, trans_details = _transport_score(lat, lng)
    comp_score, comp_details = _competition_score(lat, lng, business_type, radius_km)
    zone_score, zone_details = _zoning_score(lat, lng, business_type)
    risk_sc, risk_details = _risk_score(lat, lng)
    dem_score, dem_details = _demand_score(lat, lng, business_type, radius_km)

    # Weighted sum
    raw = (
        weights["population"] * pop_score
        + weights["transport"] * trans_score
        + weights["competition"] * comp_score
        + weights["zoning"] * zone_score
        + weights["risk"] * risk_sc
        + weights["demand"] * dem_score
    )

    total_score = round(raw * 100, 1)
    total_score = max(0, min(100, total_score))

    return {
        "total_score": total_score,
        "breakdown": {
            "population": round(pop_score, 3),
            "transport": round(trans_score, 3),
            "competition": round(comp_score, 3),
            "zoning": round(zone_score, 3),
            "risk": round(risk_sc, 3),
            "demand": round(dem_score, 3),
        },
        "weights": weights,
        "details": {
            "population": pop_details,
            "transport": trans_details,
            "competition": comp_details,
            "zoning": zone_details,
            "risk": risk_details,
            "demand": dem_details,
        },
    }
