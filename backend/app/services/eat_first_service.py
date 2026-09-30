"""
FoodFresh AI - Eat First Priority Service
Deterministic ranking and prioritization engine based on remaining shelf-life quality window,
visible freshness state, storage conditions, and storage duration.
"""

from enum import Enum
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("foodfresh.eat_first")


def _normalize_freshness_label(label: Optional[str]) -> str:
    """
    Extract the core freshness class from a potentially decorated label.
    Handles suffixes like '(Moderate Confidence)', 'Freshness Uncertain (...)', etc.
    Returns canonical lowercase string: 'rotten', 'slightly_spoiled', 'fresh', or 'uncertain'.
    """
    if not label:
        return "fresh"
    raw = str(label).lower().strip()
    # Strip parenthetical qualifiers e.g. '(moderate confidence)', '(limited model coverage for beetroot)'
    raw = re.sub(r"\s*\([^)]*\)", "", raw).strip()
    if "rotten" in raw:
        return "rotten"
    if "slightly" in raw or "spoiled" in raw:
        return "slightly_spoiled"
    if "stale" in raw or "mold" in raw:
        return "slightly_spoiled"
    if "uncertain" in raw or "unavailable" in raw:
        return "uncertain"
    if "fresh" in raw:
        return "fresh"
    return raw


class PriorityTier(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNAVAILABLE = "UNAVAILABLE"


# Priority numeric weights for sorting (higher = more urgent to consume)
PRIORITY_SCORES = {
    PriorityTier.VERY_HIGH: 4,
    PriorityTier.HIGH: 3,
    PriorityTier.MEDIUM: 2,
    PriorityTier.LOW: 1,
    PriorityTier.UNAVAILABLE: 0,
}


class EatFirstService:
    """
    Deterministic rule engine that calculates consumption urgency.
    NOT a black-box ML model; provides transparent, explainable rationales.
    """

    _instance: Optional["EatFirstService"] = None

    @classmethod
    def get_instance(cls) -> "EatFirstService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def calculate_priority(
        self,
        shelf_life_result: Optional[Dict[str, Any]] = None,
        freshness_label: Optional[str] = None,
        days_stored: int = 0,
        storage_type: str = "countertop",
        **kwargs
    ) -> Dict[str, Any]:
        data = shelf_life_result or kwargs.get("shelf_life_data")
        res = self.evaluate_priority(shelf_life_data=data, freshness_label=freshness_label)
        if "urgencyLabel" not in res and "urgency" in res:
            res["urgencyLabel"] = res["urgency"]
        return res

    def evaluate_priority(
        self,
        shelf_life_data: Optional[Dict[str, Any]],
        freshness_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate consumption priority for a single food item.
        Requires available shelf-life data. If unavailable, returns unavailable status.
        """
        if not shelf_life_data or shelf_life_data.get("status") != "available":
            return {
                "status": "unavailable",
                "priority": None,
                "score": 0,
                "tier": "UNAVAILABLE",
                "reason": "Eat First requires an available shelf-life estimate.",
                "urgency": "Guidance unavailable",
                "urgencyLabel": "Guidance unavailable"
            }

        remaining = shelf_life_data.get("remaining") or {}
        rem_min = remaining.get("minDays")
        rem_max = remaining.get("maxDays")

        if rem_min is None and rem_max is None:
            return {
                "status": "unavailable",
                "priority": None,
                "score": 0,
                "tier": "UNAVAILABLE",
                "reason": "Shelf-life window bounds are undefined.",
                "urgency": "Guidance unavailable"
            }

        effective_min = rem_min if rem_min is not None else rem_max
        effective_max = rem_max if rem_max is not None else rem_min
        effective_rem = (effective_min + effective_max) / 2.0

        freshness_norm = _normalize_freshness_label(freshness_label)

        # Deterministic Rule Hierarchy
        # 1. VERY_HIGH
        if freshness_norm == "rotten" or effective_max <= 0 or effective_rem <= 1.0 or effective_max <= 1:
            if effective_max <= 0:
                reason = "Very high priority because the estimated remaining quality is 0 days."
                urgency = "Consume immediately or discard"
            elif freshness_norm == "rotten":
                reason = "Very high priority because visible surface degradation indicates the quality window has expired."
                urgency = "Do not consume / dispose"
            else:
                reason = f"Very high priority because the estimated remaining quality window is critically short ({int(effective_min)}–{int(effective_max)} days)."
                urgency = "Consume immediately (within 24 hours)"
            return {
                "status": "available",
                "priority": PriorityTier.VERY_HIGH.value,
                "score": PRIORITY_SCORES[PriorityTier.VERY_HIGH],
                "tier": PriorityTier.VERY_HIGH.value,
                "reason": reason,
                "urgency": urgency,
                "isEstimate": True
            }

        # 2. HIGH
        if freshness_norm in ["slightly_spoiled", "slightly spoiled"] or effective_rem <= 3.0 or effective_max <= 3:
            if freshness_norm in ["slightly_spoiled", "slightly spoiled"]:
                reason = f"High priority because the estimated remaining quality window is short ({int(effective_min)}–{int(effective_max)} days) and visible freshness is declining."
            else:
                reason = f"High priority because the estimated remaining quality window is short ({int(effective_min)}–{int(effective_max)} days)."
            return {
                "status": "available",
                "priority": PriorityTier.HIGH.value,
                "score": PRIORITY_SCORES[PriorityTier.HIGH],
                "tier": PriorityTier.HIGH.value,
                "reason": reason,
                "urgency": "Consume within 1–3 days",
                "isEstimate": True
            }

        # 3. MEDIUM
        if effective_rem <= 7.0 or effective_max <= 7:
            return {
                "status": "available",
                "priority": PriorityTier.MEDIUM.value,
                "score": PRIORITY_SCORES[PriorityTier.MEDIUM],
                "tier": PriorityTier.MEDIUM.value,
                "reason": f"Estimated remaining quality is moderate ({effective_min}–{effective_max} days) under proper storage.",
                "urgency": "Consume within a week",
                "isEstimate": True
            }

        # 4. LOW
        return {
            "status": "available",
            "priority": PriorityTier.LOW.value,
            "score": PRIORITY_SCORES[PriorityTier.LOW],
            "tier": PriorityTier.LOW.value,
            "reason": f"Good visible freshness with ample estimated shelf-life ({effective_min}–{effective_max} days).",
            "urgency": "Ample quality window remaining",
            "isEstimate": True
        }

    def rank_foods_for_consumption(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank a collection of food analysis records for consumption order.
        Sorts items descending by priority score, then ascending by remaining max days.
        """
        evaluated_items = []
        for item in items:
            shelf_life = item.get("shelfLife")
            freshness = item.get("freshness", {})
            f_label = freshness.get("label") if isinstance(freshness, dict) else str(freshness)

            priority_res = self.evaluate_priority(shelf_life, f_label)
            item_copy = dict(item)
            item_copy["eatFirstPriority"] = priority_res

            rem_max = 999.0
            if shelf_life and shelf_life.get("status") == "available":
                rem = shelf_life.get("remaining", {})
                rem_max = float(rem.get("maxDays", 999.0))

            evaluated_items.append((priority_res.get("score", 0), -rem_max, item_copy))

        # Sort: highest priority score first, ties broken by lowest remaining days
        evaluated_items.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return [x[2] for x in evaluated_items]


def get_eat_first_service() -> EatFirstService:
    return EatFirstService.get_instance()
