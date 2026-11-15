"""
FoodFresh AI — Food-Waste Impact Analytics Service
Pure Python service calculating user-specific waste reduction, consumption metrics,
monthly trends, and personalized insights strictly from actual recorded user activity.
Ensures zero dummy data and strict account isolation.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.database import chat_db
from backend.app.services.pantry_state_service import get_current_pantry_state

logger = logging.getLogger("foodfresh.analytics")

MONTH_NAMES = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def _format_month_label(ym: str) -> str:
    parts = ym.split("-")
    if len(parts) == 2:
        year, month = parts
        return f"{MONTH_NAMES.get(month, month)} {year}"
    return ym


def record_user_food_action(
    user_id: str,
    food_name: str,
    action: str,
    *,
    pantry_item_id: Optional[str] = None,
    cultivar: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Record an actual user action (consumed or wasted) for a pantry food item.
    Also removes/archives the item from active pantry storage if pantry_item_id is provided.
    """
    clean_action = "consumed" if action.lower() == "consumed" else "wasted"
    remaining_days = None

    # Inspect current pantry item state to determine remaining days at action time
    if pantry_item_id:
        active_items = get_current_pantry_state(user_id)
        matched = next((i for i in active_items if i.get("id") == pantry_item_id), None)
        if matched:
            remaining_days = matched.get("remainingDays")
            if not food_name:
                food_name = matched.get("foodName") or "Produce"
            if not cultivar:
                cultivar = matched.get("cultivar")

    # Food saved calculation:
    # An item is 'saved' if it was consumed before or on the day of expiry (remainingDays >= 0 or None)
    was_saved = 1 if (clean_action == "consumed" and (remaining_days is None or remaining_days >= 0)) else 0

    log = chat_db.record_food_impact(
        user_id=user_id,
        food_name=food_name or "Produce",
        action=clean_action,
        remaining_days=remaining_days,
        was_saved=was_saved,
        pantry_item_id=pantry_item_id,
        cultivar=cultivar,
        reason=reason,
    )

    # Remove consumed/discarded item from active pantry inventory and preserve in archived history logs
    if pantry_item_id:
        try:
            chat_db.delete_pantry_item(pantry_item_id, user_id, action=clean_action, reason=reason)
        except Exception as e:
            logger.warning(f"Could not archive pantry item {pantry_item_id} after logging impact: {e}")

    return log


def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """
    Calculate dynamic food-waste impact statistics strictly from the user's recorded logs.
    Zero dummy data: if no activity exists, returns has_activity=False.
    """
    active_items = []
    archived_items = []
    if user_id:
        try:
            active_items = get_current_pantry_state(user_id)
            archived_items = chat_db.get_archived_pantry_items(user_id)
        except Exception as e:
            logger.warning(f"Could not fetch pantry counts for analytics: {e}")

    total_active = len(active_items)
    total_archived = len(archived_items)
    total_tracked_all_time = total_active + total_archived

    if not user_id:
        return _empty_analytics_response(total_active, total_archived, total_tracked_all_time, active_items)

    logs = chat_db.list_food_impact_logs(user_id, limit=500)

    if not logs:
        return _empty_analytics_response(total_active, total_archived, total_tracked_all_time, active_items)

    total_consumed = sum(1 for log in logs if log["action"] == "consumed")
    total_wasted = sum(1 for log in logs if log["action"] == "wasted")
    total_actions = total_consumed + total_wasted

    if total_actions == 0:
        return _empty_analytics_response(total_active, total_archived, total_tracked_all_time, active_items)

    waste_percentage = round((total_wasted / total_actions) * 100, 1)
    food_saved_count = sum(1 for log in logs if log["action"] == "consumed" and log["wasSaved"])
    food_saved_percentage = round((food_saved_count / total_actions) * 100, 1)

    # Rescued via Eat First: items consumed when remainingDays <= 2
    eat_first_rescued = sum(
        1 for log in logs
        if log["action"] == "consumed" and log.get("remainingDays") is not None and log["remainingDays"] <= 2
    )

    # Environmental impact calculations
    # Average produce item weighs ~0.35 kg.
    # Saving 1 kg food avoids ~2.5 kg CO2e greenhouse gas emissions.
    # Embedded agricultural water footprint is ~95 liters per fresh fruit/vegetable.
    waste_prevented_kg = round(food_saved_count * 0.35, 2)
    co2_saved_kg = round(waste_prevented_kg * 2.5, 2)
    water_saved_liters = round(food_saved_count * 95.0, 1)

    # Freshness distribution of active inventory
    fresh_count = 0
    semi_count = 0
    attention_count = 0
    for it in active_items:
        st = str(it.get("status", "")).lower()
        if "fresh" in st and "semi" not in st:
            fresh_count += 1
        elif "semi" in st or "ripe" in st or "soft" in st:
            semi_count += 1
        elif any(k in st for k in ("spoil", "rot", "decay", "bad")):
            attention_count += 1
        else:
            fresh_count += 1

    freshness_distribution = {
        "fresh": fresh_count,
        "semi_fresh": semi_count,
        "needs_attention": attention_count,
        "total_active": total_active,
    }

    # --- Weekly & Monthly Trends Aggregation ---
    monthly_data: Dict[str, Dict[str, int]] = defaultdict(lambda: {"consumed": 0, "wasted": 0, "saved": 0})
    weekly_data: Dict[str, Dict[str, int]] = defaultdict(lambda: {"consumed": 0, "wasted": 0, "saved": 0})

    consumed_counter: Counter[str] = Counter()
    wasted_counter: Counter[str] = Counter()

    for log in logs:
        created = log.get("createdAt") or ""
        month_key = created[:7] if len(created) >= 7 else "Recent"
        # ISO week key e.g. '2026-W45'
        week_key = "Recent"
        if len(created) >= 10:
            try:
                dt = datetime.fromisoformat(created[:10])
                week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            except Exception:
                week_key = created[:7]

        action = log["action"]
        monthly_data[month_key][action] += 1
        weekly_data[week_key][action] += 1
        if log.get("wasSaved"):
            monthly_data[month_key]["saved"] += 1
            weekly_data[week_key]["saved"] += 1

        fname = log.get("foodName") or "Produce"
        if action == "consumed":
            consumed_counter[fname] += 1
        else:
            wasted_counter[fname] += 1

    sorted_months = sorted(monthly_data.keys())
    monthly_trends = [
        {
            "month": ym,
            "label": _format_month_label(ym),
            "consumed": monthly_data[ym]["consumed"],
            "wasted": monthly_data[ym]["wasted"],
            "saved": monthly_data[ym]["saved"],
            "total": monthly_data[ym]["consumed"] + monthly_data[ym]["wasted"],
        }
        for ym in sorted_months
    ]

    sorted_weeks = sorted(weekly_data.keys())[-6:]
    weekly_trends = [
        {
            "week": wk,
            "label": wk,
            "consumed": weekly_data[wk]["consumed"],
            "wasted": weekly_data[wk]["wasted"],
            "saved": weekly_data[wk]["saved"],
            "total": weekly_data[wk]["consumed"] + weekly_data[wk]["wasted"],
        }
        for wk in sorted_weeks
    ]

    top_consumed = [{"foodName": name, "count": count} for name, count in consumed_counter.most_common(5)]
    top_wasted = [{"foodName": name, "count": count} for name, count in wasted_counter.most_common(5)]

    # --- Generate Personalized Waste Insights ---
    insights = _generate_personalized_insights(
        total_consumed=total_consumed,
        total_wasted=total_wasted,
        waste_percentage=waste_percentage,
        food_saved_count=food_saved_count,
        food_saved_percentage=food_saved_percentage,
        top_wasted=top_wasted,
        top_consumed=top_consumed,
    )

    return {
        "has_activity": True,
        "total_consumed": total_consumed,
        "total_wasted": total_wasted,
        "total_actions": total_actions,
        "waste_percentage": waste_percentage,
        "food_saved_count": food_saved_count,
        "food_saved_percentage": food_saved_percentage,
        "waste_prevented_kg": waste_prevented_kg,
        "co2_saved_kg": co2_saved_kg,
        "water_saved_liters": water_saved_liters,
        "eat_first_rescued": eat_first_rescued,
        "freshness_distribution": freshness_distribution,
        "monthly_trends": monthly_trends,
        "weekly_trends": weekly_trends,
        "top_consumed_foods": top_consumed,
        "top_wasted_foods": top_wasted,
        "recent_actions": logs[:20],
        "personalized_insights": insights,
        "total_active_inventory": total_active,
        "total_archived": total_archived,
        "total_tracked_all_time": total_tracked_all_time,
    }


def _empty_analytics_response(
    total_active: int = 0,
    total_archived: int = 0,
    total_tracked_all_time: int = 0,
    active_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    active_items = active_items or []
    fresh_count = sum(1 for i in active_items if "fresh" in str(i.get("status", "")).lower() and "semi" not in str(i.get("status", "")).lower())
    semi_count = sum(1 for i in active_items if any(k in str(i.get("status", "")).lower() for k in ("semi", "ripe", "soft")))
    attention_count = sum(1 for i in active_items if any(k in str(i.get("status", "")).lower() for k in ("spoil", "rot", "bad")))

    return {
        "has_activity": False,
        "total_consumed": 0,
        "total_wasted": 0,
        "total_actions": 0,
        "waste_percentage": 0.0,
        "food_saved_count": 0,
        "food_saved_percentage": 0.0,
        "waste_prevented_kg": 0.0,
        "co2_saved_kg": 0.0,
        "water_saved_liters": 0.0,
        "eat_first_rescued": 0,
        "freshness_distribution": {
            "fresh": fresh_count,
            "semi_fresh": semi_count,
            "needs_attention": attention_count,
            "total_active": total_active,
        },
        "monthly_trends": [],
        "weekly_trends": [],
        "top_consumed_foods": [],
        "top_wasted_foods": [],
        "recent_actions": [],
        "personalized_insights": [],
        "total_active_inventory": total_active,
        "total_archived": total_archived,
        "total_tracked_all_time": total_tracked_all_time,
    }


def _generate_personalized_insights(
    total_consumed: int,
    total_wasted: int,
    waste_percentage: float,
    food_saved_count: int,
    food_saved_percentage: float,
    top_wasted: List[Dict[str, Any]],
    top_consumed: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Generate dynamic, actionable insights from real user metrics."""
    insights: List[Dict[str, str]] = []

    # 1. Overall Stewardship / Save Rate
    if food_saved_percentage >= 75.0:
        insights.append({
            "type": "positive",
            "icon": "eco",
            "title": "Outstanding Kitchen Stewardship",
            "text": f"You have saved {food_saved_count} items ({food_saved_percentage}% of your tracked food) by consuming them before expiration.",
        })
    elif food_saved_percentage >= 50.0:
        insights.append({
            "type": "positive",
            "icon": "thumb_up",
            "title": "Good Waste Reduction Progress",
            "text": f"Over half of your pantry food ({food_saved_count} items) was enjoyed before spoiling.",
        })

    # 2. Waste Rate Evaluation
    if waste_percentage == 0.0 and total_consumed > 0:
        insights.append({
            "type": "positive",
            "icon": "star",
            "title": "Zero Waste Kitchen!",
            "text": "100% of your recorded pantry items have been consumed with zero recorded waste. Keep it up!",
        })
    elif waste_percentage <= 15.0:
        insights.append({
            "type": "positive",
            "icon": "verified",
            "title": "Low Waste Rate",
            "text": f"Your waste rate of {waste_percentage}% is significantly lower than average household waste (~30%).",
        })
    elif waste_percentage > 30.0:
        insights.append({
            "type": "warning",
            "icon": "warning",
            "title": "High Waste Potential",
            "text": f"{waste_percentage}% of your tracked items were discarded. Check the 'Use Soon' recipe tab to turn ripe produce into quick meals.",
        })

    # 3. Frequent Wasted Items Warning
    if top_wasted:
        most_wasted = top_wasted[0]
        insights.append({
            "type": "info",
            "icon": "lightbulb",
            "title": f"Produce Attention: {most_wasted['foodName']}",
            "text": f"{most_wasted['foodName']} is your most frequently discarded item ({most_wasted['count']} wasted). Consider buying smaller batches or freezing early.",
        })

    # 4. Favorite Saved Produce
    if top_consumed:
        favorite = top_consumed[0]
        insights.append({
            "type": "info",
            "icon": "restaurant",
            "title": f"Kitchen Champion: {favorite['foodName']}",
            "text": f"You've successfully used {favorite['foodName']} {favorite['count']} times before it spoiled.",
        })

    return insights

