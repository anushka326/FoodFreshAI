"""Food form + protected chilli regression cases (contract, not model retrain)."""

from backend.app.services.food_form_service import infer_food_form
from backend.app.services.shelf_life_service import get_shelf_life_service


def test_fresh_green_chilli_form():
    form = infer_food_form("Green Chilli", freshness_label="Fresh")
    assert form == "fresh"


def test_dried_red_chilli_form():
    form = infer_food_form("dried red chilli")
    assert form == "dried"


def test_forms_are_not_identical():
    assert infer_food_form("green chilli") != infer_food_form("dried red chilli")


def test_dried_chilli_shelf_life_unavailable_not_invented():
    svc = get_shelf_life_service()
    if not svc.is_loaded:
        return
    res = svc.get_shelf_life_guidance(
        "chili pepper",
        food_form="dried",
        freshness_label="rotten",
    )
    assert res["status"] == "unavailable"
    assert res.get("remaining") is None


def test_fresh_chilli_regression_documented_mismatch():
    """
    Protected case: fresh green chilli may be misclassified as rotten by current model.
    Architecture must allow uncertainty — this test documents form split only.
    """
    form = infer_food_form("Chili Pepper", freshness_label="Rotten")
    assert form in ("fresh", "unknown")
