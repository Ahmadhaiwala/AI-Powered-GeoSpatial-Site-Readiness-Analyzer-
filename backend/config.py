"""
Application configuration and constants.
"""

# City center coordinates (Ahmedabad)
CENTER_LAT = 23.0225
CENTER_LNG = 72.5714

# Scoring radius in km
DEFAULT_RADIUS_KM = 2.0

# H3 resolution for recommendation grid (7 = ~5km², 8 = ~0.7km², 9 = ~0.1km²)
H3_RESOLUTION = 8

# Number of top recommendations to return
TOP_N_RECOMMENDATIONS = 10

# Demand vote boost factor
DEMAND_BOOST_FACTOR = 0.05

# ──────────────────────────────────────────────
# Business-type weight profiles
# Keys: population, transport, competition, zoning, risk, demand
# ──────────────────────────────────────────────
BUSINESS_WEIGHTS = {
    "retail_store": {
        "population": 0.30,
        "transport": 0.15,
        "competition": 0.20,
        "zoning": 0.15,
        "risk": 0.10,
        "demand": 0.10,
    },
    "ev_charging": {
        "population": 0.15,
        "transport": 0.30,
        "competition": 0.15,
        "zoning": 0.15,
        "risk": 0.10,
        "demand": 0.15,
    },
    "warehouse": {
        "population": 0.05,
        "transport": 0.35,
        "competition": 0.10,
        "zoning": 0.25,
        "risk": 0.15,
        "demand": 0.10,
    },
    "salon": {
        "population": 0.30,
        "transport": 0.10,
        "competition": 0.25,
        "zoning": 0.10,
        "risk": 0.10,
        "demand": 0.15,
    },
    "restaurant": {
        "population": 0.30,
        "transport": 0.10,
        "competition": 0.20,
        "zoning": 0.10,
        "risk": 0.10,
        "demand": 0.20,
    },
    "hospital": {
        "population": 0.25,
        "transport": 0.20,
        "competition": 0.10,
        "zoning": 0.15,
        "risk": 0.20,
        "demand": 0.10,
    },
    "gym": {
        "population": 0.25,
        "transport": 0.10,
        "competition": 0.25,
        "zoning": 0.10,
        "risk": 0.10,
        "demand": 0.20,
    },
    "default": {
        "population": 0.20,
        "transport": 0.20,
        "competition": 0.15,
        "zoning": 0.15,
        "risk": 0.15,
        "demand": 0.15,
    },
}
