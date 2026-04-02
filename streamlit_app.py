"""
Streamlit test UI for the GeoSpatial Site Readiness Analyzer.
Run: streamlit run streamlit_app.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json

from backend.config import CENTER_LAT, CENTER_LNG, BUSINESS_WEIGHTS
from backend.services.scoring_service import compute_score
from backend.services.recommendation_service import recommend_locations
from backend.services.explainer_service import explain_score
from backend.services.demand_service import add_vote, get_all_votes, get_demand_hotspots
from backend.services.chatbot_service import parse_chat_message

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="GeoSpatial Site Readiness Analyzer",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 GeoSpatial Site Readiness Analyzer")
st.caption("AI-Powered location intelligence for optimal business placement")

# ──────────────────────────────────────────────
# Sidebar — Business Type & Controls
# ──────────────────────────────────────────────
st.sidebar.header("⚙️ Configuration")

business_types = [k for k in BUSINESS_WEIGHTS.keys() if k != "default"]
selected_business = st.sidebar.selectbox(
    "Business Type",
    business_types,
    format_func=lambda x: x.replace("_", " ").title(),
)

radius_km = st.sidebar.slider("Analysis Radius (km)", 0.5, 5.0, 2.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Weight Profile")
weights = BUSINESS_WEIGHTS[selected_business]
for factor, weight in weights.items():
    st.sidebar.progress(weight, text=f"{factor.title()}: {weight:.0%}")

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📍 Evaluate Location", "🔍 Recommendations", "🗳️ Demand Voting", "🤖 Chatbot"])

# ──────────────────────────────────────────────
# Tab 1: Evaluate Location
# ──────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Click on the map to evaluate a location")

        # Create map
        m = folium.Map(location=[CENTER_LAT, CENTER_LNG], zoom_start=12)
        m.add_child(folium.LatLngPopup())

        map_data = st_folium(m, height=500, width=None, key="eval_map")

    with col2:
        # Manual coordinate input
        st.subheader("📍 Coordinates")
        input_lat = st.number_input("Latitude", value=CENTER_LAT, format="%.6f", key="eval_lat")
        input_lng = st.number_input("Longitude", value=CENTER_LNG, format="%.6f", key="eval_lng")

        # Use clicked location if available
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            input_lat = clicked["lat"]
            input_lng = clicked["lng"]
            st.info(f"📍 Clicked: ({input_lat:.4f}, {input_lng:.4f})")

        if st.button("🔍 Evaluate", type="primary", use_container_width=True):
            with st.spinner("Computing score..."):
                result = compute_score(
                    lat=input_lat,
                    lng=input_lng,
                    business_type=selected_business,
                    radius_km=radius_km,
                )

                # Score display
                score = result["total_score"]
                color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                st.metric("Total Score", f"{color} {score}/100")

                # Breakdown bars
                st.markdown("**Score Breakdown:**")
                for factor, value in result["breakdown"].items():
                    weight = result["weights"][factor]
                    weighted = value * weight * 100
                    st.progress(
                        min(value, 1.0),
                        text=f"{factor.title()}: {value:.2f} (weighted: {weighted:.1f})",
                    )

                # Explanation
                explanation = explain_score(result["breakdown"], result["weights"])

                if explanation["strengths"]:
                    st.markdown("**Strengths:**")
                    for s in explanation["strengths"]:
                        st.markdown(s)

                if explanation["weaknesses"]:
                    st.markdown("**Weaknesses:**")
                    for w in explanation["weaknesses"]:
                        st.markdown(w)

                if explanation["suggestions"]:
                    st.markdown("**Suggestions:**")
                    for s in explanation["suggestions"]:
                        st.markdown(s)

# ──────────────────────────────────────────────
# Tab 2: Recommendations
# ──────────────────────────────────────────────
with tab2:
    st.subheader("🔍 Find Best Locations")

    col1, col2 = st.columns(2)
    with col1:
        rec_center_lat = st.number_input("Center Latitude", value=CENTER_LAT, format="%.6f", key="rec_lat")
        rec_center_lng = st.number_input("Center Longitude", value=CENTER_LNG, format="%.6f", key="rec_lng")
    with col2:
        search_radius = st.slider("Search Area (degrees)", 0.01, 0.1, 0.03, 0.01, key="rec_radius")
        top_n = st.slider("Top N Results", 3, 20, 5, key="rec_topn")

    if st.button("🚀 Find Best Areas", type="primary", use_container_width=True):
        with st.spinner("Analyzing area with H3 grid... This may take a moment."):
            recs = recommend_locations(
                business_type=selected_business,
                min_lat=rec_center_lat - search_radius,
                max_lat=rec_center_lat + search_radius,
                min_lng=rec_center_lng - search_radius,
                max_lng=rec_center_lng + search_radius,
                top_n=top_n,
            )

            if recs:
                # Show on map
                rec_map = folium.Map(
                    location=[rec_center_lat, rec_center_lng],
                    zoom_start=13,
                )

                for r in recs:
                    color = "green" if r["score"] >= 70 else "orange" if r["score"] >= 40 else "red"
                    folium.Marker(
                        [r["lat"], r["lng"]],
                        popup=f"#{r['rank']} Score: {r['score']}",
                        tooltip=f"#{r['rank']} — {r['score']}/100",
                        icon=folium.Icon(color=color, icon="star"),
                    ).add_to(rec_map)

                st_folium(rec_map, height=400, key="rec_map")

                # Results table
                st.markdown("**🏆 Top Recommended Locations:**")
                for r in recs:
                    emoji = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉" if r["rank"] == 3 else f"#{r['rank']}"
                    st.markdown(
                        f"{emoji} **Score: {r['score']}** — ({r['lat']:.4f}, {r['lng']:.4f}) | H3: `{r['h3_index']}`"
                    )
            else:
                st.warning("No results found in this area.")

# ──────────────────────────────────────────────
# Tab 3: Demand Voting
# ──────────────────────────────────────────────
with tab3:
    st.subheader("🗳️ What do you want in your area?")

    col1, col2 = st.columns([2, 1])

    with col2:
        vote_lat = st.number_input("Latitude", value=CENTER_LAT, format="%.6f", key="vote_lat")
        vote_lng = st.number_input("Longitude", value=CENTER_LNG, format="%.6f", key="vote_lng")
        vote_category = st.selectbox("What do you want?", business_types, format_func=lambda x: x.replace("_", " ").title(), key="vote_cat")
        vote_comment = st.text_input("Comment (optional)", key="vote_comment")

        if st.button("🗳️ Cast Vote", type="primary", use_container_width=True):
            result = add_vote(vote_lat, vote_lng, vote_category, vote_comment or None)
            st.success(result["message"])

    with col1:
        # Show existing votes on map
        vote_map = folium.Map(location=[CENTER_LAT, CENTER_LNG], zoom_start=12)

        votes = get_all_votes()
        for v in votes:
            folium.CircleMarker(
                [v["lat"], v["lng"]],
                radius=6,
                popup=f"{v['category']} — {v.get('comment', '')}",
                color="purple",
                fill=True,
                fill_opacity=0.7,
            ).add_to(vote_map)

        # Show hotspots
        hotspots = get_demand_hotspots()
        for h in hotspots:
            folium.CircleMarker(
                [h["lat"], h["lng"]],
                radius=10 + h["count"] * 3,
                popup=f"🔥 {h['category']}: {h['count']} votes",
                color="red",
                fill=True,
                fill_opacity=0.5,
            ).add_to(vote_map)

        st_folium(vote_map, height=400, key="vote_map")

        if votes:
            st.markdown(f"**Total votes recorded:** {len(votes)}")
        if hotspots:
            st.markdown("**🔥 Demand Hotspots:**")
            for h in hotspots:
                st.markdown(f"- {h['category'].title()}: {h['count']} votes at ({h['lat']:.4f}, {h['lng']:.4f})")

# ──────────────────────────────────────────────
# Tab 4: Chatbot
# ──────────────────────────────────────────────
with tab4:
    st.subheader("🤖 Ask the GeoAI Assistant")
    st.caption("Try: 'Find best place for a salon near Koramangala' or 'Where should I open a restaurant near MG Road?'")

    # Chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask me about business locations...")

    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                parsed = parse_chat_message(user_input)
                reply = parsed["reply"]

                # If action needed, run it
                if parsed["needs_action"] and parsed["business_type"] and parsed["location"]:
                    loc = parsed["location"]

                    if parsed["intent"] == "evaluate":
                        result = compute_score(
                            lat=loc["lat"],
                            lng=loc["lng"],
                            business_type=parsed["business_type"],
                        )
                        score = result["total_score"]
                        color_emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                        reply += f"\n\n{color_emoji} **Score: {score}/100**"
                        for f, v in result["breakdown"].items():
                            reply += f"\n- {f.title()}: {v:.2f}"

                        explanation = explain_score(result["breakdown"], result["weights"])
                        if explanation["strengths"]:
                            reply += "\n\n**Strengths:**"
                            for s in explanation["strengths"]:
                                reply += f"\n{s}"
                        if explanation["suggestions"]:
                            reply += "\n\n**Suggestions:**"
                            for s in explanation["suggestions"]:
                                reply += f"\n{s}"
                    else:
                        delta = 0.03
                        recs = recommend_locations(
                            business_type=parsed["business_type"],
                            min_lat=loc["lat"] - delta,
                            max_lat=loc["lat"] + delta,
                            min_lng=loc["lng"] - delta,
                            max_lng=loc["lng"] + delta,
                            top_n=5,
                        )
                        if recs:
                            reply += "\n\n**🏆 Top Locations:**"
                            for r in recs:
                                emoji = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉" if r["rank"] == 3 else f"#{r['rank']}"
                                reply += f"\n{emoji} Score: {r['score']} — ({r['lat']:.4f}, {r['lng']:.4f})"

                st.markdown(reply)

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
