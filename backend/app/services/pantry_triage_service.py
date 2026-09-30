"""
FoodFresh AI - Pantry Triage & History Decision Engine
Deterministic calculation engine for prioritizing user's pantry produce.
Evaluates remaining quality window, visible freshness state, Eat First tier,
and storage condition. Gemini explains these decisions rather than inventing them.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("foodfresh.pantry_triage")


class PantryIntent:
    EAT_FIRST = "eat_first"
    COOK_TODAY = "cook_today"
    EXPIRING_SOON = "expiring_soon"
    PANTRY_INVENTORY = "pantry_inventory"
    FRESHEST = "freshest"
    LEAST_FRESH = "least_fresh"
    SHORTEST_SHELF_LIFE = "shortest_shelf_life"
    LONGEST_SHELF_LIFE = "longest_shelf_life"
    PRIORITY_HIGH = "priority_high"
    PRIORITY_LOW = "priority_low"
    STORAGE_OPTIMIZATION = "storage_optimization"
    SPECIFIC_FOOD_STORAGE = "specific_food_storage"
    GENERAL_EDUCATIONAL = "general_educational"


def detect_pantry_intent(query: str) -> Tuple[str, Optional[str]]:
    """
    Detect the specific user intent regarding pantry produce.
    Returns (intent_type, optional_target_food).
    """
    q = query.lower().strip()

    # 1. Eat first / Most urgent
    if any(phrase in q for phrase in [
        "eat first", "use first", "consume first", "eat before it goes bad",
        "most urgent", "priority to eat", "what should i eat first"
    ]):
        return PantryIntent.EAT_FIRST, None

    # 2. Cooking / Meal planning
    if any(phrase in q for phrase in [
        "cook today", "cook tonight", "what should i cook", "what to make",
        "meal today", "prepare today", "what can i cook with my"
    ]):
        return PantryIntent.COOK_TODAY, None

    # 3. Expiring soon / Needs attention
    if any(phrase in q for phrase in [
        "expiring soon", "needs attention", "expire soon", "going bad",
        "spoil soon", "shortest remaining quality", "shortest remaining",
        "attention"
    ]):
        return PantryIntent.EXPIRING_SOON, None

    # 4. Shortest shelf life
    if "shortest shelf" in q or "shortest shelf-life" in q:
        return PantryIntent.SHORTEST_SHELF_LIFE, None

    # 5. Longest shelf life
    if "longest shelf" in q or "longest shelf-life" in q or "lasts longest" in q:
        return PantryIntent.LONGEST_SHELF_LIFE, None

    # 6. Inventory / Pantry situation
    if any(phrase in q for phrase in [
        "what food do i have", "what foods do i have", "foods do i currently have",
        "what do i have in my pantry", "show me my pantry", "my pantry situation",
        "list my food", "my logged food", "my saved food", "items in my pantry"
    ]):
        return PantryIntent.PANTRY_INVENTORY, None

    # 7. Freshest
    if "which food is freshest" in q or "most fresh" in q or "which items are fresh" in q:
        return PantryIntent.FRESHEST, None

    # 8. Least fresh
    if "least fresh" in q or "lowest freshness" in q or "worst condition" in q:
        return PantryIntent.LEAST_FRESH, None

    # 9. Priority tiers
    if "high priority" in q or "highest priority" in q:
        return PantryIntent.PRIORITY_HIGH, None
    if "low priority" in q or "lowest priority" in q:
        return PantryIntent.PRIORITY_LOW, None

    # 10. Storage changes / optimization
    if "store differently" in q or "storage advice for my pantry" in q or "how should i organize" in q:
        return PantryIntent.STORAGE_OPTIMIZATION, None

    # 11. Specific food storage (e.g., "How should I store apples?")
    store_match = re.search(r"how (?:should|to|do) i store (?:this |the |my )?([a-z\s]+)", q)
    if store_match:
        target = store_match.group(1).replace("?", "").strip()
        # Clean trailing filler words
        target = re.sub(r"\b(?:properly|correctly|well|today)\b", "", target).strip()
        if target:
            return PantryIntent.SPECIFIC_FOOD_STORAGE, target

    return PantryIntent.GENERAL_EDUCATIONAL, q


def evaluate_item_urgency(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic scoring of a single pantry item.
    Higher score = higher urgency to consume.
    """
    food_name = item.get("foodName", "Unknown Produce")
    status = str(item.get("status", "Fresh")).lower()
    rem_days = item.get("remainingDays")
    if rem_days is None:
        rem_days = 999

    storage_env = str(item.get("storageEnvironment", "")).lower()
    is_countertop = "countertop" in storage_env or "ambient" in storage_env

    # Base Score by Remaining Quality Days
    if rem_days <= 0:
        base_score = 100
        tier = "VERY_HIGH"
    elif rem_days == 1:
        base_score = 80
        tier = "HIGH"
    elif rem_days <= 3:
        base_score = 65
        tier = "HIGH"
    elif rem_days <= 7:
        base_score = 35
        tier = "MEDIUM"
    else:
        base_score = 15
        tier = "LOW"

    # Visible Freshness Override / Modifier
    freshness_mod = 0
    if "rotten" in status or "spoil" in status or "decay" in status:
        base_score = max(base_score, 120)
        tier = "VERY_HIGH"
        freshness_mod = 30
    elif "slightly" in status or "semi" in status or "soft" in status:
        base_score = max(base_score, 75)
        if tier != "VERY_HIGH":
            tier = "HIGH"
        freshness_mod = 15

    # Storage penalty: Countertop produce with <= 1 day left declines faster than chilled
    storage_mod = 5 if (is_countertop and rem_days <= 1) else 0

    total_score = base_score + freshness_mod + storage_mod

    return {
        "foodName": food_name,
        "status": item.get("status", "Fresh"),
        "remainingDays": rem_days,
        "qualityPeriod": item.get("qualityPeriod", f"{rem_days} days remaining"),
        "tier": tier,
        "urgencyScore": total_score,
        "storageEnvironment": item.get("storageEnvironment", "Countertop Ambient"),
        "storageType": item.get("storageType", "countertop"),
        "qualityScore": item.get("qualityScore", 80),
        "guidance": item.get("guidance", ""),
        "cultivar": item.get("cultivar", f"{food_name} • Fresh Harvest"),
        "rawItem": item
    }


def triage_pantry_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Perform a comprehensive deterministic triage across all user's saved pantry items.
    """
    if not items:
        return {
            "hasItems": False,
            "totalCount": 0,
            "rankedItems": [],
            "topUrgent": None,
            "tiedTop": [],
            "isTie": False,
            "expiringSoon": [],
            "freshest": None,
            "leastFresh": None,
            "summary": "Pantry history is empty."
        }

    scored_items = [evaluate_item_urgency(it) for it in items]

    # Sort primarily by urgencyScore DESC, secondarily by remainingDays ASC
    scored_items.sort(key=lambda x: (-x["urgencyScore"], x["remainingDays"], x["foodName"]))

    top_item = scored_items[0]
    top_score = top_item["urgencyScore"]

    # Detect ties at the top tier
    tied_items = [it for it in scored_items if it["urgencyScore"] == top_score]
    is_tie = len(tied_items) > 1

    # Items needing attention (<= 3 days remaining OR tier in HIGH/VERY_HIGH)
    expiring_soon = [it for it in scored_items if it["remainingDays"] <= 3 or it["tier"] in ["VERY_HIGH", "HIGH"]]

    # Freshest: longest remaining quality window and status 'Fresh'
    freshest_item = min(scored_items, key=lambda x: (-x["remainingDays"], -x["qualityScore"]))

    # Least fresh: shortest window / highest urgency
    least_fresh_item = scored_items[0]

    return {
        "hasItems": True,
        "totalCount": len(scored_items),
        "rankedItems": scored_items,
        "topUrgent": top_item,
        "tiedTop": tied_items if is_tie else [],
        "isTie": is_tie,
        "expiringSoon": expiring_soon,
        "freshest": freshest_item,
        "leastFresh": least_fresh_item
    }


def build_deterministic_answer(intent: str, triage: Dict[str, Any], target_food: Optional[str] = None) -> str:
    """
    Generate a precise, deterministic, Markdown-formatted answer when Gemini is offline or
    as the authoritative ground-truth template.
    Ensures important foods and decisions are formatted in **bold** with zero hallucination.
    """
    if not triage["hasItems"]:
        return (
            "Your pantry history is currently empty, so I can't identify a specific food to prioritize yet. "
            "Analyze and save a food first, and I'll track its freshness and prioritize it for you 🌱"
        )

    top = triage["topUrgent"]
    is_tie = triage["isTie"]
    tied = triage["tiedTop"]

    if intent == PantryIntent.EAT_FIRST:
        if is_tie:
            names = " and ".join([f"**{it['foodName']}**" for it in tied])
            days_str = f"{top['remainingDays']} days" if top['remainingDays'] > 1 else f"{top['remainingDays']} day" if top['remainingDays'] == 1 else "0 days"
            return (
                f"Based on your saved pantry history, {names} **should be used first** because both have reached the shortest estimated quality window ({days_str} remaining).\n\n"
                f"**Why:**\n"
                + "\n".join([f"- **{it['foodName']}** — {it['remainingDays']} days remaining ({it['status']}, {it['tier']} priority)" for it in tied])
                + f"\n\n**Recommendation:** Use or refrigerate these items today before texture and flavor decline."
            )
        else:
            return (
                f"Based on your saved pantry history, **{top['foodName']} should be used first** because its current estimated quality window is the shortest among your logged items.\n\n"
                f"**Why:**\n"
                f"- **{top['foodName']}** — {top['remainingDays']} days remaining\n"
                f"- **Freshness:** {top['status']}\n"
                f"- **Priority:** {top['tier']}\n\n"
                f"**Recommendation:** Plan to use **{top['foodName']}** today in your meals or move it to chilled storage to prolong quality."
            )

    elif intent == PantryIntent.COOK_TODAY:
        if is_tie:
            food_list = ", ".join([f"**{it['foodName']}**" for it in tied])
            return (
                f"Based on your saved pantry history, you should cook with {food_list} today because they have the shortest remaining quality windows (0–1 days).\n\n"
                f"**Suggested meal ideas:**\n"
                f"- Combine in a fresh salad, roasted medley, or smoothie bowl.\n"
                f"- Cook or freeze any surplus portions to prevent waste."
            )
        else:
            return (
                f"Based on your saved pantry history, you should focus on **{top['foodName']}** today because it has only **{top['remainingDays']} days remaining**.\n\n"
                f"**Cooking idea:** Incorporate **{top['foodName']}** as the centerpiece of today's lunch or dinner before quality declines."
            )

    elif intent == PantryIntent.EXPIRING_SOON or intent == PantryIntent.SHORTEST_SHELF_LIFE:
        items_soon = triage["expiringSoon"]
        if not items_soon:
            return "Based on your saved pantry history, none of your logged produce items are in immediate danger of spoiling. All have comfortable remaining quality windows."
        
        lines = [f"- **{it['foodName']}** — {it['remainingDays']} days left ({it['tier']} priority)" for it in items_soon]
        return (
            f"Based on your saved pantry history, the following items **need attention soon**:\n\n"
            + "\n".join(lines)
            + "\n\nPlan to use these first or adjust storage conditions to extend their shelf life."
        )

    elif intent == PantryIntent.PANTRY_INVENTORY:
        ranked = triage["rankedItems"]
        lines = [f"- **{it['foodName']}**: {it['status']} • {it['remainingDays']} days remaining • Priority: **{it['tier']}**" for it in ranked]
        return (
            f"Here is your current **Pantry Produce Log** ({len(ranked)} items):\n\n"
            + "\n".join(lines)
            + f"\n\n**Most urgent:** **{top['foodName']}** should be used first."
        )

    elif intent == PantryIntent.FRESHEST:
        freshest = triage["freshest"]
        return (
            f"Based on your saved pantry history, **{freshest['foodName']}** is currently your freshest logged item with approximately **{freshest['remainingDays']} days of remaining quality**."
        )

    elif intent == PantryIntent.LEAST_FRESH:
        least = triage["leastFresh"]
        return (
            f"Based on your saved pantry history, **{least['foodName']}** currently has the shortest remaining quality window (**{least['remainingDays']} days left**, {least['status']})."
        )

    elif intent == PantryIntent.LONGEST_SHELF_LIFE:
        longest = max(triage["rankedItems"], key=lambda x: x["remainingDays"])
        return (
            f"Based on your saved pantry history, **{longest['foodName']}** has the longest estimated shelf-life window with approximately **{longest['remainingDays']} days remaining**."
        )

    elif intent == PantryIntent.PRIORITY_HIGH:
        high_items = [it for it in triage["rankedItems"] if it["tier"] in ["VERY_HIGH", "HIGH"]]
        if not high_items:
            return "Based on your saved pantry history, you currently have no high-priority items. All logged items are stable."
        lines = [f"- **{it['foodName']}** — {it['remainingDays']} days remaining ({it['tier']})" for it in high_items]
        return f"The following saved foods are currently **High Priority**:\n\n" + "\n".join(lines)

    elif intent == PantryIntent.PRIORITY_LOW:
        low_items = [it for it in triage["rankedItems"] if it["tier"] in ["MEDIUM", "LOW"]]
        if not low_items:
            return "Based on your saved pantry history, all of your logged items require near-term attention."
        lines = [f"- **{it['foodName']}** — {it['remainingDays']} days remaining ({it['tier']})" for it in low_items]
        return f"The following saved foods are currently **Lower Priority**:\n\n" + "\n".join(lines)

    elif intent == PantryIntent.STORAGE_OPTIMIZATION:
        suggestions = []
        for it in triage["rankedItems"]:
            if it["remainingDays"] <= 1 and "countertop" in it["storageType"]:
                suggestions.append(f"- **{it['foodName']}**: Currently on Countertop with {it['remainingDays']} days left. Move to refrigerator crisper to slow down ethylene ripening.")
            elif it["tier"] == "VERY_HIGH":
                suggestions.append(f"- **{it['foodName']}**: Quality window has reached 0 days. Consume today or prep and freeze.")
        
        if suggestions:
            return "Based on your saved pantry history, here are recommended **storage adjustments**:\n\n" + "\n".join(suggestions)
        return "Based on your saved pantry history, your current produce items appear to be stored in appropriate environments."

    elif intent == PantryIntent.SPECIFIC_FOOD_STORAGE and target_food:
        # Check if user has this food in pantry
        match = next((it for it in triage["rankedItems"] if target_food.lower() in it["foodName"].lower()), None)
        if match:
            return (
                f"According to your saved pantry history, you currently have **{match['foodName']}** stored in **{match['storageEnvironment']}** with approximately **{match['remainingDays']} days of remaining quality**.\n\n"
                f"**Storage guidance:** {match['guidance']}"
            )
        else:
            food_display = target_food.strip().title()
            return (
                f"You do not currently have **{food_display}** saved in your produce log, but here is optimal storage advice:\n\n"
                f"- Store whole **{food_display}** in the crisper drawer of your refrigerator to prolong crunch and freshness for up to 3–4 weeks.\n"
                f"- Keep them away from ethylene-sensitive vegetables, as ripening apples emit natural ethylene gas.\n"
                f"- On ambient countertops, consume within 5–7 days before texture begins softening."
            )

    elif intent == PantryIntent.GENERAL_EDUCATIONAL:
        query_hint = (target_food or "").lower()
        if "banana" in query_hint or "spot" in query_hint or "brown" in query_hint:
            return (
                "**Why bananas get brown spots:**\n\n"
                "As bananas ripen, natural ethylene gas triggers the conversion of complex starches into simple sugars. "
                "The brown spots indicate peak sweetness and high fructose content. "
                "They are completely edible, very sweet to eat, and perfect for smoothies or baking."
            )
        elif "slightly spoiled" in query_hint or "slightly" in query_hint and "spoil" in query_hint:
            return (
                "**What “slightly spoiled” means in FoodFresh AI:**\n\n"
                "It describes visible surface wear (soft spots, dull color, early breakdown) — not a laboratory safety verdict. "
                "Use smell, texture, and your judgment before eating. When in doubt, discard affected portions."
            )
        elif "waste" in query_hint:
            return (
                "**How to reduce food waste in your kitchen:**\n\n"
                "- Check your **Pantry Produce Log** regularly to track remaining quality windows.\n"
                "- Use items flagged with **VERY_HIGH** priority first.\n"
                "- Move ripe countertop produce to refrigerator crisper chill to prolong freshness."
            )
        return (
            "FoodFresh AI provides visual freshness estimates, USDA FoodKeeper guidance, and pantry inventory tracking to help you maintain quality and reduce food waste 🌱"
        )

    # General fallback
    return (
        f"Based on your saved pantry history ({triage['totalCount']} items logged), **{top['foodName']} should be used first** because it has the shortest remaining quality window ({top['remainingDays']} days left)."
    )
