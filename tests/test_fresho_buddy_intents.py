"""
FreshoBuddy intent detection and context level tests.
"""

from backend.app.services.fresho_intent_service import (
    ContextLevel,
    FreshoIntent,
    detect_fresho_intent,
)


def test_strong_pantry_priority_intents():
    questions = [
        "Which food should I eat first?",
        "What should I use before it goes bad?",
        "Which food has the shortest remaining quality?",
    ]
    for q in questions:
        intent, level, _ = detect_fresho_intent(q)
        assert level == ContextLevel.STRONG
        assert intent in (FreshoIntent.PANTRY_PRIORITY, FreshoIntent.EXPIRING_SOON)


def test_pantry_list_intent():
    intent, level, _ = detect_fresho_intent("What foods do I have?")
    assert intent == FreshoIntent.PANTRY_LIST
    assert level == ContextLevel.STRONG


def test_storage_advice_medium():
    intent, level, target = detect_fresho_intent("How should I store apples?")
    assert intent == FreshoIntent.STORAGE_ADVICE
    assert level == ContextLevel.MEDIUM
    assert target is not None


def test_general_freshness_simple():
    intent, level, _ = detect_fresho_intent("Why do bananas get brown spots?")
    assert intent == FreshoIntent.FRESHNESS_EXPLANATION
    assert level == ContextLevel.SIMPLE


def test_cook_today_strong():
    intent, level, _ = detect_fresho_intent("What should I cook today?")
    assert intent == FreshoIntent.COOK_TODAY
    assert level == ContextLevel.STRONG


def test_expiring_soon():
    intent, level, _ = detect_fresho_intent("What food needs attention?")
    assert level == ContextLevel.STRONG
