"""
Synthetic geospatial data generator for Bangalore area.
Generates realistic-looking data for testing without real datasets.
"""
import random
import math
from typing import List, Dict

# Bangalore city center
CENTER_LAT = 12.9716
CENTER_LNG = 77.5946

random.seed(42)  # Reproducible data


def _random_point_in_radius(center_lat: float, center_lng: float, radius_km: float) -> Dict:
    """Generate a random point within radius_km of the center."""
    # Convert radius to degrees (approx)
    r = radius_km / 111.0  # ~111 km per degree
    angle = random.uniform(0, 2 * math.pi)
    dist = r * math.sqrt(random.random())
    lat = center_lat + dist * math.cos(angle)
    lng = center_lng + dist * math.sin(angle) / math.cos(math.radians(center_lat))
    return {"lat": round(lat, 6), "lng": round(lng, 6)}


def generate_population_centers(n: int = 80, radius_km: float = 15.0) -> List[Dict]:
    """Generate population density centers with population counts."""
    centers = []
    for _ in range(n):
        pt = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        # Higher population near city center
        dist_from_center = math.sqrt(
            (pt["lat"] - CENTER_LAT) ** 2 + (pt["lng"] - CENTER_LNG) ** 2
        )
        base_pop = max(500, int(20000 * math.exp(-dist_from_center * 30)))
        pt["population"] = base_pop + random.randint(-200, 500)
        centers.append(pt)
    return centers


def generate_roads(n: int = 60, radius_km: float = 15.0) -> List[Dict]:
    """Generate road/highway points."""
    roads = []
    # Main highways — linear corridors
    for angle in [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]:
        for dist in [0.02, 0.04, 0.06, 0.08, 0.10, 0.12]:
            lat = CENTER_LAT + dist * math.cos(angle)
            lng = CENTER_LNG + dist * math.sin(angle) / math.cos(math.radians(CENTER_LAT))
            roads.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "type": "highway",
            })
    # Secondary roads
    for _ in range(n):
        pt = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        pt["type"] = random.choice(["main_road", "secondary_road"])
        roads.append(pt)
    return roads


def generate_competitors(n: int = 100, radius_km: float = 15.0) -> List[Dict]:
    """Generate competitor POI locations with categories."""
    categories = [
        "salon", "restaurant", "gym", "retail_store",
        "ev_charging", "hospital", "warehouse", "cafe",
        "pharmacy", "grocery",
    ]
    competitors = []
    for _ in range(n):
        pt = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        pt["category"] = random.choice(categories)
        pt["name"] = f"{pt['category'].replace('_', ' ').title()} #{random.randint(1, 999)}"
        competitors.append(pt)
    return competitors


def generate_zoning(radius_km: float = 15.0) -> List[Dict]:
    """Generate zoning polygons (commercial, residential, industrial, restricted)."""
    zones = []
    zone_types = ["commercial", "residential", "industrial", "restricted", "mixed"]

    for i in range(25):
        # Create small rectangular zones
        center = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        size = random.uniform(0.005, 0.015)
        polygon = [
            {"lat": center["lat"] - size, "lng": center["lng"] - size},
            {"lat": center["lat"] - size, "lng": center["lng"] + size},
            {"lat": center["lat"] + size, "lng": center["lng"] + size},
            {"lat": center["lat"] + size, "lng": center["lng"] - size},
        ]
        zones.append({
            "id": i,
            "type": zone_types[i % len(zone_types)],
            "polygon": polygon,
            "center": center,
        })
    return zones


def generate_risk_zones(radius_km: float = 15.0) -> List[Dict]:
    """Generate environmental risk zones (flood, pollution)."""
    risks = []

    # Flood-prone areas (typically near water bodies / low-lying)
    for _ in range(8):
        center = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        risks.append({
            "type": "flood",
            "lat": center["lat"],
            "lng": center["lng"],
            "radius_km": random.uniform(0.3, 1.0),
            "severity": random.uniform(0.3, 0.9),
        })

    # Pollution zones (near industrial areas)
    for _ in range(6):
        center = _random_point_in_radius(CENTER_LAT, CENTER_LNG, radius_km)
        risks.append({
            "type": "pollution",
            "lat": center["lat"],
            "lng": center["lng"],
            "radius_km": random.uniform(0.5, 1.5),
            "severity": random.uniform(0.2, 0.7),
        })

    return risks


def generate_all_data() -> Dict:
    """Generate all synthetic datasets."""
    return {
        "population_centers": generate_population_centers(),
        "roads": generate_roads(),
        "competitors": generate_competitors(),
        "zoning": generate_zoning(),
        "risk_zones": generate_risk_zones(),
    }
