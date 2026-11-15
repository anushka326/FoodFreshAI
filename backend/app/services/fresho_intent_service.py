"""
FoodFresh AI - FreshoBuddy Intent & Context Detection Service
Provides 3-tier context isolation (SIMPLE / MEDIUM / STRONG), comprehensive produce alias mapping,
and deterministic pantry triage routing based on user queries and ownership patterns.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional, Tuple, Dict


class ContextLevel(str, Enum):
    SIMPLE = "simple"   # Level 1 — General food knowledge (no pantry query or injection)
    MEDIUM = "medium"   # Level 2 — Specific food lookup (loads only matching food or reports absent)
    STRONG = "strong"   # Level 3 — Whole pantry inventory & Eat First triage required


class FreshoIntent(str, Enum):
    PANTRY_PRIORITY = "PANTRY_PRIORITY"
    PANTRY_LIST = "PANTRY_LIST"
    EXPIRING_SOON = "EXPIRING_SOON"
    COOK_TODAY = "COOK_TODAY"
    PANTRY_ITEM_LOOKUP = "PANTRY_ITEM_LOOKUP"
    PANTRY_ITEM_STORAGE = "PANTRY_ITEM_STORAGE"
    STORAGE_ADVICE = "STORAGE_ADVICE"
    FRESHNESS_EXPLANATION = "FRESHNESS_EXPLANATION"
    FOOD_WASTE = "FOOD_WASTE"
    GENERAL_FOOD_QUESTION = "GENERAL_FOOD_QUESTION"
    ANALYSIS_CONTEXT = "ANALYSIS_CONTEXT"
    FOLLOW_UP = "FOLLOW_UP"


# Canonical food aliases covering plural, singular, and regional Indian variants
FOOD_ALIASES: Dict[str, str] = {
    "cherry tomatoes": "cherry tomato",
    "cherry tomato": "cherry tomato",
    "sweet potatoes": "sweet potato",
    "sweet potato": "sweet potato",
    "bell peppers": "bell pepper",
    "bell pepper": "bell pepper",
    "green chillies": "green chilli",
    "green chilli": "green chilli",
    "green chilis": "green chilli",
    "green chili": "green chilli",
    "chili peppers": "green chilli",
    "chili pepper": "green chilli",
    "hot peppers": "green chilli",
    "green beans": "green beans",
    "green bean": "green beans",
    "strawberries": "strawberry",
    "strawberry": "strawberry",
    "blueberries": "blueberry",
    "blueberry": "blueberry",
    "pomegranates": "pomegranate",
    "pomegranate": "pomegranate",
    "anar": "pomegranate",
    "watermelons": "watermelon",
    "watermelon": "watermelon",
    "pineapples": "pineapple",
    "pineapple": "pineapple",
    "cauliflowers": "cauliflower",
    "cauliflower": "cauliflower",
    "cucumbers": "cucumber",
    "cucumber": "cucumber",
    "eggplants": "eggplant",
    "eggplant": "eggplant",
    "aubergines": "eggplant",
    "aubergine": "eggplant",
    "brinjals": "eggplant",
    "brinjal": "eggplant",
    "beetroots": "beetroot",
    "beetroot": "beetroot",
    "beets": "beetroot",
    "beet": "beetroot",
    "avocados": "avocado",
    "avocado": "avocado",
    "tomatoes": "tomato",
    "tomato": "tomato",
    "potatoes": "potato",
    "potato": "potato",
    "mangoes": "mango",
    "mangos": "mango",
    "mango": "mango",
    "alphonso": "mango",
    "kesar": "mango",
    "bananas": "banana",
    "banana": "banana",
    "apples": "apple",
    "apple": "apple",
    "kashmiri apple": "apple",
    "kashmiri apples": "apple",
    "kashmir apple": "apple",
    "kashmir apples": "apple",
    "green apple": "apple",
    "green apples": "apple",
    "oranges": "orange",
    "orange": "orange",
    "mosambi": "orange",
    "sweet lime": "orange",
    "lemons": "lemon",
    "lemon": "lemon",
    "limes": "lime",
    "lime": "lime",
    "grapes": "grape",
    "grape": "grape",
    "papayas": "papaya",
    "papaya": "papaya",
    "chickoos": "chikoo",
    "chickoo": "chikoo",
    "chikus": "chikoo",
    "chiku": "chikoo",
    "chikoo": "chikoo",
    "sapota": "chikoo",
    "pears": "pear",
    "pear": "pear",
    "peaches": "peach",
    "peach": "peach",
    "plums": "plum",
    "plum": "plum",
    "guavas": "guava",
    "guava": "guava",
    "cherries": "cherry",
    "cherry": "cherry",
    "peppers": "bell pepper",
    "pepper": "bell pepper",
    "capsicums": "bell pepper",
    "capsicum": "bell pepper",
    "onions": "onion",
    "onion": "onion",
    "garlic": "garlic",
    "carrots": "carrot",
    "carrot": "carrot",
    "broccoli": "broccoli",
    "cabbage": "cabbage",
    "spinach": "spinach",
    "palak": "spinach",
    "methi": "fenugreek",
    "lettuce": "lettuce",
    "corn": "corn",
    "radishes": "radish",
    "radish": "radish",
    "ginger": "ginger",
    "mushrooms": "mushroom",
    "mushroom": "mushroom",
    "bread": "bread",
    "sourdough": "bread",
    "cakes": "cake",
    "cake": "cake",
    "milk": "milk",
    "cheese": "cheese",
    "paneer": "paneer",
    "yogurt": "yogurt",
    "kiwis": "kiwi",
    "kiwi": "kiwi",
    "dragonfruit": "dragonfruit",
    "figs": "fig",
    "fig": "fig",
    "anjeer": "fig",
    # Regional apple variants
    "kashmir apples": "apple",
    "kashmir apple": "apple",
    "kashmiri apples": "apple",
    "kashmiri apple": "apple",
    "himachal apple": "apple",
    "himachal apples": "apple",
    "green apples": "apple",
    "green apple": "apple",
    "red apple": "apple",
    "red apples": "apple",
    # Packaged and fresh beverages
    "cold drinks": "cold drink",
    "cold drink": "cold drink",
    "coldrinks": "cold drink",
    "coldrink": "cold drink",
    "soft drinks": "soft drink",
    "soft drink": "soft drink",
    "softdrinks": "soft drink",
    "softdrink": "soft drink",
    "carbonated drinks": "soft drink",
    "carbonated drink": "soft drink",
    "soda": "soft drink",
    "sodas": "soft drink",
    "cola": "soft drink",
    "coke": "soft drink",
    "pepsi": "soft drink",
    "sprite": "soft drink",
    "fanta": "soft drink",
    "energy drinks": "energy drink",
    "energy drink": "energy drink",
    "fruit juice": "fruit juice",
    "fruit juices": "fruit juice",
    "fresh juice": "fruit juice",
    "fresh juices": "fruit juice",
    "orange juice": "orange juice",
    "apple juice": "apple juice",
    "lemonade": "lemonade",
    "iced tea": "iced tea",
    "sports drinks": "sports drink",
    "sports drink": "sports drink",
    "beverages": "beverage",
    "beverage": "beverage",
    # Cooked food and leftovers
    "cooked rice": "cooked rice",
    "cooked food": "cooked food",
    "leftover food": "cooked food",
    "leftovers": "cooked food",
    "leftover": "cooked food",
    "cooked vegetables": "cooked food",
    "cooked meat": "cooked meat",
    "cooked chicken": "cooked chicken",
    "dal": "dal",
    "curry": "curry",
    "pasta": "pasta",
    "pizza": "pizza",
    "soup": "soup",
    "rice": "rice",
    "roti": "roti",
    "chapatis": "roti",
    "chapati": "roti",
    # Dairy & plant milks
    "curd": "yogurt",
    "dahi": "yogurt",
    "butter": "butter",
    "ghee": "ghee",
    "cream": "cream",
    "buttermilk": "buttermilk",
    "chaas": "buttermilk",
    "lassi": "lassi",
    "almond milk": "almond milk",
    "soy milk": "soy milk",
    "oat milk": "oat milk",
    # Meat, poultry & seafood
    "chicken": "chicken",
    "fish": "fish",
    "eggs": "egg",
    "egg": "egg",
    "meat": "meat",
    "mutton": "mutton",
    "prawns": "prawns",
    "shrimp": "prawns",
    "seafood": "seafood",
    # Bakery
    "buns": "bun",
    "bun": "bun",
    "bagel": "bagel",
    "cookies": "cookie",
    "cookie": "cookie",
    "biscuits": "biscuit",
    "biscuit": "biscuit",
    "pastries": "pastry",
    "pastry": "pastry",
}

# Sorted by length descending so multi-word variants match before single words
_SORTED_FOOD_KEYS = sorted(FOOD_ALIASES.keys(), key=lambda k: len(k), reverse=True)

OWNERSHIP_PATTERNS = [
    r"\bmy\s+saved\b",
    r"\bsaved\b",
    r"\bmy\s+logged\b",
    r"\blogged\b",
    r"\bin\s+my\s+pantry\b",
    r"\bfrom\s+my\s+pantry\b",
    r"\bmy\s+pantry\b",
    r"\bdo\s+i\s+(?:currently\s+)?have\b",
    r"\bhave\s+any\b",
    r"\bi\s+(?:currently\s+)?have\b",
    r"\bi\s+saved\b",
    r"\bi\s+logged\b",
    r"\bfor\s+my\b",
    r"\bof\s+my\b",
    r"\bis\s+my\b",
    r"\bare\s+my\b",
    r"\bcheck\s+my\b",
    r"\bstore\s+my\b",
]


def normalize(text: str) -> str:
    """Normalize query text for clean regex inspection."""
    q = (text or "").lower().strip()
    # Normalize common spelling variants
    q = re.sub(r"\bself[\s\-_]?life\b", "shelf life", q)
    q = re.sub(r"\bshelf[\-_]?life\b", "shelf life", q)
    q = re.sub(r"\bcold[\-_]?drinks?\b", "cold drink", q)
    q = re.sub(r"\bsoft[\-_]?drinks?\b", "soft drink", q)
    q = re.sub(r"[^\w\s?']", " ", q)
    q = re.sub(r"\s+", " ", q)
    return q


def has_pantry_ownership(q: str) -> bool:
    """Return True if query explicitly refers to user's saved/logged pantry property."""
    return any(re.search(pat, q) for pat in OWNERSHIP_PATTERNS)


def extract_food_noun(text: str) -> Optional[str]:
    """Extract canonical food noun from query string using alias dictionary and regex."""
    q = normalize(text)
    if not q:
        return None

    for key in _SORTED_FOOD_KEYS:
        if re.search(r"\b" + re.escape(key) + r"\b", q):
            return FOOD_ALIASES[key]

    fallback_patterns = [
        r"\b(?:my\s+saved|saved|my\s+logged|logged|my)\s+([a-z][a-z\s]{1,24}?)(?:\s+(?:in\s+my\s+pantry|left|remain|remaining|expire|last|yet|still|today)\b|\?|$)",
        r"\bdo\s+i\s+have\s+(?:any\s+)?([a-z][a-z\s]{1,24}?)(?:\s+in\s+my\s+pantry|\?|$)",
        r"\bhow\s+(?:should|to|do)(?:\s+i)?\s+store\s+(?:fresh\s+|ripe\s+|whole\s+)?([a-z][a-z\s]{1,24}?)(?:\?|$)",
    ]
    stop_tokens = {
        "food", "foods", "item", "items", "produce", "pantry", "it", "this",
        "that", "them", "things", "everything", "first", "one"
    }

    for pat in fallback_patterns:
        m = re.search(pat, q)
        if m and m.group(1):
            cand = re.sub(r"\b(?:fresh|ripe|whole|properly|correctly|well|today|any|some)\b", "", m.group(1)).strip()
            if cand and cand not in stop_tokens and len(cand.split()) <= 3:
                if cand.endswith("oes") and len(cand) > 4:
                    cand = cand[:-2]
                elif cand.endswith("ies") and len(cand) > 4:
                    cand = cand[:-3] + "y"
                elif cand.endswith("s") and len(cand) > 3 and not cand.endswith("ss"):
                    cand = cand[:-1]
                return cand

    return None


def is_follow_up_query(text: str) -> bool:
    """Detect if user query is a short follow-up referencing prior conversation turn."""
    q = re.sub(r"[?.!\s]+$", "", normalize(text))
    if not q:
        return False
    words = q.split()
    phrases = [
        "why that one",
        "why that",
        "why is it",
        "why is that",
        "that one",
        "how should i store it",
        "how to store it",
        "store it",
        "store them",
        "what about it",
        "what about that",
        "what about them",
        "tell me more about it",
        "tell me more",
        "how long will it last",
        "how long does it last",
        "how many days left for it",
        "explain why",
        "how can i increase it",
        "how to increase it",
        "increase it",
        "what if i refrigerate them",
        "what if i refrigerate it",
        "can i freeze it",
        "can i freeze them",
        "freeze it",
        "freeze them",
        "refrigerate them",
        "refrigerate it",
        "keep it longer",
        "extend its shelf life",
        "prolong its shelf life",
    ]
    if len(words) <= 12 and any(re.search(r"\b" + re.escape(p) + r"\b", q) for p in phrases):
        return True
    if len(words) <= 10 and re.search(r"\b(?:it|them|that|these|those)\b", q) and any(
        re.search(r"\b" + verb + r"\b", q)
        for verb in ("refrigerat", "freeze", "chill", "store", "keep", "increase", "extend", "prolong", "cook", "eat", "wash", "boil")
    ):
        return True
    return q in ("why", "how", "and storage", "what else", "more details")


def detect_fresho_intent(
    query: str,
    *,
    has_analysis_context: bool = False,
    is_short_follow_up: bool = False,
) -> Tuple[FreshoIntent, ContextLevel, Optional[str]]:
    """
    Returns (FreshoIntent, ContextLevel, target_food).
    Ensures strict context tiering:
      - SIMPLE: General questions about storage, freshness, science (never injects user pantry records)
      - MEDIUM: Specific food pantry queries (checks if item is saved or reports absent)
      - STRONG: Whole pantry inventory, Eat First priority, expiration overview
    """
    q = normalize(query)
    ownership = has_pantry_ownership(q)
    target_food = extract_food_noun(q)

    # Follow-up
    if is_short_follow_up or is_follow_up_query(q):
        return FreshoIntent.FOLLOW_UP, ContextLevel.MEDIUM, target_food

    # Analysis context (from current scan)
    if has_analysis_context and any(p in q for p in ("this food", "tell me about this", "this item", "store this")):
        return FreshoIntent.ANALYSIS_CONTEXT, ContextLevel.MEDIUM, target_food

    # Eat First / Urgent
    if any(
        p in q
        for p in (
            "eat first",
            "use first",
            "consume first",
            "what should i eat first",
            "which food should i eat first",
            "which food should i consume first",
            "which item should i eat first",
            "before it goes bad",
            "most urgent",
            "priority to eat",
        )
    ):
        return FreshoIntent.PANTRY_PRIORITY, ContextLevel.STRONG, None

    # Expiring soon / Quality limit
    if any(
        p in q
        for p in (
            "approaching their quality limit",
            "approaching its quality limit",
            "closest to its quality limit",
            "closest to quality limit",
            "shortest remaining quality",
            "expiring soon",
            "expire soon",
            "going bad soon",
            "spoil soon",
            "needs attention",
            "high priority",
            "low priority",
        )
    ):
        return FreshoIntent.EXPIRING_SOON, ContextLevel.STRONG, None

    # Cook today / recipes from pantry
    if any(p in q for p in ("cook today", "cook tonight", "what should i cook", "what can i cook", "what to make today")):
        return FreshoIntent.COOK_TODAY, ContextLevel.STRONG, None

    if any(p in q for p in ("storage advice for my pantry", "store differently", "organize my pantry")):
        return FreshoIntent.PANTRY_LIST, ContextLevel.STRONG, None

    # Specific food with ownership (MEDIUM context)
    if ownership and target_food:
        if any(p in q for p in ("store", "storage", "keep", "fridge", "refrigerate", "countertop")):
            return FreshoIntent.PANTRY_ITEM_STORAGE, ContextLevel.MEDIUM, target_food
        return FreshoIntent.PANTRY_ITEM_LOOKUP, ContextLevel.MEDIUM, target_food

    # Whole pantry list
    if (
        any(
            p in q
            for p in (
                "what foods are in my pantry",
                "what food is in my pantry",
                "what is in my pantry",
                "what s in my pantry",
                "whats in my pantry",
                "what foods do i have",
                "what food do i have",
                "foods do i have",
                "items in my pantry",
                "show me my pantry",
                "my pantry situation",
                "pantry situation",
                "list my food",
                "my logged food",
                "my saved food",
                "which food is freshest",
                "least fresh",
                "what foods do i have",
                "what foods do i currently have",
                "what do i have",
                "what do i currently have",
            )
        )
        or (ownership and any(p in q for p in ("pantry", "saved food", "logged food", "foods", "items")))
    ):
        return FreshoIntent.PANTRY_LIST, ContextLevel.STRONG, None

    # Storage advice
    store_match = re.search(r"how\s+(?:should|to|do)(?:\s+i)?\s+store\s+(?:the\s+|this\s+|fresh\s+|ripe\s+)?([a-z\s]+)", q)
    if store_match and store_match.group(1):
        cleaned = store_match.group(1).replace("?", "")
        cleaned = re.sub(r"\b(?:properly|correctly|well|today|fresh|ripe|whole)\b", "", cleaned).strip()
        matched_target = target_food or extract_food_noun(cleaned) or cleaned or None
        return FreshoIntent.STORAGE_ADVICE, ContextLevel.MEDIUM if matched_target else ContextLevel.SIMPLE, matched_target

    # General Freshness Explanation (e.g. why bananas get brown spots) -> SIMPLE context!
    if any(p in q for p in ("slightly spoiled", "what is slightly spoiled", "what does slightly spoiled mean")):
        return FreshoIntent.FRESHNESS_EXPLANATION, ContextLevel.SIMPLE, target_food

    if any(p in q for p in ("brown spot", "turn brown", "why do bananas", "why bananas")):
        return FreshoIntent.FRESHNESS_EXPLANATION, ContextLevel.SIMPLE, target_food or "banana"

    # Food waste reduction
    if "waste" in q and ("reduce" in q or "food" in q):
        if "pantry" in q and ownership:
            return FreshoIntent.FOOD_WASTE, ContextLevel.STRONG, None
        return FreshoIntent.FOOD_WASTE, ContextLevel.SIMPLE, target_food

    # Default general question -> SIMPLE context
    return FreshoIntent.GENERAL_FOOD_QUESTION, ContextLevel.SIMPLE, target_food


def map_fresho_intent_to_pantry_intent(fresho_intent: FreshoIntent) -> str:
    """Map unified FreshoIntent to deterministic pantry triage intent strings."""
    from backend.app.services.pantry_triage_service import PantryIntent

    mapping = {
        FreshoIntent.PANTRY_PRIORITY: PantryIntent.EAT_FIRST,
        FreshoIntent.PANTRY_LIST: PantryIntent.PANTRY_INVENTORY,
        FreshoIntent.EXPIRING_SOON: PantryIntent.EXPIRING_SOON,
        FreshoIntent.COOK_TODAY: PantryIntent.COOK_TODAY,
        FreshoIntent.PANTRY_ITEM_LOOKUP: PantryIntent.PANTRY_ITEM_LOOKUP,
        FreshoIntent.PANTRY_ITEM_STORAGE: PantryIntent.SPECIFIC_FOOD_STORAGE,
        FreshoIntent.STORAGE_ADVICE: PantryIntent.SPECIFIC_FOOD_STORAGE,
        FreshoIntent.FOOD_WASTE: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.FRESHNESS_EXPLANATION: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.GENERAL_FOOD_QUESTION: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.ANALYSIS_CONTEXT: PantryIntent.GENERAL_EDUCATIONAL,
        FreshoIntent.FOLLOW_UP: PantryIntent.GENERAL_EDUCATIONAL,
    }
    return mapping.get(fresho_intent, PantryIntent.GENERAL_EDUCATIONAL)
