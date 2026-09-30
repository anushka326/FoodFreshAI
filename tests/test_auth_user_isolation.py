"""
User isolation for pantry records (backend SQLite).
"""

import uuid

from backend.app.database import chat_db
from backend.app.services.pantry_state_service import get_current_pantry_state


def test_pantry_user_isolation():
    user_a = f"test_user_a_{uuid.uuid4().hex[:8]}"
    user_b = f"test_user_b_{uuid.uuid4().hex[:8]}"

    chat_db.add_pantry_item(
        user_a,
        {
            "foodName": "Food A",
            "estimatedQualityDays": 3,
            "freshness": {"label": "Fresh"},
            "shelfLife": {"remaining": {"minDays": 3, "maxDays": 3}},
        },
    )
    chat_db.add_pantry_item(
        user_b,
        {"foodName": "Food C", "estimatedQualityDays": 5, "shelfLife": {"remaining": {"minDays": 5}}},
    )

    items_a = get_current_pantry_state(user_a)
    items_b = get_current_pantry_state(user_b)

    names_a = {i["foodName"] for i in items_a}
    names_b = {i["foodName"] for i in items_b}

    assert "Food A" in names_a
    assert "Food C" not in names_a
    assert "Food C" in names_b
    assert "Food A" not in names_b
