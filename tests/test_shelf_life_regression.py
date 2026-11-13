"""Shelf-life regression — FoodKeeper baseline, form-aware."""

import pytest

from backend.app.services.shelf_life_service import get_shelf_life_service

CASES = [
    ("Apple", "fresh", "countertop", 0, True),
    ("Banana", "fresh", "countertop", 0, True),
    ("Orange", "fresh", "countertop", 0, True),
    ("Tomato", "fresh", "countertop", 0, True),
    ("Mango", "fresh", "countertop", 0, True),
    ("Pomegranate", "fresh", "countertop", 0, True),
    ("Potato", "fresh", "countertop", 0, True),
    ("Bell Pepper", "fresh", "fridge", 0, True),
    ("green chilli", "fresh", "fridge", 0, True),
    ("dried red chilli", "dried", "countertop", 0, False),
    ("Cucumber", "fresh", "fridge", 0, True),
    ("Watermelon", "fresh", "countertop", 0, True),
    ("Cantaloupe", "fresh", "fridge", 0, True),
    ("Grape", "fresh", "fridge", 0, True),
    ("Strawberry", "fresh", "fridge", 0, False),
]


@pytest.mark.parametrize("food,form,storage,days,expect_available", CASES)
def test_shelf_life_foodkeeper_regression(food, form, storage, days, expect_available):
    svc = get_shelf_life_service()
    if not svc.is_loaded:
        pytest.skip("FoodKeeper.json not available in this environment")
    res = svc.get_shelf_life_guidance(
        food_name=food,
        storage_type=storage,
        days_stored=days,
        freshness_label="fresh",
        food_form=form,
    )
    if expect_available:
        assert res["status"] == "available", res.get("reason")
        assert res.get("referenceDuration") is not None
    else:
        assert res["status"] == "unavailable"
        mt = res.get("matchType")
        assert mt in ("form_unsupported", "unmatched") or "food form" in res.get("reason", "").lower()
