"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import BUSINESS_WEIGHTS
from backend.controllers import (
    evaluate_controller,
    recommend_controller,
    demand_controller,
    chat_controller,
)

app = FastAPI(
    title="GeoSpatial Site Readiness Analyzer",
    description="AI-Powered platform for evaluating and recommending optimal business locations",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(evaluate_controller.router)
app.include_router(recommend_controller.router)
app.include_router(demand_controller.router)
app.include_router(chat_controller.router)


@app.get("/")
async def root():
    return {
        "name": "GeoSpatial Site Readiness Analyzer",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/business-types")
async def get_business_types():
    """List all supported business types with their weight profiles."""
    return [
        {
            "key": key,
            "label": key.replace("_", " ").title(),
            "weights": weights,
        }
        for key, weights in BUSINESS_WEIGHTS.items()
        if key != "default"
    ]
