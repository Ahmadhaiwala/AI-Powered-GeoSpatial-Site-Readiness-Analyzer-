"""
Rule-based chatbot service.
Parses natural language queries into structured scoring/recommendation requests.
"""
import re
from typing import Dict, Optional, Tuple

from backend.config import BUSINESS_WEIGHTS, CENTER_LAT, CENTER_LNG


# ──────────────────────────────────────────────
# Keyword maps for intent detection
# ──────────────────────────────────────────────

BUSINESS_KEYWORDS = {
    "salon": ["salon", "hair", "beauty", "spa", "parlour", "parlor", "barber"],
    "restaurant": ["restaurant", "food", "cafe", "dining", "eatery", "eat", "biryani", "pizza"],
    "gym": ["gym", "fitness", "workout", "exercise"],
    "retail_store": ["retail", "store", "shop", "mall", "supermarket", "grocery"],
    "ev_charging": ["ev", "charging", "electric vehicle", "charger", "tesla"],
    "hospital": ["hospital", "clinic", "medical", "healthcare", "doctor"],
    "warehouse": ["warehouse", "storage", "godown", "logistics", "distribution"],
}

LOCATION_KEYWORDS = {
    "center": {"lat": CENTER_LAT, "lng": CENTER_LNG, "label": "city center"},
    "navrangpura": {"lat": 23.0395, "lng": 72.5600, "label": "Navrangpura"},
    "bodakdev": {"lat": 23.0490, "lng": 72.5060, "label": "Bodakdev"},
    "vastrapur": {"lat": 23.0282, "lng": 72.5290, "label": "Vastrapur"},
    "satellite": {"lat": 23.0261, "lng": 72.5254, "label": "Satellite"},
    "prahlad nagar": {"lat": 23.0050, "lng": 72.5050, "label": "Prahlad Nagar"},
    "sg highway": {"lat": 23.0500, "lng": 72.4950, "label": "SG Highway"},
    "maninagar": {"lat": 22.9990, "lng": 72.6050, "label": "Maninagar"},
    "naroda": {"lat": 23.0800, "lng": 72.6500, "label": "Naroda"},
    "sabarmati": {"lat": 23.0770, "lng": 72.5890, "label": "Sabarmati"},
    "odhav": {"lat": 23.0200, "lng": 72.6500, "label": "Odhav"},
    "college": {"lat": 23.0395, "lng": 72.5600, "label": "near college area"},
    "university": {"lat": 23.0215, "lng": 72.5780, "label": "near university area"},
}

INTENT_PATTERNS = {
    "evaluate": [r"evaluat", r"score", r"rate", r"how good", r"check"],
    "recommend": [r"best", r"recommend", r"suggest", r"find", r"where", r"top", r"optimal"],
}


def _detect_business_type(text: str) -> Optional[str]:
    """Detect business type from text."""
    text_lower = text.lower()
    for btype, keywords in BUSINESS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return btype
    return None


def _detect_location(text: str) -> Optional[Dict]:
    """Detect a location reference from text."""
    text_lower = text.lower()
    for loc_key, loc_data in LOCATION_KEYWORDS.items():
        if loc_key in text_lower:
            return loc_data
    return None


def _detect_intent(text: str) -> str:
    """Detect whether user wants to evaluate or get recommendations."""
    text_lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                return intent
    return "recommend"  # default intent


def parse_chat_message(message: str) -> Dict:
    """
    Parse a natural language message into a structured query.

    Returns:
        dict with: intent, business_type, location, reply, needs_action
    """
    business_type = _detect_business_type(message)
    location = _detect_location(message)
    intent = _detect_intent(message)

    # Build reply
    parts = []
    needs_action = False

    if business_type:
        parts.append(f"I detected you're looking for: **{business_type.replace('_', ' ').title()}**")
    else:
        parts.append("I couldn't detect a specific business type. Could you specify? (e.g., salon, restaurant, gym, warehouse, EV charging)")

    if location:
        parts.append(f"Location: **{location['label']}** ({location['lat']}, {location['lng']})")
    else:
        parts.append("No specific location mentioned — I'll search the general city area.")
        # Default to city center for recommendations
        location = {"lat": CENTER_LAT, "lng": CENTER_LNG, "label": "city center"}

    if business_type:
        if intent == "evaluate":
            parts.append(f"\n📍 I'll evaluate **{location['label']}** for a {business_type.replace('_', ' ')}...")
        else:
            parts.append(f"\n🔍 I'll find the **best areas** for a {business_type.replace('_', ' ')} near {location['label']}...")
        needs_action = True
    else:
        parts.append("\nPlease specify a business type so I can help you!")

    return {
        "intent": intent,
        "business_type": business_type,
        "location": location,
        "reply": "\n".join(parts),
        "needs_action": needs_action,
    }
