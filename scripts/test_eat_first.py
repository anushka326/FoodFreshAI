"""
FoodFresh AI - Validation Script for Eat First Priority Service (Phase 16)
Tests deterministic priority calculations and multi-item ranking.
"""

from pathlib import Path
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.services.eat_first_service import get_eat_first_service

TEST_CASES = [
    {
        "name": "Food A (Banana)",
        "shelfLife": {
            "status": "available",
            "food": "Banana",
            "remaining": {"minDays": 1, "maxDays": 2},
            "source": "USDA FoodKeeper + freshness adjustment"
        },
        "freshness": {"label": "Slightly Spoiled"}
    },
    {
        "name": "Food B (Apple in Fridge)",
        "shelfLife": {
            "status": "available",
            "food": "Apple",
            "remaining": {"minDays": 20, "maxDays": 35},
            "source": "USDA FoodKeeper"
        },
        "freshness": {"label": "Fresh"}
    },
    {
        "name": "Food C (Tomato on Counter)",
        "shelfLife": {
            "status": "available",
            "food": "Tomato",
            "remaining": {"minDays": 2, "maxDays": 3},
            "source": "USDA FoodKeeper"
        },
        "freshness": {"label": "Fresh"}
    },
    {
        "name": "Food D (Rotten Peach)",
        "shelfLife": {
            "status": "available",
            "food": "Peach",
            "remaining": {"minDays": 0, "maxDays": 0},
            "source": "USDA FoodKeeper + freshness adjustment"
        },
        "freshness": {"label": "Rotten"}
    },
    {
        "name": "Food E (Bread on Counter)",
        "shelfLife": {
            "status": "available",
            "food": "Bread",
            "remaining": {"minDays": 4, "maxDays": 6},
            "source": "USDA FoodKeeper"
        },
        "freshness": {"label": "Fresh"}
    },
    {
        "name": "Food F (Unsupported / Unavailable)",
        "shelfLife": {
            "status": "unavailable",
            "food": "Mystery Item",
            "remaining": None
        },
        "freshness": {"label": "Fresh"}
    }
]


def test_eat_first_service():
    service = get_eat_first_service()
    print("=" * 70)
    print("EAT FIRST SERVICE EVALUATION — INDIVIDUAL ITEMS")
    print("=" * 70)

    for tc in TEST_CASES:
        res = service.evaluate_priority(tc["shelfLife"], tc["freshness"]["label"])
        print(f"\nItem: {tc['name']}")
        print(f"  Shelf-Life Input:   {tc['shelfLife'].get('remaining')}")
        print(f"  Freshness Input:    {tc['freshness'].get('label')}")
        print(f"  Status:             {res.get('status')}")
        print(f"  Priority:           {res.get('priority')} (Score: {res.get('score')})")
        print(f"  Urgency:            {res.get('urgency')}")
        print(f"  Reason:             {res.get('reason')}")

    print("\n" + "=" * 70)
    print("MULTI-FOOD CONSUMPTION RANKING TEST")
    print("=" * 70)

    ranked = service.rank_foods_for_consumption(TEST_CASES)
    print("\nRanked Consumption Order (Most Urgent -> Least Urgent):")
    for idx, item in enumerate(ranked, 1):
        p_res = item["eatFirstPriority"]
        print(
            f"  {idx}. {item['name']}: Priority {p_res.get('priority')} "
            f"(Score {p_res.get('score')}) — {p_res.get('reason')}"
        )

    print("\n" + "=" * 70)
    print("EAT FIRST VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    test_eat_first_service()
