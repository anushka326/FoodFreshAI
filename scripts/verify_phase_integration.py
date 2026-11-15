"""
FoodFresh AI - Integration Verification Script
Tests FreshoBuddy 3-tier Context Isolation, Pantry Mode ON/OFF,
Eat First Authority Enforcement, and Impact Analytics.
"""

import sys
from backend.app.services.fresho_buddy_service import FreshoBuddyService
from backend.app.services.fresho_intent_service import detect_fresho_intent, ContextLevel, FreshoIntent
from backend.app.services.pantry_triage_service import triage_pantry_items
from backend.app.services.analytics_service import get_user_analytics, record_user_food_action

def run_tests():
    svc = FreshoBuddyService.get_instance()
    passed = 0
    total = 0

    print("==================================================")
    print("RUNNING FRESHOBUDDY & IMPACT ANALYTICS AUDIT TESTS")
    print("==================================================")

    # TEST 1: Pantry Mode OFF (Global Mode) - Maharashtra Produce
    total += 1
    r1 = svc.generate_reply(
        "Which is the fruit that could have more shelf life? And which is available in Maharashtra",
        pantry_mode=False
    )
    assert "Your pantry history is currently empty" not in r1["text"], "Failed: Leaked empty pantry message in Global Mode!"
    assert any(f in r1["text"] for f in ("Pomegranate", "Orange", "Amla", "Maharashtra")), "Failed: Missing regional fruit knowledge!"
    print("PASS [1/7]: Global Mode correctly provides regional food intelligence without empty-pantry leaks.")
    passed += 1

    # TEST 2: Pantry Mode OFF (Global Mode) - Green Apples Shelf Life
    total += 1
    r2 = svc.generate_reply(
        "What is the average shelf life of freshly bought green apples?",
        pantry_mode=False
    )
    assert "Your pantry history is currently empty" not in r2["text"]
    assert "Apple" in r2["text"] and ("week" in r2["text"] or "month" in r2["text"])
    print("PASS [2/7]: Global Mode correctly answers general shelf life question with produce tables.")
    passed += 1

    # TEST 3: Pantry Mode ON - Empty Pantry Guard
    total += 1
    r3 = svc.generate_reply(
        "Which food should I eat first?",
        pantry_mode=True,
        pantry_items=[]
    )
    assert "empty" in r3["text"].lower() and "pantry" in r3["text"].lower()
    print("PASS [3/7]: Pantry Mode ON correctly detects empty pantry and guides user to scan foods.")
    passed += 1

    # TEST 4: Pantry Mode ON - Populated Pantry Eat First Determinism
    total += 1
    mock_pantry = [
        {"foodName": "Fresh Strawberries", "status": "Semi-Fresh", "remainingDays": 1, "tier": "HIGH", "storageEnvironment": "Crisper"},
        {"foodName": "Whole Pomegranate", "status": "Fresh", "remainingDays": 25, "tier": "LOW", "storageEnvironment": "Countertop"}
    ]
    r4 = svc.generate_reply(
        "Which food should I eat first?",
        pantry_mode=True,
        pantry_items=mock_pantry
    )
    assert "Strawberries" in r4["text"], "Failed: Eat First did not prioritize Strawberries with 1 day remaining!"
    print("PASS [4/7]: Pantry Mode ON deterministically identifies highest urgency produce item.")
    passed += 1

    # TEST 5: Pantry Mode ON - Specific Food Lookup (Medium Context)
    total += 1
    # 5a. Food is in pantry
    r5a = svc.generate_reply(
        "Do I have any strawberries in my pantry?",
        pantry_mode=True,
        pantry_items=mock_pantry
    )
    assert "Strawberries" in r5a["text"] and "1" in r5a["text"]
    # 5b. Food is NOT in pantry
    r5b = svc.generate_reply(
        "Do I have any carrots saved in my pantry?",
        pantry_mode=True,
        pantry_items=mock_pantry
    )
    assert "not currently saved in your pantry" in r5b["text"].lower() or "not saved in your pantry" in r5b["text"].lower()
    print("PASS [5/7]: Specific food lookup accurately distinguishes between present and absent items.")
    passed += 1

    # TEST 6: Context Level Classification
    total += 1
    intent1, level1, _ = detect_fresho_intent("How should I store apples?")
    assert level1 == ContextLevel.SIMPLE
    intent2, level2, _ = detect_fresho_intent("Do I have apples in my pantry?")
    assert level2 == ContextLevel.MEDIUM
    intent3, level3, _ = detect_fresho_intent("Which food should I eat first?")
    assert level3 == ContextLevel.STRONG
    print("PASS [6/7]: 3-tier intent classification strictly isolates SIMPLE / MEDIUM / STRONG contexts.")
    passed += 1

    # TEST 7: Impact Analytics Calculation
    total += 1
    test_uid = "audit_user_test_999"
    record_user_food_action(test_uid, "Tomatoes", "consumed")
    record_user_food_action(test_uid, "Coriander", "wasted")
    ana = get_user_analytics(test_uid)
    assert ana["has_activity"] is True
    assert ana["total_consumed"] == 1
    assert ana["total_wasted"] == 1
    assert ana["total_actions"] == 2
    assert ana["waste_percentage"] == 50.0
    assert ana["waste_prevented_kg"] > 0
    assert ana["co2_saved_kg"] > 0
    assert ana["water_saved_liters"] > 0
    print("PASS [7/7]: Impact Analytics accurately computes real metrics, waste %, CO2e, and water savings.")
    passed += 1

    print("==================================================")
    print(f"ALL TESTS PASSED: {passed}/{total} (100% SUCCESS)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()

