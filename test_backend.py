"""Quick test of core services."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.scoring_service import compute_score
from backend.services.recommendation_service import recommend_locations
from backend.services.explainer_service import explain_score
from backend.services.chatbot_service import parse_chat_message

print("=" * 50)
print("TEST 1: Scoring Engine")
print("=" * 50)
result = compute_score(12.9716, 77.5946, "salon")
print(f"Score: {result['total_score']}/100")
print("Breakdown:")
for k, v in result["breakdown"].items():
    print(f"  {k}: {v:.3f}")
print()

print("=" * 50)
print("TEST 2: Explainer")
print("=" * 50)
explanation = explain_score(result["breakdown"], result["weights"])
print("Strengths:", explanation["strengths"])
print("Weaknesses:", explanation["weaknesses"])
print("Suggestions:", explanation["suggestions"])
print()

print("=" * 50)
print("TEST 3: Chatbot")
print("=" * 50)
msg = "Find best place for a salon near Koramangala"
parsed = parse_chat_message(msg)
print(f"Input: {msg}")
print(f"Business Type: {parsed['business_type']}")
print(f"Location: {parsed['location']}")
print(f"Intent: {parsed['intent']}")
print(f"Reply:\n{parsed['reply']}")
print()

print("=" * 50)
print("TEST 4: Recommendations")
print("=" * 50)
recs = recommend_locations(
    business_type="salon",
    min_lat=12.95, max_lat=12.99,
    min_lng=77.57, max_lng=77.62,
    top_n=5,
)
print(f"Found {len(recs)} recommendations:")
for r in recs:
    print(f"  #{r['rank']} Score: {r['score']} at ({r['lat']:.4f}, {r['lng']:.4f})")

print()
print("ALL TESTS PASSED!")
