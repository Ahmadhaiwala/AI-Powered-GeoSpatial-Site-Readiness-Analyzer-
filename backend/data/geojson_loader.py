"""
GeoJSON data loader.
Parses the real GeoJSON files into structured data for the scoring engine.
"""
import json
import os
from typing import List, Dict, Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def _load_geojson(filename: str) -> Dict:
    """Load a GeoJSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_point_coords(feature: Dict) -> Optional[Dict]:
    """Extract lat/lng from a GeoJSON Point feature."""
    geom = feature.get("geometry", {})
    if geom.get("type") == "Point":
        coords = geom.get("coordinates", [])
        if len(coords) >= 2:
            return {"lng": coords[0], "lat": coords[1]}
    return None


def _extract_line_midpoint(feature: Dict) -> Optional[Dict]:
    """Extract the midpoint of a LineString geometry."""
    geom = feature.get("geometry", {})
    if geom.get("type") == "LineString":
        coords = geom.get("coordinates", [])
        if coords:
            mid = len(coords) // 2
            return {"lng": coords[mid][0], "lat": coords[mid][1]}
    return None


def _extract_polygon_centroid(feature: Dict) -> Optional[Dict]:
    """Extract approximate centroid of a Polygon geometry."""
    geom = feature.get("geometry", {})
    if geom.get("type") == "Polygon":
        coords = geom.get("coordinates", [[]])[0]
        if coords:
            avg_lng = sum(c[0] for c in coords) / len(coords)
            avg_lat = sum(c[1] for c in coords) / len(coords)
            return {"lng": avg_lng, "lat": avg_lat}
    return None


def _extract_polygon_vertices(feature: Dict) -> Optional[List[Dict]]:
    """Extract polygon vertices as list of {lat, lng}."""
    geom = feature.get("geometry", {})
    if geom.get("type") == "Polygon":
        coords = geom.get("coordinates", [[]])[0]
        return [{"lat": c[1], "lng": c[0]} for c in coords]
    return None


# ──────────────────────────────────────────────
# Data loaders for each GeoJSON file
# ──────────────────────────────────────────────

def load_dense_activity_places() -> List[Dict]:
    """
    Load dense_activity_places.geojson.
    Contains: schools, hospitals, railway stations, bus stations, marketplaces.
    Used as population/activity proxy.
    """
    data = _load_geojson("dense_activity_places.geojson")
    places = []

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = _extract_point_coords(feature)
        if not coords:
            # Try polygon centroid (some features might be polygons)
            coords = _extract_polygon_centroid(feature)
        if not coords:
            continue

        # Determine the amenity type
        amenity = props.get("amenity", "")
        name = props.get("name", "Unknown")
        is_railway = props.get("railway") == "station"
        is_bus = props.get("public_transport") == "station" or props.get("bus") == "yes"

        # Classify the place type
        if amenity == "hospital" or props.get("healthcare"):
            place_type = "hospital"
        elif amenity == "school":
            place_type = "school"
        elif amenity == "marketplace":
            place_type = "marketplace"
        elif amenity == "bus_station" or is_bus:
            place_type = "bus_station"
        elif is_railway:
            place_type = "railway_station"
        else:
            place_type = amenity or "other"

        # Assign population weight (proxy for foot traffic)
        pop_weights = {
            "railway_station": 8000,
            "bus_station": 5000,
            "hospital": 3000,
            "marketplace": 4000,
            "school": 2000,
            "other": 1000,
        }

        places.append({
            "lat": coords["lat"],
            "lng": coords["lng"],
            "name": name,
            "type": place_type,
            "amenity": amenity,
            "population": pop_weights.get(place_type, 1000),
        })

    return places


def load_highways() -> List[Dict]:
    """
    Load highway.geojson.
    Contains: primary, secondary, tertiary roads, bridges, platforms.
    Returns sampled road points for distance-based scoring.
    """
    data = _load_geojson("highway.geojson")
    roads = []
    seen_coords = set()

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        highway_type = props.get("highway", "")
        name = props.get("name", "")
        geom = feature.get("geometry", {})
        geom_type = geom.get("type", "")

        # Classify road type
        if highway_type in ("motorway", "trunk", "primary"):
            road_type = "highway"
        elif highway_type in ("secondary", "tertiary"):
            road_type = "main_road"
        elif highway_type in ("residential", "living_street", "unclassified"):
            road_type = "secondary_road"
        elif highway_type in ("platform", "pedestrian"):
            road_type = "transit_point"
        else:
            road_type = "other"

        # Extract points from the geometry
        if geom_type == "LineString":
            coords_list = geom.get("coordinates", [])
            # Sample: take start, middle, end points to avoid huge data
            sample_indices = [0, len(coords_list) // 2, len(coords_list) - 1]
            for idx in sample_indices:
                if 0 <= idx < len(coords_list):
                    c = coords_list[idx]
                    key = (round(c[0], 4), round(c[1], 4))
                    if key not in seen_coords:
                        seen_coords.add(key)
                        roads.append({
                            "lat": c[1],
                            "lng": c[0],
                            "type": road_type,
                            "name": name,
                        })
        elif geom_type == "Polygon":
            # For platforms, bus stops — take centroid
            coords = _extract_polygon_centroid(feature)
            if coords:
                key = (round(coords["lng"], 4), round(coords["lat"], 4))
                if key not in seen_coords:
                    seen_coords.add(key)
                    roads.append({
                        "lat": coords["lat"],
                        "lng": coords["lng"],
                        "type": road_type,
                        "name": name,
                    })

    return roads


def load_competitors() -> List[Dict]:
    """
    Load retail_shop_data.geojson + petrol_fuel.geojson as competitor POIs.
    Maps shop types to business categories for competition scoring.
    """
    competitors = []

    # ── Retail shops ──
    retail_data = _load_geojson("retail_shop_data.geojson")
    shop_category_map = {
        "hairdresser": "salon",
        "beauty": "salon",
        "barber": "salon",
        "supermarket": "retail_store",
        "convenience": "retail_store",
        "mall": "retail_store",
        "grocery": "retail_store",
        "clothes": "retail_store",
        "department_store": "retail_store",
        "bakery": "restaurant",
        "deli": "restaurant",
        "coffee": "restaurant",
        "tea": "restaurant",
        "beverages": "restaurant",
        "ice_cream": "restaurant",
        "books": "retail_store",
        "kiosk": "retail_store",
        "dairy": "retail_store",
        "greengrocer": "retail_store",
        "lifestyle": "retail_store",
    }

    for feature in retail_data.get("features", []):
        coords = _extract_point_coords(feature)
        if not coords:
            continue

        props = feature.get("properties", {})
        shop_type = props.get("shop", "").lower().split("-")[0].strip()
        name = props.get("name", "Unknown Shop")
        category = shop_category_map.get(shop_type, "retail_store")

        competitors.append({
            "lat": coords["lat"],
            "lng": coords["lng"],
            "name": name,
            "category": category,
            "shop_type": shop_type,
        })

    # ── Fuel stations → mapped to ev_charging category ──
    fuel_data = _load_geojson("petrol_fuel.geojson")
    for feature in fuel_data.get("features", []):
        coords = _extract_point_coords(feature)
        if not coords:
            continue

        props = feature.get("properties", {})
        name = props.get("name", props.get("brand", "Fuel Station"))

        # Fuel stations serve as proxy competitors for EV charging
        competitors.append({
            "lat": coords["lat"],
            "lng": coords["lng"],
            "name": name,
            "category": "ev_charging",
            "shop_type": "fuel",
        })

    return competitors


def load_zoning() -> List[Dict]:
    """
    Load warehouse_building_landuse.geojson for zoning data.
    Also create synthetic zoning from dense activity places.
    """
    zones = []

    # ── Real warehouse zones ──
    wh_data = _load_geojson("warehouse_building_landuse.geojson")
    for i, feature in enumerate(wh_data.get("features", [])):
        polygon = _extract_polygon_vertices(feature)
        centroid = _extract_polygon_centroid(feature)
        if polygon and centroid:
            zones.append({
                "id": i,
                "type": "industrial",
                "polygon": polygon,
                "center": centroid,
            })

    # ── Create zoning from activity clusters ──
    # Areas with many hospitals/schools → residential/mixed
    # Areas with many shops → commercial
    # Areas with railway/bus stations → commercial/mixed
    places = load_dense_activity_places()
    zone_id = len(zones)

    # Group places by rough grid cells
    from collections import defaultdict
    grid = defaultdict(list)
    cell_size = 0.01  # ~1km grid cells

    for p in places:
        cell_key = (round(p["lat"] / cell_size) * cell_size,
                    round(p["lng"] / cell_size) * cell_size)
        grid[cell_key].append(p)

    for (cell_lat, cell_lng), cell_places in grid.items():
        # Determine zone type based on dominant place types
        type_counts = {}
        for p in cell_places:
            t = p["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        if type_counts.get("hospital", 0) >= 2 or type_counts.get("school", 0) >= 3:
            zone_type = "residential"
        elif type_counts.get("marketplace", 0) >= 1 or type_counts.get("railway_station", 0) >= 1:
            zone_type = "commercial"
        elif type_counts.get("bus_station", 0) >= 1:
            zone_type = "mixed"
        else:
            zone_type = "mixed"

        half = cell_size / 2
        polygon = [
            {"lat": cell_lat - half, "lng": cell_lng - half},
            {"lat": cell_lat - half, "lng": cell_lng + half},
            {"lat": cell_lat + half, "lng": cell_lng + half},
            {"lat": cell_lat + half, "lng": cell_lng - half},
        ]

        zones.append({
            "id": zone_id,
            "type": zone_type,
            "polygon": polygon,
            "center": {"lat": cell_lat, "lng": cell_lng},
        })
        zone_id += 1

    return zones


def load_all_real_data() -> Dict:
    """Load all real GeoJSON data."""
    print("📍 Loading GeoJSON data from Ahmedabad, Gujarat...")

    places = load_dense_activity_places()
    print(f"  ✅ Dense activity places: {len(places)}")

    roads = load_highways()
    print(f"  ✅ Road network points: {len(roads)}")

    competitors = load_competitors()
    print(f"  ✅ Competitor POIs: {len(competitors)}")

    zoning = load_zoning()
    print(f"  ✅ Zoning areas: {len(zoning)}")

    # Generate simple risk zones around industrial/warehouse areas
    risk_zones = []
    for z in zoning:
        if z["type"] == "industrial":
            risk_zones.append({
                "type": "pollution",
                "lat": z["center"]["lat"],
                "lng": z["center"]["lng"],
                "radius_km": 0.5,
                "severity": 0.4,
            })
    print(f"  ✅ Risk zones: {len(risk_zones)}")

    return {
        "population_centers": places,
        "roads": roads,
        "competitors": competitors,
        "zoning": zoning,
        "risk_zones": risk_zones,
    }
