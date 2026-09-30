"""
Infer food form (fresh / dried / powdered / etc.) from recognition label and context.
Does not force a form when evidence is insufficient.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

VALID_FORMS = frozenset({"fresh", "dried", "powdered", "cooked", "processed", "unknown"})


def normalize_food_form(value: Optional[str]) -> str:
    if not value:
        return "unknown"
    v = str(value).lower().strip()
    if v in VALID_FORMS:
        return v
    return "unknown"


def infer_food_form(
    food_name: Optional[str],
    *,
    freshness_label: Optional[str] = None,
    analysis_context: Optional[Dict[str, Any]] = None,
) -> str:
    if analysis_context and analysis_context.get("foodForm"):
        return normalize_food_form(analysis_context.get("foodForm"))

    name = (food_name or "").lower()
    text_blob = name
    if freshness_label:
        text_blob += " " + str(freshness_label).lower()

    if any(k in name for k in ("dried", "dehydrated", "sun-dried", "sun dried")):
        return "dried"
    if any(k in name for k in ("powder", "ground spice", "chilli powder", "chili powder")):
        return "powdered"
    if any(k in name for k in ("cooked", "roasted", "fried", "grilled")):
        return "cooked"
    if any(k in name for k in ("canned", "pickled", "preserved", "jarred")):
        return "processed"

    # Fresh produce cues — only when not explicitly dried/powder
    if re.search(r"\b(fresh|raw|green)\b", text_blob) and "dried" not in name:
        return "fresh"

    if "chilli" in name or "chili" in name or "pepper" in name:
        if "dried" in name or "red chilli" in name and "green" not in name:
            return "dried"
        if "green" in name:
            return "fresh"
        return "unknown"

    return "fresh" if name else "unknown"
