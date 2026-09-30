"""
FoodFresh AI - Shelf-Life Module
Provides FoodKeeper-based shelf-life estimation and pantry guidance.
"""

from backend.app.services.shelf_life_service import FoodKeeperService, get_foodkeeper_service

__all__ = ["FoodKeeperService", "get_foodkeeper_service"]
