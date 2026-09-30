"""
FoodFresh AI - Hybrid Vision Utilities
Label normalization, synonym mapping, semantic agreement checking, and candidate ranking.
"""

from typing import List, Optional, Set, Tuple
from ml.hybrid_vision.schemas import PredictionCandidate

# Canonical food aliases for fuzzy cross-model reconciliation
FOOD_SYNONYMS = {
    "bell pepper": {"bell pepper", "pepper", "capsicum", "sweet pepper"},
    "pepper": {"bell pepper", "pepper", "chili pepper", "chili"},
    "chili pepper": {"chili pepper", "pepper", "chili", "chilli", "green chilli", "hot pepper"},
    "eggplant": {"eggplant", "aubergine", "brinjal"},
    "corn": {"corn", "sweetcorn", "maize"},
    "green beans": {"green beans", "french beans", "string beans", "beans"},
    "bitter gourd": {"bitter gourd", "bittermelon", "bitter melon", "karela"},
    "bottle gourd": {"bottle gourd", "calabash", "lauki"},
    "yogurt": {"yogurt", "yoghurt", "soy yogurt", "soyghurt", "vanilla yogurt", "vanilla yoghurt"},
    "bread": {"bread", "toast", "loaf", "bun", "buns", "roti"},
    "cake": {"cake", "cakes", "muffin", "muffins"},
    "potato": {"potato", "potatoes"},
    "tomato": {"tomato", "tomatoes"},
    "sweet potato": {"sweet potato", "sweet potatoes"},
    "avocado": {"avocado", "avocados"},
    "grape": {"grape", "grapes"},
    "beetroot": {"beetroot", "beet", "beets"},
    "mango": {"mango", "mangoes"},
    "papaya": {"papaya", "papayas", "pawpaw"},
    "watermelon": {"watermelon", "water melon"},
    "apple": {"apple", "apples"},
    "banana": {"banana", "bananas"},
    "orange": {"orange", "oranges"},
    "lemon": {"lemon", "lemons"},
    "onion": {"onion", "onions"},
    "carrot": {"carrot", "carrots"},
    "cucumber": {"cucumber", "cucumbers"},
    "pomegranate": {"pomegranate", "pomegranates"},
    # Chickoo / Sapodilla synonyms (common South Asian tropical fruit)
    "chickoo": {"chickoo", "chiku", "sapota", "sapodilla", "chikoo"},
    "chiku": {"chickoo", "chiku", "sapota", "sapodilla", "chikoo"},
    "sapodilla": {"chickoo", "chiku", "sapota", "sapodilla", "chikoo"},
    "jackfruit": {"jackfruit", "jack fruit"},
    "custard apple": {"custard apple", "sitaphal", "sugar apple", "sweetsop"},
}


def normalize_food_name(name: str) -> str:
    """Normalize a food label for display and comparison."""
    clean = name.strip().lower().replace("_", " ").replace("-", " ")
    # Singularize common plurals
    if clean.endswith("ies") and len(clean) > 4:
        clean = clean[:-3] + "y"
    elif clean.endswith("es") and len(clean) > 3 and clean not in {"cheese"}:
        clean = clean[:-2]
    elif clean.endswith("s") and len(clean) > 2 and clean not in {"asparagus", "peas", "hummus", "couscous", "cheese", "citrus"}:
        clean = clean[:-1]
    return clean.strip()


def display_name(name: str) -> str:
    """Format normalized name to title case for display."""
    return normalize_food_name(name).title()


def labels_match(label_a: str, label_b: str) -> bool:
    """
    Check if two food labels semantically refer to the same food item.
    Accounts for singular/plural, capitalization, and known synonym groups.
    """
    norm_a = normalize_food_name(label_a)
    norm_b = normalize_food_name(label_b)

    if norm_a == norm_b:
        return True

    # Check synonym groups
    for canonical, syns in FOOD_SYNONYMS.items():
        norm_syns = {normalize_food_name(s) for s in syns}
        if norm_a in norm_syns and norm_b in norm_syns:
            return True

    # Substring containment for compound names (e.g. "pomegranate" and "pomegranate", "apple" in "green apple")
    words_a = set(norm_a.split())
    words_b = set(norm_b.split())
    if words_a and words_b and (words_a.issubset(words_b) or words_b.issubset(words_a)):
        return True

    return False


def find_agreement_candidate(
    candidates_a: List[PredictionCandidate],
    candidates_b: List[PredictionCandidate]
) -> Optional[Tuple[PredictionCandidate, PredictionCandidate]]:
    """
    Find matching candidates across two model prediction lists.
    Returns the first matching pair (ordered by rank).
    """
    for a in candidates_a:
        for b in candidates_b:
            if labels_match(a.label, b.label):
                return a, b
    return None
