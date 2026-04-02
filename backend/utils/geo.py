"""
Geospatial utility functions.
"""
import math
from typing import List, Dict


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def points_within_radius(
    lat: float,
    lng: float,
    points: List[Dict],
    radius_km: float,
) -> List[Dict]:
    """Filter points within a given radius from (lat, lng)."""
    return [
        p
        for p in points
        if haversine_km(lat, lng, p["lat"], p["lng"]) <= radius_km
    ]


def min_distance_to_points(
    lat: float,
    lng: float,
    points: List[Dict],
) -> float:
    """Return the minimum distance in km from (lat,lng) to a list of points.
    Returns float('inf') if the list is empty.
    """
    if not points:
        return float("inf")
    return min(haversine_km(lat, lng, p["lat"], p["lng"]) for p in points)


def normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to [0, 1] range."""
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def sigmoid_saturation(value: float, midpoint: float, steepness: float = 1.0) -> float:
    """Sigmoid-like saturation curve, returns 0–1."""
    x = steepness * (value - midpoint) / midpoint if midpoint else 0
    return 1.0 / (1.0 + math.exp(-x))


def exponential_decay(distance_km: float, decay_rate: float = 2.0) -> float:
    """Exponential decay: closer = higher score. Returns 0–1."""
    return math.exp(-decay_rate * distance_km)


def gaussian_score(count: int, optimal: int, sigma: float = 3.0) -> float:
    """Gaussian curve around an optimal count. Returns 0–1.
    Some competition is good, too much or none is bad.
    """
    return math.exp(-((count - optimal) ** 2) / (2 * sigma ** 2))


def point_in_polygon(lat: float, lng: float, polygon: List[Dict]) -> bool:
    """Ray-casting algorithm to check if point is inside polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]["lat"], polygon[i]["lng"]
        yj, xj = polygon[j]["lat"], polygon[j]["lng"]
        if ((yi > lat) != (yj > lat)) and (
            lng < (xj - xi) * (lat - yi) / (yj - yi) + xi
        ):
            inside = not inside
        j = i
    return inside
