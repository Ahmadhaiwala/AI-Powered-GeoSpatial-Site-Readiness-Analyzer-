"""
In-memory data store. Loads synthetic data on startup.
"""
from backend.data.geojson_loader import load_all_real_data
from typing import List, Dict


class Database:
    """Singleton-ish in-memory data store."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Load real GeoJSON data
        data = load_all_real_data()
        self.population_centers: List[Dict] = data["population_centers"]
        self.roads: List[Dict] = data["roads"]
        self.competitors: List[Dict] = data["competitors"]
        self.zoning: List[Dict] = data["zoning"]
        self.risk_zones: List[Dict] = data["risk_zones"]

        # Demand votes storage
        self.votes: List[Dict] = []

    def add_vote(self, vote: Dict) -> int:
        """Add a demand vote. Returns total votes in area."""
        self.votes.append(vote)
        return len(self.votes)

    def get_votes(self) -> List[Dict]:
        """Return all votes."""
        return self.votes

    def get_competitors_by_category(self, category: str) -> List[Dict]:
        """Filter competitors by category."""
        return [c for c in self.competitors if c["category"] == category]


# Global database instance
db = Database()
