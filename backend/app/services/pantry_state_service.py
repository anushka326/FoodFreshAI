"""
FoodFresh AI — Central pantry state and remaining-quality calculation (UTC).

Single source of truth for:
- dynamic remaining days from added_at + estimated_quality_days
- derived priority / eat-first tiers
- enriched pantry records for History, Dashboard, and FreshoBuddy
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from backend.app.services.eat_first_service import get_eat_first_service

REMAINING_UNKNOWN_LABEL = "Remaining quality cannot currently be estimated."


def parse_utc_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_estimated_end_at(added_at: datetime, estimated_quality_days: int) -> datetime:
    """
    End of quality window at 23:59:59 UTC on added_date + estimated_quality_days.
    Example: added 2026-09-30 + 5 days → end 2026-10-05.
    """
    added_date = added_at.astimezone(timezone.utc).date()
    if estimated_quality_days <= 0:
        end_date = added_date
    else:
        end_date = added_date + timedelta(days=int(estimated_quality_days))
    return datetime(
        end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc
    )


def compute_remaining_days_from_end_at(
    estimated_end_at_iso: Optional[str],
    *,
    now: Optional[datetime] = None,
) -> Optional[int]:
    """Whole calendar days from today (UTC) through estimated_end_at date; clamped >= 0."""
    end = parse_utc_iso(estimated_end_at_iso)
    if end is None:
        return None
    today = (now or utc_now()).astimezone(timezone.utc).date()
    end_date = end.astimezone(timezone.utc).date()
    return max(0, (end_date - today).days)


def compute_remaining_days(
    added_at_iso: Optional[str],
    estimated_quality_days: Optional[int],
    *,
    estimated_end_at_iso: Optional[str] = None,
    now: Optional[datetime] = None,
) -> Optional[int]:
    """Prefer estimated_end_at; fallback to added_at + quality days."""
    if estimated_end_at_iso:
        rem = compute_remaining_days_from_end_at(estimated_end_at_iso, now=now)
        if rem is not None:
            return rem
    if estimated_quality_days is None:
        return None
    added = parse_utc_iso(added_at_iso)
    if added is None:
        return None
    end_at = compute_estimated_end_at(added, int(estimated_quality_days))
    return compute_remaining_days_from_end_at(end_at.isoformat(), now=now)


def quality_period_label(remaining: Optional[int]) -> str:
    if remaining is None:
        return REMAINING_UNKNOWN_LABEL
    if remaining == 0:
        return "0 days remaining"
    if remaining == 1:
        return "1 day remaining"
    return f"{remaining} days remaining"


def derive_display_status(remaining: Optional[int], freshness_state: Optional[str]) -> str:
    fresh = (freshness_state or "Fresh").strip()
    if remaining is None:
        return fresh
    if remaining <= 0:
        return "ATTENTION / EXPIRED QUALITY WINDOW"
    if remaining <= 3:
        return "HIGH PRIORITY"
    if remaining <= 7:
        return "MEDIUM PRIORITY"
    return "LOW PRIORITY"


def shelf_life_dict_from_remaining(
    food_name: str,
    remaining_days: Optional[int],
    storage_type: str = "countertop",
) -> Dict[str, Any]:
    if remaining_days is None:
        return {"status": "unavailable", "reason": REMAINING_UNKNOWN_LABEL}
    return {
        "status": "available",
        "food": food_name,
        "storageType": storage_type,
        "remaining": {"minDays": remaining_days, "maxDays": remaining_days},
    }


def compute_eat_first_fields(
    food_name: str,
    remaining_days: Optional[int],
    freshness_state: Optional[str],
    storage_type: str = "countertop",
) -> Dict[str, Any]:
    eat = get_eat_first_service()
    sl = shelf_life_dict_from_remaining(food_name, remaining_days, storage_type)
    label = freshness_state or "fresh"
    if isinstance(label, str):
        low = label.lower()
        if "slightly" in low:
            label = "slightly_spoiled"
        elif "rotten" in low:
            label = "rotten"
        elif "uncertain" in low:
            label = "fresh"
        else:
            label = "fresh"
    result = eat.evaluate_priority(sl, freshness_label=label)
    return {
        "eatFirstPriority": result.get("priority") or "UNAVAILABLE",
        "eatFirstScore": result.get("score") or 0,
        "eatFirstReason": result.get("reason") or "",
        "eatFirstUrgency": result.get("urgency") or result.get("urgencyLabel") or "",
        "priorityTier": result.get("tier") or result.get("priority"),
    }


def enrich_pantry_row(row: Dict[str, Any], *, now: Optional[datetime] = None) -> Dict[str, Any]:
    """Apply dynamic remaining days and derived priority to a raw DB row dict."""
    added_at = row.get("addedAt") or row.get("analyzedAt") or row.get("created_at")
    est_days = row.get("estimatedQualityDays")
    if est_days is None and row.get("estimated_quality_days") is not None:
        est_days = row.get("estimated_quality_days")

    end_at_iso = row.get("estimatedEndAt") or row.get("estimated_end_at")
    remaining = compute_remaining_days(
        added_at,
        int(est_days) if est_days is not None else None,
        estimated_end_at_iso=end_at_iso,
        now=now,
    )

    food_name = row.get("foodName") or row.get("food_name") or "Produce"
    storage_type = row.get("storageType") or row.get("storage_type") or "countertop"
    freshness_state = row.get("freshnessState") or row.get("freshness_state") or row.get("status")

    eat_fields = compute_eat_first_fields(food_name, remaining, freshness_state, storage_type)

    out = dict(row)
    out["remainingDays"] = remaining
    out["qualityPeriod"] = quality_period_label(remaining)
    out["remainingQualityKnown"] = remaining is not None
    out["pantryStatus"] = derive_display_status(remaining, freshness_state)
    out["estimatedEndAt"] = row.get("estimatedEndAt") or row.get("estimated_end_at")
    out.update(eat_fields)
    return out


def get_current_pantry_state(user_id: str, *, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    from backend.app.database import chat_db

    raw_items = chat_db.get_pantry_items_raw(user_id)
    enriched = [enrich_pantry_row(item, now=now) for item in raw_items]
    enriched.sort(
        key=lambda x: (
            x.get("remainingDays") is None,
            x.get("remainingDays") if x.get("remainingDays") is not None else 9999,
            x.get("foodName") or "",
        )
    )
    return enriched


def extract_initial_quality_days_from_save_payload(item: Dict[str, Any]) -> Optional[int]:
    """Use existing analysis shelf-life output; do not invent values."""
    if item.get("estimatedQualityDays") is not None:
        try:
            return max(0, int(item["estimatedQualityDays"]))
        except (TypeError, ValueError):
            pass
    if item.get("remainingDays") is not None:
        try:
            return max(0, int(item["remainingDays"]))
        except (TypeError, ValueError):
            pass
    sl = item.get("shelfLife")
    if isinstance(sl, dict):
        rem = sl.get("remaining") or {}
        for key in ("maxDays", "minDays"):
            if rem.get(key) is not None:
                try:
                    return max(0, int(rem[key]))
                except (TypeError, ValueError):
                    continue
        if sl.get("status") == "unavailable":
            return None
    return None
