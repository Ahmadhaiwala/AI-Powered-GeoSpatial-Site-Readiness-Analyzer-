"""
Crowdsourced demand voting service.
"""
from typing import List, Dict
from datetime import datetime

from backend.models.database import db
from backend.utils.geo import points_within_radius


def add_vote(lat: float, lng: float, category: str, comment: str = None) -> Dict:
    """Register a demand vote."""
    vote = {
        "lat": lat,
        "lng": lng,
        "category": category.lower().strip(),
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat(),
    }
    db.add_vote(vote)

    # Count total votes for this category nearby
    relevant = [v for v in db.votes if v["category"] == vote["category"]]
    nearby = points_within_radius(lat, lng, relevant, radius_km=2.0)

    return {
        "success": True,
        "total_votes_in_area": len(nearby),
        "message": f"Vote recorded! {len(nearby)} people want a {category} in this area.",
    }


def get_all_votes() -> List[Dict]:
    """Get all votes for heatmap display."""
    return db.get_votes()


def get_demand_hotspots(radius_km: float = 2.0) -> List[Dict]:
    """
    Aggregate votes into hotspot clusters.
    Returns list of {lat, lng, category, count}.
    """
    votes = db.get_votes()
    if not votes:
        return []

    # Simple clustering: group votes by category, then cluster nearby ones
    from collections import defaultdict
    by_category = defaultdict(list)
    for v in votes:
        by_category[v["category"]].append(v)

    hotspots = []
    for category, cat_votes in by_category.items():
        # Use first vote as cluster seed, merge nearby
        processed = set()
        for i, v in enumerate(cat_votes):
            if i in processed:
                continue
            cluster = [v]
            processed.add(i)
            for j, other in enumerate(cat_votes):
                if j in processed:
                    continue
                from backend.utils.geo import haversine_km
                if haversine_km(v["lat"], v["lng"], other["lat"], other["lng"]) <= radius_km:
                    cluster.append(other)
                    processed.add(j)

            # Cluster center = average
            avg_lat = sum(c["lat"] for c in cluster) / len(cluster)
            avg_lng = sum(c["lng"] for c in cluster) / len(cluster)
            hotspots.append({
                "lat": round(avg_lat, 6),
                "lng": round(avg_lng, 6),
                "category": category,
                "count": len(cluster),
            })

    hotspots.sort(key=lambda x: x["count"], reverse=True)
    return hotspots
