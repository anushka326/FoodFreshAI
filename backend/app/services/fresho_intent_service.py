"""
Lightweight NLP-style intent detection for FreshoBuddy (keyword + phrase rules).
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional, Tuple


class ContextLevel(str, Enum):
    SIMPLE = "simple"  # Level 1 — general food education
    MEDIUM = "medium"  # Level 2 — optional pantry when relevant
    STRONG = "strong"  # Level 3 — pantry required


class FreshoIntent(str, Enum):
    PANTRY_PRIORITY = "PANTRY_PRIORITY"
    PANTRY_LIST = "PANTRY_LIST"
    EXPIRING_SOON = "EXPIRING_SOON"
    COOK_TODAY = "COOK_TODAY"
    STORAGE_ADVICE = "STORAGE_ADVICE"
    FRESHNESS_EXPLANATION = "FRESHNESS_EXPLANATION"
    FOOD_WASTE = "FOOD_WASTE"
    GENERAL_FOOD_QUESTION = "GENERAL_FOOD_QUESTION"
    ANALYSIS_CONTEXT = "ANALYSIS_CONTEXT"
    FOLLOW_UP = "FOLLOW_UP"


def normalize(text: str) -> str:
    q = (text or "").lower().strip()
    q = re.sub(r"[^\w\s?']", " ", q)
    q = re.sub(r"\s+", " ", q)
    return q


def detect_fresho_intent(
    query: str,
    *,
    has_analysis_context: bool = False,
    is_short_follow_up: bool = False,
) -> Tuple[FreshoIntent, ContextLevel, Optional[str]]:
    """
    Returns (intent, context_level, optional_target_food).
    """
    q = normalize(query)

    if is_short_follow_up or _is_follow_up(q):
        return FreshoIntent.FOLLOW_UP, ContextLevel.MEDIUM, None

    if has_analysis_context and any(p in q for p in ("this food", "tell me about this", "this item")):
        return FreshoIntent.ANALYSIS_CONTEXT, ContextLevel.MEDIUM, None

    # STRONG — pantry priority / inventory
    if any(
        p in q
        for p in (
            "eat first",
            "use first",
            "consume first",
            "what should i eat first",
            "which food should i eat first",
            "before it goes bad",
            "shortest remaining quality",
            "closest to its quality limit",
            "needs attention",
            "pantry situation",
            "show me my pantry",
        )
    ):
        if "what foods do i have" in q or "what food do i have" in q or "list my food" in q:
            return FreshoIntent.PANTRY_LIST, ContextLevel.STRONG, None
        if "expir" in q or "going bad" in q or "attention" in q:
            return FreshoIntent.EXPIRING_SOON, ContextLevel.STRONG, None
        return FreshoIntent.PANTRY_PRIORITY, ContextLevel.STRONG, None

    if any(p in q for p in ("what foods do i have", "what food do i have", "my pantry", "logged food", "saved food")):
        return FreshoIntent.PANTRY_LIST, ContextLevel.STRONG, None

    if any(p in q for p in ("expiring soon", "expire soon", "going bad soon")):
        return FreshoIntent.EXPIRING_SOON, ContextLevel.STRONG, None

    if any(p in q for p in ("cook today", "cook tonight", "what should i cook", "what to make today")):
        return FreshoIntent.COOK_TODAY, ContextLevel.STRONG, None

    # MEDIUM — mentions having foods
    if re.search(r"\bi have\b", q) and any(f in q for f in ("mango", "tomato", "apple", "banana", "pantry")):
        if "store" in q or "storage" in q or "keep" in q:
            target = _extract_food_noun(q)
            return FreshoIntent.STORAGE_ADVICE, ContextLevel.MEDIUM, target
        return FreshoIntent.PANTRY_LIST, ContextLevel.MEDIUM, None

    store_match = re.search(r"how (?:should|to|do) i store (?:this |the |my )?([a-z\s]+)", q)
    if store_match:
        target = store_match.group(1).replace("?", "").strip()
        target = re.sub(r"\b(?:properly|correctly|well|today)\b", "", target).strip()
        return FreshoIntent.STORAGE_ADVICE, ContextLevel.MEDIUM, target or None

    if any(p in q for p in ("slightly spoiled", "what is slightly spoiled", "what does slightly spoiled mean")):
        return FreshoIntent.FRESHNESS_EXPLANATION, ContextLevel.SIMPLE, None

    if any(p in q for p in ("brown spot", "turn brown", "banana", "why do bananas")):
        return FreshoIntent.FRESHNESS_EXPLANATION, ContextLevel.SIMPLE, None

    if "waste" in q and ("reduce" in q or "food" in q):
        return FreshoIntent.FOOD_WASTE, ContextLevel.MEDIUM, None

    return FreshoIntent.GENERAL_FOOD_QUESTION, ContextLevel.SIMPLE, None


def _is_follow_up(q: str) -> bool:
    if len(q.split()) <= 8 and any(
        p in q
        for p in (
            "why that one",
            "why that",
            "that one",
            "how should i store it",
            "store it",
            "what about it",
            "tell me more about it",
        )
    ):
        return True
    return q.strip() in ("why?", "why", "how?", "how")


def _extract_food_noun(q: str) -> Optional[str]:
    for word in ("mangoes", "mango", "tomatoes", "tomato", "apples", "apple", "bananas", "banana"):
        if word in q:
            return word.rstrip("s") if word.endswith("es") else word.rstrip("s") if word.endswith("s") and word != "mango" else word
    return None


def map_fresho_intent_to_pantry_intent(fresho_intent: FreshoIntent) -> str:
    from backend.app.services.pantry_triage_service import PantryIntent

    mapping = {
        FreshoIntent.PANTRY_PRIORITY: PantryIntent.EAT_FIRST,
        FreshoIntent.PANTRY_LIST: PantryIntent.PANTRY_INVENTORY,
        FreshoIntent.EXPIRING_SOON: PantryIntent.EXPIRING_SOON,
        FreshoIntent.COOK_TODAY: PantryIntent.COOK_TODAY,
        FreshoIntent.STORAGE_ADVICE: PantryIntent.SPECIFIC_FOOD_STORAGE,
        FreshoIntent.FOOD_WASTE: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.FRESHNESS_EXPLANATION: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.GENERAL_FOOD_QUESTION: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.ANALYSIS_CONTEXT: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.FOLLOW_UP: PantryIntent.GENERAL_EDUCATIONAL,
    }
    return mapping.get(fresho_intent, PantryIntent.GENERAL_EDUCATIONAL)
