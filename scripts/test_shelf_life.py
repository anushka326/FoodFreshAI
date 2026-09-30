"""
FoodFresh AI - Validation Script for FoodKeeper Shelf-Life Service (Phase 15)
Tests: Apple, Banana, Orange, Mango, Bread, Tomato, Pomegranate, and an unsupported food.
"""

from pathlib import Path
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.services.shelf_life_service import get_foodkeeper_service

TEST_CASES = [
    {"food": "Apple", "storage": "countertop", "days_stored": 2, "freshness": "Fresh"},
    {"food": "Apple", "storage": "fridge", "days_stored": 5, "freshness": "Fresh"},
    {"food": "Banana", "storage": "countertop", "days_stored": 1, "freshness": "Slightly Spoiled"},
    {"food": "Orange", "storage": "countertop", "days_stored": 3, "freshness": "Fresh"},
    {"food": "Mango", "storage": "countertop", "days_stored": 2, "freshness": "Fresh"},
    {"food": "Bread", "storage": "countertop", "days_stored": 4, "freshness": "Fresh"},
    {"food": "Tomato", "storage": "countertop", "days_stored": 3, "freshness": "Slightly Spoiled"},
    {"food": "Pomegranate", "storage": "countertop", "days_stored": 1, "freshness": "Fresh"},
    {"food": "Pomegranate", "storage": "fridge", "days_stored": 10, "freshness": "Fresh"},
    {"food": "Space Alien Food X99", "storage": "countertop", "days_stored": 0, "freshness": "Fresh"},  # Unsupported case
]


def test_shelf_life_integration():
    service = get_foodkeeper_service()
    print("=" * 70)
    print(f"FOODKEEPER SERVICE INITIALIZED — Loaded {len(service.products)} products")
    print("=" * 70)

    for tc in TEST_CASES:
        food = tc["food"]
        storage = tc["storage"]
        days = tc["days_stored"]
        freshness = tc["freshness"]

        res = service.get_shelf_life_guidance(
            food_name=food,
            storage_type=storage,
            days_stored=days,
            freshness_label=freshness
        )

        print(f"\n--- Testing: {food} (Storage: {storage}, Stored: {days}d, Freshness: {freshness}) ---")
        print(f"  Status:             {res.get('status')}")
        print(f"  Matched Food:       {res.get('matchedFood')}")
        print(f"  Reference Duration: {res.get('referenceDuration')}")
        print(f"  Remaining Window:   {res.get('remaining')} {res.get('unit', '')}")
        print(f"  Source:             {res.get('source')}")
        if res.get("reason"):
            print(f"  Reason:             {res.get('reason')}")
        if res.get("heuristicAdjustment"):
            print(f"  Heuristic Note:     {res.get('heuristicAdjustment')}")

    print("\n" + "=" * 70)
    print("ALL FOODKEEPER TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    test_shelf_life_integration()
