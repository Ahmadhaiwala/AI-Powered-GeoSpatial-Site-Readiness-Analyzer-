"""
Recommendation engine using H3 hexagonal grid.
Divides area into grid cells, scores each, and returns top N.
"""
from typing import List, Dict
import h3

from backend.config import H3_RESOLUTION, TOP_N_RECOMMENDATIONS
from backend.services.scoring_service import compute_score


def recommend_locations(
    business_type: str,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    top_n: int = TOP_N_RECOMMENDATIONS,
) -> List[Dict]:
    """
    Divide the bounding box into H3 hex cells, score each, rank, and return top N.
    """
    # Get all H3 cells that cover the bounding box
    # Create a polygon from the bounding box
    bbox_polygon = [
        (min_lat, min_lng),
        (min_lat, max_lng),
        (max_lat, max_lng),
        (max_lat, min_lng),
        (min_lat, min_lng),  # close the polygon
    ]

    # Use h3.polyfill to get all hexes in the bounding box
    try:
        hex_set = h3.polyfill_geojson(
            {
                "type": "Polygon",
                "coordinates": [[
                    [lng, lat] for lat, lng in bbox_polygon
                ]],
            },
            H3_RESOLUTION,
        )
    except Exception:
        # Fallback: generate a grid of points
        hex_set = set()
        lat_step = 0.005  # ~500m
        lng_step = 0.005
        lat = min_lat
        while lat <= max_lat:
            lng = min_lng
            while lng <= max_lng:
                h = h3.latlng_to_cell(lat, lng, H3_RESOLUTION)
                hex_set.add(h)
                lng += lng_step
            lat += lat_step

    # Score each hex cell center
    scored_cells = []
    for hex_id in hex_set:
        lat, lng = h3.cell_to_latlng(hex_id)
        result = compute_score(lat, lng, business_type)
        scored_cells.append({
            "h3_index": hex_id,
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "score": result["total_score"],
        })

    # Sort by score descending
    scored_cells.sort(key=lambda x: x["score"], reverse=True)

    # Return top N with rank
    top = scored_cells[:top_n]
    for i, cell in enumerate(top):
        cell["rank"] = i + 1

    return top
