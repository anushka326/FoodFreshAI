"""
FoodFresh AI - Unified FreshoBuddy AI Service (Groq & optional xAI Grok)
Official Groq SDK backend integration providing 3-tier context isolation (SIMPLE / MEDIUM / STRONG),
strict deterministic Eat First authority, synchronized Pantry Mode ON/OFF, and comprehensive
culinary and food-science intelligence.
"""

from __future__ import annotations

import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from backend.app.database import chat_db
from backend.app.services.pantry_triage_service import (
    PantryIntent,
    detect_pantry_intent,
    triage_pantry_items,
    build_deterministic_answer,
)
from backend.app.services.fresho_intent_service import (
    ContextLevel,
    FreshoIntent,
    FOOD_ALIASES,
    detect_fresho_intent,
    extract_food_noun,
    has_pantry_ownership,
    is_follow_up_query,
    map_fresho_intent_to_pantry_intent,
)
from backend.app.services.pantry_state_service import get_current_pantry_state

logger = logging.getLogger("foodfresh.fresho_buddy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
DEFAULT_GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_XAI_GROK_MODEL = "grok-2-latest"
DEFAULT_XAI_GROK_VISION_MODEL = "grok-2-vision-1212"

PREFERRED_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "allam-2-7b",
]

FRESHO_BUDDY_SYSTEM_PROMPT = """You are FreshoBuddy AI 🌱, the intelligent, friendly, and expert food companion inside FoodFresh AI.

You answer BOTH general food science, storage, shelf-life, beverage longevity, dairy/meat preservation, nutrition, and zero-waste cooking questions AND questions grounded in the authenticated user's saved pantry records.

CORE OPERATING PRINCIPLES & APPLICATION AUTHORITY RULES:
1. STRICT CONTEXT BOUNDARIES:
   - When Pantry Mode is OFF (GLOBAL MODE) or NO saved pantry block is provided (SIMPLE context):
     Answer strictly using general culinary knowledge, food science, and storage best practices. Never guess or claim what is in the user's pantry, and NEVER state that you cannot answer because the pantry is empty.
   - When Pantry Mode is ON and a MEDIUM specific-item lookup states that the requested food is NOT saved in the user's pantry:
     Explicitly state that the food is not currently saved in their pantry, then provide helpful general storage/freshness guidance for that food.
   - When Pantry Mode is ON and a STRONG or MEDIUM saved-pantry block is provided:
     Treat the supplied application data as the single source of truth. Never invent pantry items, dates, remaining days, freshness statuses, or confidence scores.
2. DETERMINISTIC EAT FIRST PRIORITY:
   - The application computes the Eat First priority, urgency tier, and remaining quality days deterministically.
   - Explain the supplied Eat First winner (or ties) accurately without altering, inventing, or overriding the ranking.
3. COMPREHENSIVE FOOD CATEGORIES & BEVERAGE INTELLIGENCE:
   - Understand the distinct properties, safety parameters, and shelf lives of:
     * Packaged & carbonated beverages (soft drinks, soda, energy drinks, sports drinks) - opened vs. unopened.
     * Fresh & pasteurized fruit juices.
     * Dairy products (milk, paneer, yogurt/dahi, cheese, butter).
     * Meat, poultry, seafood, and eggs.
     * Cooked meals & leftovers (cooked rice, dal, curry, pasta) - always highlight critical safety (e.g. Bacillus cereus in rice).
     * Bakery products (bread, sourdough, cakes) - emphasize retrogradation staling vs. freezing.
     * Fresh produce (fruits, vegetables, regional Indian crops like Kashmir apples, Alphonso mangoes, Nagpur oranges).
   - Distinguish quality/flavor degradation (e.g. loss of fizz/crispness) from microbial food safety limits.
4. CLEAN MARKDOWN FORMATTING:
   - Use clean GitHub-style Markdown. BOLD key food names, temperatures, and time frames (e.g. **3–5 days**, **below 4 °C**, **Cold Drinks**).
   - Use Markdown tables when comparing storage conditions (Countertop, Refrigerator, Freezer).
   - Be concise, warm, practical, and directly useful.
"""


def load_env_vars() -> None:
    """Load environment variables from backend/.env or root .env safely."""
    for env_candidate in [PROJECT_ROOT / "backend" / ".env", PROJECT_ROOT / ".env"]:
        if env_candidate.exists():
            try:
                with open(env_candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k == "GROQ_API_KEY":
                                # Never overwrite a valid gsk_ key in os.environ with an invalid key
                                existing = os.environ.get("GROQ_API_KEY", "")
                                if existing.startswith("gsk_") and not v.startswith("gsk_"):
                                    continue
                            if k:
                                os.environ[k] = v
            except Exception as e:
                logger.warning(f"Could not load {env_candidate}: {e}")


# Initialize environment on module import
load_env_vars()


def get_provider_config() -> Dict[str, Any]:
    """
    Resolve AI inference provider configuration.
    Primary: Groq via official Groq SDK.
    Optional: xAI Grok when XAI_API_KEY or an 'xai-' key is explicitly supplied.
    """
    load_env_vars()

    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    xai_api_key = os.environ.get("XAI_API_KEY", os.environ.get("GROK_API_KEY", "")).strip()

    # Determine provider
    if xai_api_key or groq_api_key.startswith("xai-"):
        provider = "grok"
        api_key = xai_api_key or groq_api_key
        model = os.environ.get("XAI_MODEL", os.environ.get("GROK_MODEL", DEFAULT_XAI_GROK_MODEL)).strip()
        vision_model = os.environ.get("XAI_VISION_MODEL", DEFAULT_XAI_GROK_VISION_MODEL).strip()
    else:
        provider = "groq"
        api_key = groq_api_key
        model = os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip()
        if not model or model == "llama-3.3-70b-versatile":
            model = DEFAULT_GROQ_MODEL
        vision_model = os.environ.get("GROQ_VISION_MODEL", DEFAULT_GROQ_VISION_MODEL).strip()

    base_url = os.environ.get("GROQ_BASE_URL", os.environ.get("GROK_BASE_URL", "")).strip()
    is_groq_key_valid_shape = bool(api_key and (api_key.startswith("gsk_") or api_key.startswith("xai-")))

    return {
        "provider": provider,
        "api_key": api_key,
        "is_valid_shape": is_groq_key_valid_shape,
        "model": model,
        "vision_model": vision_model,
        "base_url": base_url,
    }


def derive_conversation_title(first_user_message: str, food_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Deterministic generation of a clean, meaningful conversation title from the first message and context.
    Matches user expectations (e.g. 'Pantry Priority', 'Apple Storage Advice', 'Banana Browning').
    """
    msg_lower = (first_user_message or "").lower()

    if any(p in msg_lower for p in ("eat first", "which food", "use first", "consume first")):
        return "Pantry Priority"
    if any(p in msg_lower for p in ("cook today", "cook tonight", "what to make", "what can i cook")):
        return "Pantry Meal Ideas"
    if any(p in msg_lower for p in ("expir", "attention", "quality limit")):
        return "Expiring Foods"
    if "reduce" in msg_lower and "waste" in msg_lower:
        return "Reduce Food Waste"
    if "brown spot" in msg_lower or ("banana" in msg_lower and "brown" in msg_lower):
        return "Banana Browning"
    if any(p in msg_lower for p in ("pantry", "inventory", "what food")):
        return "Pantry Overview"

    if food_context and (food_context.get("detectedFood") or food_context.get("foodName")):
        food = (food_context.get("detectedFood") or food_context.get("foodName")).strip().title()
        if any(p in msg_lower for p in ("store", "keep", "fridge")):
            return f"{food} Storage Advice"
        if any(p in msg_lower for p in ("fresh", "spoil", "rot")):
            return f"{food} Freshness"
        if any(p in msg_lower for p in ("recipe", "cook", "eat")):
            return f"{food} Ideas"
        return f"{food} Discussion"

    # Specific storage questions (e.g. "How should I store apples?")
    store_match = re.search(r"how (?:should|to|do) i store (?:this |the |my |fresh |ripe )?([a-z\s]+)", msg_lower)
    if store_match:
        target = store_match.group(1).replace("?", "").strip().title()
        if target:
            return f"{target} Storage Advice"[:40]

    # Fallback to first few words
    clean = re.sub(r"[^\w\s]", "", first_user_message).strip()
    words = clean.split()
    if not words:
        return "New Food Discussion"

    title = " ".join(words[:4]).title()
    return title[:40]


def resolve_follow_up_context(history: List[Dict[str, Any]]) -> Tuple[Optional[str], bool, Optional[FreshoIntent], ContextLevel]:
    """
    Inspect previous conversation turns to resolve pronouns ('it', 'that one', 'why')
    to a concrete produce name and prior context level.
    """
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        role = msg.get("role")
        if role not in ("assistant", "bot"):
            continue

        text = msg.get("content") or msg.get("text") or ""

        # Find preceding user message
        prev_user_text = ""
        for j in range(i - 1, -1, -1):
            if history[j].get("role") == "user":
                prev_user_text = history[j].get("content") or history[j].get("text") or ""
                break

        prev_intent, prev_level, prev_target = detect_fresho_intent(prev_user_text)
        was_pantry_scoped = (
            prev_level in (ContextLevel.STRONG, ContextLevel.MEDIUM)
            or any(k in text.lower() for k in ("saved pantry", "should be used first", "pantry produce log", "days remaining", "priority:"))
        )

        resolved_food: Optional[str] = None
        m_first = re.search(r"\*\*([A-Za-z][A-Za-z\s]{1,30}?)\s+should be used first\*\*", text)
        if m_first:
            resolved_food = extract_food_noun(m_first.group(1)) or m_first.group(1).strip()

        if not resolved_food:
            bold_matches = re.findall(r"\*\*([A-Za-z][A-Za-z\s]{1,30}?)\*\*", text)
            for cand_str in bold_matches:
                cand_noun = extract_food_noun(cand_str)
                if cand_noun:
                    resolved_food = cand_noun
                    break

        if not resolved_food:
            resolved_food = prev_target or extract_food_noun(prev_user_text) or extract_food_noun(text)

        return resolved_food, was_pantry_scoped, prev_intent, prev_level

    return None, False, None, ContextLevel.SIMPLE


def find_matching_pantry_items(triage: Dict[str, Any], target_food: Optional[str]) -> List[Dict[str, Any]]:
    """Find items in user's pantry triage matching a canonical food noun."""
    if not triage or not triage.get("hasItems") or not target_food:
        return []
    needle = target_food.lower().strip()
    canonical_needle = FOOD_ALIASES.get(needle, needle)

    matches = []
    for it in triage.get("rankedItems", []):
        name_low = str(it.get("foodName", "")).lower()
        name_canonical = FOOD_ALIASES.get(name_low, extract_food_noun(name_low) or name_low)
        if canonical_needle in name_low or name_low in canonical_needle or name_canonical == canonical_needle:
            matches.append(it)
    return matches


def enforce_application_authority(
    reply_text: str,
    context_level: ContextLevel,
    fresho_intent: FreshoIntent,
    triage: Optional[Dict[str, Any]],
    matched_items: List[Dict[str, Any]],
    target_food: Optional[str],
) -> str:
    """
    Ensure the LLM does not override or omit deterministic application facts:
    1. Eat First winner is always explicitly stated.
    2. Missing items are explicitly declared not in the user's pantry.
    """
    text = (reply_text or "").strip()
    if not text:
        return text

    if context_level == ContextLevel.STRONG and fresho_intent == FreshoIntent.PANTRY_PRIORITY:
        if triage and triage.get("hasItems") and triage.get("topUrgent"):
            top = triage["topUrgent"]
            winners = triage["tiedTop"] if triage.get("isTie") else [top]
            missing_winner = any(w["foodName"].lower() not in text.lower() for w in winners)
            if missing_winner:
                names = " and ".join(f"**{w['foodName']}**" for w in winners)
                rem_txt = f"{winners[0]['remainingDays']} days remaining" if winners[0].get("remainingDays") is not None else "pending"
                text = f"**Application Eat First Priority:** {names} ({rem_txt}, {winners[0]['tier']} priority).\n\n{text}"

    elif context_level == ContextLevel.MEDIUM and target_food and len(matched_items) == 0:
        low = text.lower()
        if "not" not in low or "pantry" not in low:
            titled = target_food.strip().title()
            text = f"**{titled}** is not currently saved in your pantry log.\n\n{text}"

    return text


class FreshoBuddyService:
    """
    Unified FreshoBuddy AI Service coordinating Groq (primary) and optional xAI Grok inference
    with deterministic Eat First authority, 3-tier context isolation, and persistent history.
    """

    _instance: Optional["FreshoBuddyService"] = None

    def __init__(self):
        self._init_clients()

    @classmethod
    def get_instance(cls) -> "FreshoBuddyService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_clients(self) -> None:
        """Initialize official Groq client or configure xAI Grok provider."""
        self.cfg = get_provider_config()
        self.groq_client = None
        self.is_configured = False

        if not self.cfg["api_key"]:
            logger.info("FreshoBuddy: No API key configured. Operating in domain intelligence mode.")
            return

        if self.cfg["provider"] == "groq":
            try:
                from groq import Groq

                kwargs: Dict[str, Any] = {"api_key": self.cfg["api_key"], "timeout": 45.0, "max_retries": 2}
                if self.cfg["base_url"]:
                    kwargs["base_url"] = self.cfg["base_url"]
                self.groq_client = Groq(**kwargs)
                self.is_configured = True
                logger.info(f"FreshoBuddy initialized with official Groq SDK (Model: {self.cfg['model']})")
            except Exception as e:
                logger.warning(f"Could not initialize Groq SDK client: {e}")
                self.is_configured = False
        else:
            # xAI Grok provider
            self.is_configured = True
            logger.info(f"FreshoBuddy initialized with xAI Grok provider (Model: {self.cfg['model']})")

    def generate_reply(
        self,
        user_message: str,
        user_id: str = "guest",
        history: Optional[List[Dict[str, Any]]] = None,
        analysis_context: Optional[Dict[str, Any]] = None,
        pantry_items: Optional[List[Dict[str, Any]]] = None,
        pantry_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate response using Groq/Grok or intelligent domain fallback:
        - pantry_mode=False (Global Mode):
            Zero pantry database queries, zero pantry items injected.
            Answers general food science, storage, shelf life, and recipes.
            NEVER replies that the pantry is empty.
        - pantry_mode=True (Pantry Mode):
            3-tier context isolation (SIMPLE / MEDIUM / STRONG).
            Grounds responses in the authenticated user's actual pantry records.
        """
        self._init_clients()
        history = history or []

        # Follow-up resolution
        is_short_follow = len(history) > 0 and is_follow_up_query(user_message)
        fresho_intent, context_level, target_food = detect_fresho_intent(
            user_message,
            has_analysis_context=bool(analysis_context),
            is_short_follow_up=is_short_follow,
        )

        if fresho_intent == FreshoIntent.FOLLOW_UP and len(history) > 0:
            resolved_food, was_pantry_scoped, prior_intent, prior_level = resolve_follow_up_context(history)
            if not target_food:
                target_food = resolved_food
            if not was_pantry_scoped and not analysis_context:
                context_level = ContextLevel.SIMPLE
            else:
                context_level = ContextLevel.MEDIUM

        # Enforce Global Mode boundary: when Pantry Mode is OFF, NEVER query or inject pantry
        if not pantry_mode:
            context_level = ContextLevel.SIMPLE if fresho_intent != FreshoIntent.ANALYSIS_CONTEXT else ContextLevel.MEDIUM
            pantry_items = []
            triage = triage_pantry_items([])
            matched_items: List[Dict[str, Any]] = []
        else:
            # Pantry Mode is ON: load authentic user-scoped pantry data if query is MEDIUM or STRONG
            if context_level in (ContextLevel.MEDIUM, ContextLevel.STRONG) or target_food is not None:
                if pantry_items is None:
                    try:
                        pantry_items = get_current_pantry_state(user_id)
                    except Exception as e:
                        logger.warning(f"Could not load pantry items for user {user_id}: {e}")
                        pantry_items = []
                triage = triage_pantry_items(pantry_items)
            else:
                pantry_items = []
                triage = triage_pantry_items([])

            matched_items = find_matching_pantry_items(triage, target_food) if target_food else []

        # Empty pantry early return ONLY when Pantry Mode is ON and user specifically requested whole-pantry triage
        if pantry_mode and context_level == ContextLevel.STRONG and not triage.get("hasItems"):
            empty_msg = (
                "🌱 **Your pantry is currently empty** — you haven't saved any food items yet.\n\n"
                "To get personalized Eat First rankings and inventory advice here:\n"
                "1. Go to **Analyze Food** to scan fresh produce and save it to your pantry.\n"
                "2. Go to **Packaged Foods** to scan a product barcode or nutrition label.\n\n"
                "Once items are saved, I will track their remaining quality windows, calculate Eat First priorities, "
                "and suggest zero-waste recipes based on what you actually have in stock!\n\n"
                "💡 **Tip:** Turn **Pantry Mode OFF** (toggle switch above) to ask me any general food storage, "
                "shelf-life, or culinary science question without requiring pantry items!"
            )
            return {
                "text": empty_msg,
                "status": "success",
                "model": "fresho_pantry_guard",
                "contextLevel": context_level.value,
                "intent": fresho_intent.value,
                "targetFood": target_food,
                "pantryInjected": False,
                "aiCallAttempted": False,
                "fallbackUsed": False,
                "providerError": None,
            }

        # Build Authority Blocks for LLM Prompt
        authority_block = ""
        if pantry_mode:
            if context_level == ContextLevel.STRONG:
                if triage.get("hasItems"):
                    top = triage["topUrgent"]
                    items_lines = []
                    for it in triage.get("rankedItems", []):
                        rem = it.get("remainingDays")
                        rem_str = f"{rem} days remaining" if rem is not None else "pending estimate"
                        items_lines.append(
                            f"- {it['foodName']}: status={it.get('status', 'Good')} | remaining={rem_str} | priority={it.get('tier', 'NORMAL')} | storage={it.get('storageEnvironment', 'Pantry')}"
                        )
                    tied_names = ", ".join(it["foodName"] for it in triage["tiedTop"]) if triage.get("isTie") else "None"
                    pantry_intent_name = map_fresho_intent_to_pantry_intent(fresho_intent)
                    authority_block = (
                        f"\n[USER SAVED PANTRY LOG — {triage['totalCount']} ITEMS]\n"
                        + "\n".join(items_lines)
                        + f"\n\n[APPLICATION DETERMINISTIC EAT-FIRST CALCULATION]\n"
                        + f"- Detected Intent: {pantry_intent_name}\n"
                        + f"- Calculated Top Priority Food: {top['foodName']} (Tier: {top['tier']}, UrgencyScore: {top.get('urgencyScore', 0)}, Remaining: {top.get('remainingDays')} days)\n"
                        + f"- Is Tied At Top: {triage.get('isTie', False)} (Tied: {tied_names})\n"
                        + f"- Strict Rule: Ground your answer ONLY in the saved items above. Never override the priority ranking or invent foods not listed above.\n"
                    )
            elif context_level == ContextLevel.MEDIUM and target_food:
                if matched_items:
                    lines = [
                        f"- {it['foodName']}: status={it.get('status', 'Good')} | remaining={it.get('remainingDays')} days | priority={it.get('tier', 'NORMAL')} | storage={it.get('storageEnvironment', 'Pantry')}"
                        for it in matched_items
                    ]
                    authority_block = (
                        f"\n[MATCHING SAVED PANTRY RECORD FOR '{target_food.upper()}']\n"
                        + "\n".join(lines)
                        + f"\n- Strict Rule: Cite the exact remaining quality days, freshness status, and priority above. Do not fabricate additional items.\n"
                    )
                else:
                    titled = target_food.strip().title()
                    authority_block = (
                        f"\n[PANTRY LOOKUP RESULT FOR '{target_food.upper()}']\n"
                        + f"- Found In User's Saved Pantry: FALSE (0 matching items for '{target_food}').\n"
                        + f"- Strict Rule: Explicitly state that {titled} is NOT currently saved in the user's pantry, and then provide helpful general storage/freshness guidance for {titled}.\n"
                    )

        # Scanned Food Context (Active scan from Analyze Food)
        scan_context_block = ""
        if analysis_context and (analysis_context.get("detectedFood") or analysis_context.get("foodName")):
            scan_food = analysis_context.get("detectedFood") or analysis_context.get("foodName")
            freshness = analysis_context.get("freshness", {})
            f_label = freshness.get("label") if isinstance(freshness, dict) else str(freshness)
            f_conf = freshness.get("confidence") if isinstance(freshness, dict) else None
            shelf_life = analysis_context.get("shelfLife", {})
            rem = shelf_life.get("remaining", {}) if isinstance(shelf_life, dict) else {}
            rem_str = f"{rem.get('minDays', '?')}–{rem.get('maxDays', '?')} days" if rem else "Guidance unavailable"
            storage = analysis_context.get("storageType") or analysis_context.get("storageEnvironment") or "countertop"
            days_stored = analysis_context.get("daysStored", 0)

            scan_context_block = (
                f"\n[ACTIVE SCANNED FOOD CONTEXT]\n"
                f"- Food Item: {scan_food}\n"
                f"- Estimated Visible Freshness: {f_label or 'Uncertain'} ({f_conf or 'N/A'}% confidence)\n"
                f"- Estimated Remaining Quality Window: {rem_str}\n"
                f"- Storage Environment: {storage}\n"
                f"- Days Stored So Far: {days_stored} days\n"
            )

        # Construct messages payload for LLM
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": FRESHO_BUDDY_SYSTEM_PROMPT}
        ]

        # Multi-turn history injection
        for msg in history[-8:]:
            content = (msg.get("content") or msg.get("text") or "").strip()
            if not content:
                continue
            role = "assistant" if msg.get("role") in ("assistant", "bot") else "user"
            messages.append({"role": role, "content": content})

        context_prefix = f"{authority_block}{scan_context_block}".strip()
        final_user_turn = f"{context_prefix}\n\nUser Question: {user_message}" if context_prefix else user_message
        messages.append({"role": "user", "content": final_user_turn})

        # --- SAFE DIAGNOSTIC LOGGING ---
        ai_attempted = bool(self.is_configured and self.cfg["is_valid_shape"])
        logger.info(
            f"[FreshoBuddy Diagnostic] query='{user_message[:60]}' | intent={fresho_intent.value} | "
            f"context_level={context_level.value} | target_food={target_food} | pantry_mode={pantry_mode} | "
            f"provider={self.cfg['provider']} | configured_model={self.cfg['model']} | "
            f"ai_attempted={ai_attempted}"
        )

        # --- EXECUTE GROQ / GROK INFERENCE ---
        if ai_attempted:
            used_model = self.cfg["model"]
            try:
                raw_reply = ""
                if self.cfg["provider"] == "grok" and not self.cfg["base_url"]:
                    resp = httpx.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.cfg['api_key']}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.cfg["model"],
                            "messages": messages,
                            "temperature": 0.3,
                            "max_tokens": 750,
                        },
                        timeout=45.0,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    raw_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                elif self.groq_client:
                    try:
                        completion = self.groq_client.chat.completions.create(
                            model=self.cfg["model"],
                            messages=messages,
                            temperature=0.3,
                            max_tokens=450,
                        )
                        raw_reply = completion.choices[0].message.content or ""
                    except Exception as primary_err:
                        err_str = str(primary_err).lower()
                        # Fallback model discovery if model not found, rate limited (429), or access denied
                        if "404" in err_str or "429" in err_str or "rate" in err_str or "model_not_found" in err_str or "does not exist" in err_str or "access" in err_str:
                            logger.info(f"Model {self.cfg['model']} unavailable or rate-limited ({primary_err}). Discovering accessible Groq models...")
                            try:
                                model_list = self.groq_client.models.list()
                                available_ids = [
                                    m.id for m in model_list.data
                                    if m.id and not any(k in m.id.lower() for k in ("whisper", "guard", "audio", "orpheus", "tts", "playai"))
                                ]
                                # Prioritize candidates different from the one that just hit rate limit
                                other_candidates = [m for m in PREFERRED_GROQ_MODELS if m in available_ids and m != self.cfg["model"]]
                                remaining = [m for m in available_ids if m not in PREFERRED_GROQ_MODELS and m != self.cfg["model"]]
                                ordered_candidates = other_candidates + remaining
                                for cand in ordered_candidates:
                                    try:
                                        completion = self.groq_client.chat.completions.create(
                                            model=cand,
                                            messages=messages,
                                            temperature=0.3,
                                            max_tokens=450,
                                        )
                                        raw_reply = completion.choices[0].message.content or ""
                                        if raw_reply:
                                            used_model = cand
                                            self.cfg["model"] = cand
                                            logger.info(f"[FreshoBuddy Diagnostic] Successfully recovered with available Groq model: {cand}")
                                            break
                                    except Exception:
                                        continue
                                if not raw_reply:
                                    raise primary_err
                            except Exception as fb_err:
                                raise fb_err from primary_err
                        else:
                            raise primary_err

                if raw_reply and raw_reply.strip():
                    enforced_reply = enforce_application_authority(
                        reply_text=raw_reply.strip(),
                        context_level=context_level,
                        fresho_intent=fresho_intent,
                        triage=triage,
                        matched_items=matched_items,
                        target_food=target_food,
                    )
                    logger.info(f"[FreshoBuddy Diagnostic] AI inference SUCCEEDED using model='{used_model}'")
                    return {
                        "text": enforced_reply,
                        "status": "success",
                        "model": f"{self.cfg['provider']}:{used_model}",
                        "contextLevel": context_level.value,
                        "intent": fresho_intent.value,
                        "targetFood": target_food,
                        "pantryInjected": bool(authority_block),
                        "aiCallAttempted": True,
                        "fallbackUsed": False,
                        "providerError": None,
                    }
            except Exception as e:
                last_provider_error = f"{type(e).__name__}: {e}"
                logger.warning(f"[FreshoBuddy Diagnostic] AI Provider call failed ({type(e).__name__}: {e}). Activating domain intelligence.")
        else:
            last_provider_error = "AI credentials not configured or invalid API key format."

        # --- DOMAIN INTELLIGENCE ENGINE (Guarantees zero downtime & accurate grounded guidance) ---
        logger.info(f"[FreshoBuddy Diagnostic] Domain intelligence activated for query: '{user_message[:50]}'")
        pantry_intent = map_fresho_intent_to_pantry_intent(fresho_intent)
        deterministic_fallback = build_deterministic_answer(pantry_intent, triage, target_food) if pantry_mode else ""

        domain_response = _generate_domain_fallback(
            user_message=user_message,
            triage=triage,
            intent=pantry_intent,
            target_food=target_food,
            deterministic_fallback=deterministic_fallback,
            analysis_context=analysis_context,
            pantry_mode=pantry_mode,
        )

        enforced_domain = enforce_application_authority(
            reply_text=domain_response,
            context_level=context_level,
            fresho_intent=fresho_intent,
            triage=triage,
            matched_items=matched_items,
            target_food=target_food,
        )

        return {
            "text": enforced_domain,
            "status": "fallback",
            "model": "fresho_domain_intelligence",
            "contextLevel": context_level.value,
            "intent": fresho_intent.value,
            "targetFood": target_food,
            "pantryInjected": bool(authority_block),
            "aiCallAttempted": ai_attempted,
            "fallbackUsed": True,
            "providerError": last_provider_error,
        }


# ── Domain Fallback Food Intelligence Knowledge Base ─────────────────────────

def _generate_domain_fallback(
    user_message: str,
    triage: Dict[str, Any],
    intent: str,
    target_food: Optional[str],
    deterministic_fallback: str,
    analysis_context: Optional[Dict[str, Any]],
    pantry_mode: bool = False,
) -> str:
    """
    Produce rich, science-backed answers for food queries when API is unreachable.
    Guarantees that Global Mode (pantry_mode=False) never outputs an empty-pantry message.
    """
    q = user_message.lower().strip()
    identified_food = target_food or extract_food_noun(q)

    # 1. Pantry-specific triage when Pantry Mode is explicitly ON
    if pantry_mode:
        if intent in (
            PantryIntent.EAT_FIRST,
            PantryIntent.EXPIRING_SOON,
            PantryIntent.SHORTEST_SHELF_LIFE,
            PantryIntent.LONGEST_SHELF_LIFE,
            PantryIntent.FRESHEST,
            PantryIntent.LEAST_FRESH,
            PantryIntent.PRIORITY_HIGH,
            PantryIntent.PRIORITY_LOW,
        ):
            if triage.get("hasItems"):
                return deterministic_fallback
            else:
                return (
                    "🌱 **Your pantry is currently empty.**\n\n"
                    "Scan and save food items in **Analyze Food** to track real-time freshness and get Eat First rankings!\n\n"
                    "💡 Turn **Pantry Mode OFF** to ask general food questions."
                )

        if intent == PantryIntent.PANTRY_INVENTORY or any(k in q for k in ("what food do i have", "what foods do i have", "currently have", "in my pantry", "list my food")):
            if triage.get("hasItems"):
                lines = []
                for it in triage.get("rankedItems", []):
                    rem = it.get("remainingDays")
                    rem_txt = f"{rem} days remaining" if rem is not None else "pending estimate"
                    lines.append(f"- **{it['foodName']}** — {it.get('status', 'Good')} ({rem_txt}, Priority: **{it.get('tier', 'NORMAL')}**)")
                return f"You currently have **{triage['totalCount']} items** in your saved pantry:\n\n" + "\n".join(lines)
            return "Your pantry is currently empty. Scan items in **Analyze Food** or **Packaged Foods** to add them to your pantry 🌱"

        if (intent == PantryIntent.PANTRY_ITEM_LOOKUP or intent == PantryIntent.SPECIFIC_FOOD_STORAGE) and identified_food:
            matches = find_matching_pantry_items(triage, identified_food)
            if matches:
                m = matches[0]
                rem = m.get("remainingDays")
                rem_txt = f"**{rem} days remaining**" if rem is not None else "pending estimate"
                return f"According to your saved pantry history, you have **{m['foodName']}** ({m.get('status', 'Good')}, {rem_txt}, stored in **{m.get('storageEnvironment', 'Pantry')}**, Priority: **{m.get('tier', 'NORMAL')}**)."
            titled = identified_food.strip().title()
            return f"**{titled}** is not currently saved in your pantry history.\n\n" + _storage_guidance(identified_food)

    # 2. Regional Produce Queries (e.g. Maharashtra, India)
    is_regional = any(k in q for k in ("maharashtra", "india", "regional", "local market", "pune", "mumbai", "nashik", "nagpur", "solapur", "satara", "vidarbha", "marathwada"))
    is_low_shelf = any(k in q for k in ("low shelf", "very low", "short shelf", "shortest", "spoil fast", "spoil quick", "perish", "less shelf", "minimum shelf", "shorter shelf", "quick to rot", "rot fast"))
    is_high_shelf = any(k in q for k in ("high shelf", "very high", "long shelf", "longest shelf", "more shelf", "highest shelf", "longer shelf", "durable", "lasts longest"))

    if ("fruit" in q or "produce" in q or "crop" in q or "vegetable" in q) and is_regional:
        if is_low_shelf:
            return (
                "## Fruits with Very Low Shelf Life in Maharashtra 🍓\n\n"
                "Maharashtra's diverse agro-climatic zones produce delicate fruits that have a very short natural shelf life and require immediate consumption or cold storage:\n\n"
                "1. **Strawberries (Mahabaleshwar & Panchgani, Satara district):**\n"
                "   - **Shelf Life:** **1–2 days** at room temperature; **3–5 days** refrigerated (below 4 °C).\n"
                "   - Extremely thin skin and high moisture content make them highly vulnerable to mold within 48 hours.\n\n"
                "2. **Fresh Figs / Anjeer (Purandar / Saswad, Pune district):**\n"
                "   - **Shelf Life:** **1–2 days** fresh.\n"
                "   - Fresh figs do not ripen after harvest and ferment very rapidly at room temperature.\n\n"
                "3. **Custard Apple / Sitaphal (Beed, Jalgaon, Aurangabad):**\n"
                "   - **Shelf Life:** **1–2 days** once soft-ripe.\n"
                "   - Once ripe, the aromatic pulp breaks down quickly into ethanol at ambient temperatures.\n\n"
                "4. **Mulberries / Tut (Mahabaleshwar):**\n"
                "   - **Shelf Life:** **1 day** at room temp; **2–3 days** refrigerated.\n"
                "   - Highly perishable; consume immediately or preserve into fruit crush or jam.\n\n"
                "5. **Ripe Alphonso & Kesar Mangoes (Ratnagiri, Devgad, Sindhudurg):**\n"
                "   - **Shelf Life:** **3–5 days** once fully ripe and yellow.\n"
                "   - While green raw mangoes keep for weeks, tree-ripened Alphonso mangoes soften quickly.\n\n"
                "6. **Grapes (Nashik & Sangli):**\n"
                "   - **Shelf Life:** **3–5 days** at room temp; **1–2 weeks** refrigerated.\n\n"
                "💡 **Preservation Tip:** Keep strawberries and figs unwashed in a single layer with a dry paper towel in your refrigerator crisper (below 4 °C). 🌱"
            )
        elif is_high_shelf or not is_low_shelf:
            return (
                "## Fruits with High Shelf Life in Maharashtra & Western India 🍎\n\n"
                "Maharashtra is one of India's leading fruit-producing states. Fruits available locally that have a long natural shelf life include:\n\n"
                "1. **Pomegranate (डाळिंब / Anar) — *Solapur, Nashik & Sangli*:**\n"
                "   - **Shelf Life:** **3–4 weeks** at room temperature; **up to 2 months** refrigerated below 5 °C.\n"
                "   - Their thick, leathery rind naturally prevents moisture loss and microbial spoilage.\n\n"
                "2. **Nagpur Orange & Sweet Lime (Mosambi) — *Vidarbha, Marathwada & Jalna*:**\n"
                "   - **Shelf Life:** **2–3 weeks** at room temperature; **4–6 weeks** in the refrigerator crisper.\n"
                "   - Thick citrus peels protect against bruising and slow respiration.\n\n"
                "3. **Indian Gooseberry (Amla) — *Widespread in Maharashtra*:**\n"
                "   - **Shelf Life:** **2–3 weeks** fresh; months when pickled or kept in brine.\n\n"
                "4. **Apples (Himachal/Kashmir varieties widely distributed in Maharashtra markets):**\n"
                "   - **Shelf Life:** **2–4 weeks** at cool room temperature; **1–2 months** refrigerated.\n\n"
                "5. **Raw / Green Mangoes (Kacchi Kairi / Alphonso):**\n"
                "   - Stored in a cool, ventilated basket, raw mangoes keep for **1–2 weeks** before gradual ripening.\n\n"
                "💡 **Storage Tip:** Store pomegranates and citrus in a cool, ventilated basket away from direct sunlight, or in the refrigerator's crisper drawer. 🌱"
            )

    # 3. Category-specific shelf life queries
    # 3a. Packaged beverages & cold drinks
    if any(k in q for k in ("cold drink", "cold drinks", "soft drink", "soft drinks", "soda", "cola", "coke", "pepsi", "sprite", "fanta", "energy drink", "sports drink", "beverage", "beverages")):
        return _shelf_life_guidance("cold drink")

    # 3b. Fresh and packaged juices
    if "juice" in q:
        return _shelf_life_guidance("juice")

    # 3c. Cooked food, rice & leftovers
    if any(k in q for k in ("cooked rice", "rice", "cooked food", "leftover", "leftovers", "curry", "dal", "pasta")):
        return _shelf_life_guidance("cooked rice" if "rice" in q else "cooked food")

    # 3d. Dairy products
    if any(k in q for k in ("milk", "dairy", "paneer", "cheese", "yogurt", "curd", "dahi", "butter", "lassi", "chaas")):
        return _shelf_life_guidance(identified_food or "milk")

    # 3e. Bakery products
    if any(k in q for k in ("bread", "sourdough", "bakery", "cake", "roti", "chapati")):
        return _shelf_life_guidance(identified_food or "bread")

    # 3f. Meat, poultry & seafood
    if any(k in q for k in ("meat", "chicken", "poultry", "fish", "seafood", "egg", "eggs", "mutton", "prawns")):
        return _shelf_life_guidance(identified_food or "meat")

    # 3g. Specific produce item shelf life (e.g. Kashmir apples, bananas, strawberries)
    if any(k in q for k in ("shelf life", "shelf-life", "how long", "last", "stay fresh", "how many days", "average", "more shelf", "longer shelf")):
        if identified_food:
            return _shelf_life_guidance(identified_food)
        return (
            "## General Kitchen Shelf Life Overview\n\n"
            "| Food Category | Room Temperature | Refrigerator (below 4 °C) | Freezer (-18 °C) |\n"
            "|---|---|---|---|\n"
            "| **Fresh Produce (Greens & Berries)** | 1–2 days | 3–7 days | 6–12 months |\n"
            "| **Hard Produce (Apples, Pomegranates, Citrus)** | 2–3 weeks | 1–2 months | 8–12 months |\n"
            "| **Packaged Soft Drinks (Unopened)** | 6–12 months | 9–18 months | Do not freeze in can |\n"
            "| **Soft Drinks / Juices (Opened)** | 1 day | 2–4 days | 3–6 months (juices) |\n"
            "| **Dairy (Milk, Paneer)** | 2 hours max | 3–7 days | 2–3 months |\n"
            "| **Cooked Leftovers (Rice, Dal, Curries)** | 2 hours max | 3–4 days | 2–3 months |\n"
            "| **Bakery (Bread & Buns)** | 3–5 days | Not recommended (stales fast) | 3 months |\n\n"
            "**Key Principle:** Which specific food or beverage are you asking about? Ask me about **cold drinks**, **Kashmir apples**, **cooked rice**, or any pantry item for tailored longevity and food safety rules! 🌱"
        )

    # 4. Storage guidance
    if any(k in q for k in ("store", "keep", "fridge", "crisper", "freezer", "refrigerat")):
        return _storage_guidance(identified_food)

    # 5. Banana browning / Ethylene gas / Refrigeration effect on bananas
    if "banana" in q and ("brown" in q or "spot" in q or "refrigerat" in q or "fridge" in q):
        return (
            "## Banana Browning & Refrigeration Science 🍌\n\n"
            "Bananas develop brown spots due to the natural production of **ethylene gas**, an airborne plant hormone that triggers ripening:\n\n"
            "1. **Does Refrigeration Increase Shelf Life?**\n"
            "   - **YES, but only for ripe bananas!** When yellow-ripe bananas are moved to the refrigerator (below 4 °C), the cold environment slows pulp metabolism and extends eating quality by **3–5 extra days**.\n"
            "   - **The Peel vs. Pulp Effect:** The peel will turn dark brown or black within 24 hours due to chilling-induced enzyme activity (polyphenol oxidase), but the fruit inside remains firm, sweet, and perfectly edible!\n"
            "   - **Never refrigerate green bananas:** Chilling green bananas permanently interrupts ripening enzymes, preventing them from ever developing sweetness or proper texture.\n\n"
            "2. **Why Spots Form:** As bananas ripen, enzymes convert complex starches into fructose and glucose. The brown spots indicate peak sweetness and high antioxidant concentration.\n\n"
            "💡 **Storage Tip:** Wrap the banana crown (stem) tightly in foil or beeswax wrap to inhibit ethylene gas release. 🌱"
        )

    # 6. Food Waste reduction
    if "waste" in q or ("reduce" in q and "food" in q):
        return (
            "## Top Strategies to Reduce Food Waste ♻️\n\n"
            "1. **Follow the Eat First Principle:** Keep foods approaching their quality limit at eye level on the top shelf of your refrigerator.\n"
            "2. **Isolate Ethylene Producers:** Store high-ethylene fruits (apples, bananas) separately from ethylene-sensitive greens and berries.\n"
            "3. **Freeze Before Spoilage:** If berries or herbs are softening, wash, chop, and freeze them in airtight containers for smoothies and sauces.\n"
            "4. **Moisture Control:** Wrap herbs and greens in a dry paper towel inside a breathable container to absorb condensation.\n"
            "5. **Revive Wilted Produce:** Limp carrots, celery, and spinach can be refreshed in an ice-water bath for 15 minutes! 🌱"
        )

    # 7. Recipes & Cooking Ideas
    if any(k in q for k in ("recipe", "cook", "make today", "what to make", "what can i cook", "meal idea", "dish")):
        return (
            "## Zero-Waste Kitchen Meal Ideas 🥘\n\n"
            "Here are quick, adaptable meal ideas based on common kitchen produce:\n\n"
            "- **Leafy Greens (Spinach, Methi):** Sauté with garlic, cumin, and olive oil, or fold into eggs/dal.\n"
            "- **Ripe Tomatoes:** Simmer with garlic and basil for quick pasta sauce, or blend into fresh tomato soup.\n"
            "- **Soft Bananas:** Blend with oats and milk for a breakfast smoothie, or bake into zero-waste banana bread.\n"
            "- **Mixed Veggies:** Toss with olive oil, salt, and cumin; roast at 200 °C for 25 minutes for a flavorful roasted medley.\n\n"
            "💡 **Tip:** Turn **Pantry Mode ON** to receive recipe suggestions tailored specifically to your saved pantry inventory! 🌱"
        )

    # 8. Food safety & sensory checks
    if any(k in q for k in ("safe to eat", "gone bad", "spoiled", "mold", "expired", "is it safe", "can i eat")):
        return (
            "## Assessing Produce Freshness & Safety 🔍\n\n"
            "Use the **3-step sensory check** before deciding whether produce is safe:\n\n"
            "1. 👁️ **Look:** Check for fuzzy white/green mold, dark sunken spots, or sliminess. Any mold on soft foods (berries, bread, soft cheese) requires discarding the item.\n"
            "2. 👃 **Smell:** Sour, fermented, or musty odours are clear indicators of microbial spoilage.\n"
            "3. ✋ **Touch:** Excessive mushiness or liquid pooling indicates cellular breakdown.\n\n"
            "**Rule of Thumb:** When in doubt, prioritize your health. FoodFresh AI provides visual freshness estimates, not laboratory microbiology tests. 🌱"
        )

    # 9. Scanned Produce Context
    if analysis_context and (analysis_context.get("detectedFood") or analysis_context.get("foodName")):
        food = analysis_context.get("detectedFood") or analysis_context.get("foodName")
        storage = analysis_context.get("storageType") or "countertop"
        return (
            f"Looking at your scanned **{food}**, it is currently evaluated for **{storage}** storage.\n\n"
            f"To extend its freshness window, keep it in an airtight container or chilled environment (below 4 °C), "
            f"and consume within its estimated quality window. Add it to your FoodFresh AI pantry to monitor it in real time! 🌱"
        )

    # 10. Default General Food Knowledge
    return (
        "## Food Freshness & Storage Wisdom 🌱\n\n"
        "Here are key food science principles to keep your kitchen fresh and reduce waste:\n\n"
        "- 🌡️ **Temperature Control:** Maintain your refrigerator at **1–4 °C** (below 4 °C inhibits pathogenic bacteria).\n"
        "- 🍎 **Ethylene Sensitivity:** Apples, bananas, and tomatoes release ethylene gas that accelerates ripening in nearby greens.\n"
        "- 💧 **Humidity Balance:** High humidity keeps leafy greens crisp; low humidity prevents mold on fruits and berries.\n"
        "- 📦 **FIFO Rule:** First In, First Out — always consume older logged items before opening new packages.\n\n"
        "Ask me anything about food shelf life, storage, nutrition, or regional produce! 🌱"
    )


def _shelf_life_guidance(food_name: str) -> str:
    """Return tailored shelf life guidance for a specific produce, beverage, dairy, cooked food or bakery item."""
    name_low = food_name.lower().strip()

    # 1. Cold drinks, soft drinks & packaged beverages
    if any(k in name_low for k in ("cold drink", "soft drink", "soda", "cola", "coke", "pepsi", "sprite", "fanta", "energy drink", "sports drink", "beverage")):
        return (
            "## Shelf Life of Cold Drinks & Soft Drinks 🥤\n\n"
            "The shelf life of cold drinks depends primarily on whether the container is **unopened** or **opened**, packaging (can vs. plastic bottle), and carbonation:\n\n"
            "| Beverage State | Storage Condition | Shelf Life Window | Sensory & Quality Indicators |\n"
            "|---|---|---|---|\n"
            "| **Unopened Cans** | Cool, dry pantry | **9–12 months** past 'Best By' | Best carbonation seal; remains safe indefinitely if undamaged |\n"
            "| **Unopened Plastic Bottles** | Cool, dark pantry | **3–6 months** past 'Best By' | CO₂ slowly permeates plastic over time, resulting in flatness |\n"
            "| **Opened Can / Bottle** | Refrigerator (below 4 °C) | **2–4 days** tightly capped | Rapidly loses carbonation after 24–48 hours |\n"
            "| **Opened Can / Bottle** | Room temperature | **1 day** | Loses fizz within hours; warm sugary liquid invites mold if left open |\n\n"
            "**Key Principles:**\n"
            "- **Quality vs. Safety:** Commercial soft drinks are acidic and carbonated, making bacterial pathogens extremely rare. Past-date sodas primarily suffer from **loss of carbonation (flat taste)** and flavor degradation rather than food poisoning.\n"
            "- **Opened Storage:** Always re-cap tightly and refrigerate below **4 °C** to preserve dissolved CO₂.\n"
            "- **Can Caution:** Once opened, transfer leftover soda from an aluminum can to a sealed glass or plastic container if storing beyond 24 hours. 🌱"
        )

    # 2. Fruit juices (Fresh vs. pasteurized)
    if "juice" in name_low:
        return (
            "## Shelf Life of Fruit Juices 🍊\n\n"
            "| Juice Type | Unopened | Opened (Refrigerated < 4 °C) | Freezer (-18 °C) |\n"
            "|---|---|---|---|\n"
            "| **Fresh / Freshly Squeezed (Unpasteurized)** | — | **24–48 hours** | **3–6 months** |\n"
            "| **Refrigerated Carton (Pasteurized)** | Use-by date | **7–10 days** | **8–12 months** |\n"
            "| **Shelf-Stable Bottled / Canned** | **9–12 months** | **7–10 days** | **8–12 months** |\n\n"
            "**Food Safety Notice:** Unpasteurized fresh juices ferment rapidly due to wild yeasts and high natural sugar. If the container puffs or tastes fizzy/sour, discard immediately. 🌱"
        )

    # 3. Cooked rice & leftovers
    if any(k in name_low for k in ("rice", "cooked", "leftover", "pasta", "curry", "dal")):
        item_title = "Cooked Rice" if "rice" in name_low else "Cooked Food & Leftovers"
        return (
            f"## Shelf Life & Food Safety: {item_title} 🍚\n\n"
            "| Storage Condition | Safe Window | Quality & Safety Notes |\n"
            "|---|---|---|\n"
            "| **Refrigerator (below 4 °C)** | **3–4 days** | Store in shallow airtight containers to cool rapidly |\n"
            "| **Freezer (-18 °C)** | **2–3 months** | Texture holds best if frozen immediately upon cooling |\n"
            "| **Room Temperature (above 20 °C)** | **2 hours maximum** | High danger zone for bacterial multiplication |\n\n"
            "**CRITICAL FOOD SAFETY RULE (Bacillus cereus):**\n"
            "- Uncooked rice often contains spores of *Bacillus cereus*, a bacterium that survives boiling.\n"
            "- If cooked rice is left at room temperature, spores can germinate into bacteria that produce heat-resistant toxins causing food poisoning.\n"
            "- **Rule of Thumb:** Cool cooked rice and refrigerate within **1 hour** of cooking. Reheat thoroughly until steaming hot (above 74 °C), and never reheat more than once! 🌱"
        )

    # 4. Dairy products
    if any(k in name_low for k in ("milk", "dairy", "paneer", "cheese", "yogurt", "curd", "dahi", "butter")):
        return (
            "## Shelf Life of Dairy Products 🥛\n\n"
            "| Dairy Item | Refrigerator (below 4 °C) | Freezer (-18 °C) | Spoilage Signs |\n"
            "|---|---|---|---|\n"
            "| **Fresh Milk (Opened)** | **5–7 days** | **3 months** (thawed milk separates, best for baking) | Sour odor, curdling in hot coffee |\n"
            "| **Fresh Paneer (in water)** | **3–5 days** (change water daily) | **2–3 months** | Slimy texture, sour pungent smell |\n"
            "| **Yogurt / Curd / Dahi** | **7–14 days** | Not recommended (breaks texture) | Pink/green mold spots, gas pockets |\n"
            "| **Hard Cheeses (Cheddar, Parmesan)** | **3–4 weeks** opened | **6–9 months** | Surface mold can be trimmed 1 inch around |\n"
            "| **Soft Cheeses (Mozzarella, Ricotta)** | **1–2 weeks** | Not recommended | Any visible mold means discard whole batch |\n\n"
            "**Storage Tip:** Store milk on interior refrigerator shelves rather than door pockets where temperatures fluctuate during door opening. 🌱"
        )

    # 5. Bakery
    if any(k in name_low for k in ("bread", "sourdough", "bakery", "cake", "roti", "chapati")):
        return (
            "## Shelf Life of Bread & Bakery 🍞\n\n"
            "| Storage Method | Duration | Best For |\n"
            "|---|---|---|\n"
            "| **Countertop Breadbox / Sealed Bag** | **3–5 days** (artisanal: 2–3 days, commercial: 5–7 days) | Soft crumb and optimal crust texture |\n"
            "| **Refrigerator (below 4 °C)** | **NOT RECOMMENDED** (stales 3x faster) | Retrogradation crystallizes starch rapidly |\n"
            "| **Freezer (-18 °C, sliced)** | **3 months** | Best long-term storage; pop slices straight into toaster! |\n\n"
            "**Food Safety:** Discard bread immediately if white, green, or black fuzzy mold appears — mold hyphae penetrate deeply through porous baked goods. 🌱"
        )

    # 6. Meat, poultry & seafood
    if any(k in name_low for k in ("meat", "chicken", "poultry", "fish", "seafood", "egg", "eggs", "mutton", "prawns")):
        return (
            "## Shelf Life of Meat, Poultry, Seafood & Eggs 🍗\n\n"
            "| Item | Refrigerator (below 4 °C) | Freezer (-18 °C) | Key Safety Rule |\n"
            "|---|---|---|---|\n"
            "| **Raw Poultry & Minced Meat** | **1–2 days** | **9–12 months** | Keep on bottom shelf to prevent drips |\n"
            "| **Raw Fish & Shellfish** | **1–2 days** | **3–6 months** | Store on ice inside refrigerator |\n"
            "| **Raw Steaks, Chops & Roasts** | **3–5 days** | **6–12 months** | Pat dry and wrap airtight |\n"
            "| **Cooked Meat Leftovers** | **3–4 days** | **2–3 months** | Cool and refrigerate within 2 hours |\n"
            "| **Fresh Eggs (Raw in shell)** | **3–5 weeks** | Do not freeze in shell | Float test: bad eggs float due to gas build-up |\n\n"
            "**Food Safety Alert:** Never rinse raw chicken or meat under the tap — splashing spreads bacteria across kitchen surfaces! 🌱"
        )

    # 7. Apples (Kashmir, Himachal, Green, Red)
    if "apple" in name_low:
        return (
            "## Shelf Life of Fresh Apples (including Kashmir & Green Apples) 🍎\n\n"
            "Apples are climacteric fruits with sturdy cellular walls that maintain crunch exceptionally well under cold storage:\n\n"
            "| Storage Method | Estimated Shelf Life | Quality & Texture Notes |\n"
            "|---|---|---|\n"
            "| **Countertop / Room Temp** | **2–4 weeks** | Kashmir & Granny Smith varieties stay firm for 2–3 weeks; keep out of direct sun |\n"
            "| **Refrigerator (below 4 °C)** | **1–2 months** | Optimal crisper humidity preserves natural moisture and tart sweetness |\n"
            "| **Controlled Atmosphere (Commercial)** | **3–6 months** | Standard for cold-stored Kashmir harvests distributed across India |\n"
            "| **Freezer (-18 °C)** | **8–12 months** | Slice, toss with lemon juice, and freeze for pies and smoothies |\n\n"
            "**Storage Tips to Maximize Freshness:**\n"
            "- **Ethylene Isolation:** Apples emit natural **ethylene gas**, which accelerates ripening in nearby leafy greens and bananas. Store them in a separate crisper drawer.\n"
            "- **Keep Dry:** Do not wash apples until right before eating; premature surface moisture triggers fungal breakdown.\n"
            "- **Sensory Check:** Check for soft brown bruising or wrinkled skin. Slightly wrinkled apples are still safe for applesauce or baking! 🌱"
        )

    # 8. Bananas
    if "banana" in name_low:
        return (
            "## Shelf Life of Bananas 🍌\n\n"
            "| Storage Method | Estimated Duration |\n"
            "|---|---|---|\n"
            "| **Countertop (Green / Semi-ripe)** | **3–5 days** |\n"
            "| **Countertop (Yellow / Ripe)** | **2–4 days** |\n"
            "| **Refrigerator (Ripe only)** | **5–7 days** (peel darkens, pulp stays firm) |\n"
            "| **Freezer (Peeled)** | **3–6 months** (great for smoothies & baking) |\n\n"
            "**Storage Tip:** Never refrigerate green bananas — chilling interrupts enzymatic ripening permanently. Wrap stems in foil to slow ethylene release. 🌱"
        )

    # 9. Strawberries & Berries
    if "strawberry" in name_low or "berries" in name_low or "blueberry" in name_low:
        return (
            f"## Shelf Life of {food_name.title()} 🍓\n\n"
            "| Storage Method | Estimated Duration |\n"
            "|---|---|---|\n"
            "| **Countertop / Room Temp** | **1–2 days** |\n"
            "| **Refrigerator (below 4 °C)** | **3–7 days** |\n"
            "| **Freezer (-18 °C)** | **10–12 months** |\n\n"
            "**Storage Tips:**\n"
            "- **Do not wash** until immediately before eating. Surface moisture promotes rapid botrytis (gray mold).\n"
            "- Store unwashed on a dry paper towel in a breathable container. 🌱"
        )

    # 10. Tomatoes
    if "tomato" in name_low:
        return (
            "## Shelf Life of Fresh Tomatoes 🍅\n\n"
            "| Storage Method | Estimated Duration |\n"
            "|---|---|---|\n"
            "| **Countertop (Stem down, room temp)** | **4–7 days** |\n"
            "| **Refrigerator (Fully ripe)** | **1–2 weeks** (bring to room temp before serving) |\n"
            "| **Freezer (Whole or pureed)** | **6–8 months** |\n\n"
            "**Storage Tip:** Storing unripe tomatoes below 10 °C permanently destroys volatile aroma compounds. Keep on countertop until fully red! 🌱"
        )

    # General produce guidance fallback
    return (
        f"## Shelf Life Guidance for {food_name.title()}\n\n"
        f"| Storage Method | Estimated Duration |\n"
        f"|---|---|---|\n"
        f"| **Countertop / Room Temp** | **2–5 days** |\n"
        f"| **Refrigerator (below 4 °C)** | **1–2 weeks** |\n"
        f"| **Freezer (-18 °C)** | **6–10 months** |\n\n"
        f"**Best Storage Practices:**\n"
        f"- Refrigerate below **4 °C** in the crisper drawer to slow cellular respiration.\n"
        f"- Keep unwashed until ready to prepare to prevent moisture-induced mold.\n"
        f"- Separate from strong ethylene emitters (apples, bananas) to prolong freshness. 🌱"
    )


def _storage_guidance(food_name: Optional[str]) -> str:
    """Return storage guidance for a specific produce item, beverage, dairy, cooked food or general guidance."""
    if not food_name:
        return (
            "## General Kitchen Storage Guide 🥬\n\n"
            "**Refrigerator (below 4 °C):**\n"
            "- **Produce & Leafy Greens:** High-humidity crisper drawer with a dry paper towel.\n"
            "- **Opened Soft Drinks & Juices:** Tightly capped on middle shelf (2–4 days).\n"
            "- **Dairy & Milk:** Interior shelves (avoid door pockets where temperature swings occur).\n"
            "- **Cooked Leftovers:** Sealed shallow containers within 2 hours of cooking.\n\n"
            "**Pantry / Countertop (Cool & Dry):**\n"
            "- **Unopened Cans & Beverages:** Cool, dry area away from direct heat.\n"
            "- **Bananas, Mangoes, Tomatoes:** Keep at room temp until ripe.\n"
            "- **Bread:** Store in a breathable breadbox at room temp (never in fridge!).\n\n"
            "Ask about any specific food item for tailored storage advice! 🌱"
        )

    name_low = food_name.lower().strip()
    name_title = food_name.title()

    if any(k in name_low for k in ("cold drink", "soft drink", "soda", "beverage", "cola")):
        return (
            "## Optimal Storage Advice for Cold Drinks & Sodas 🥤\n\n"
            "- **Unopened:** Keep in a cool, dark pantry or refrigerator away from direct heat and sunlight. Cans maintain carbonation longer than plastic bottles.\n"
            "- **Opened:** Reseal tightly and refrigerate below **4 °C**. Consume within **2–4 days** for peak fizz.\n"
            "- **Freeze Warning:** Never freeze sealed carbonated cans or glass bottles — freezing liquid expands and can cause explosive rupture! 🌱"
        )

    if any(k in name_low for k in ("cooked", "rice", "leftover")):
        return (
            f"## Optimal Storage Advice for {name_title} 🍚\n\n"
            "- **Rapid Cooling:** Do not let cooked food sit at room temperature for more than **2 hours** (1 hour if ambient temp > 32 °C).\n"
            "- **Shallow Containers:** Divide large portions into shallow, airtight containers so food cools rapidly below 4 °C in the refrigerator.\n"
            "- **Reheating:** Reheat only the portion you plan to eat until steaming hot (74 °C), and do not reheat multiple times. 🌱"
        )

    return (
        f"## Optimal Storage Advice for {name_title}\n\n"
        f"**Best practices for {name_title}:**\n"
        f"- If leafy or tender: store in the refrigerator's crisper drawer at **high humidity** with a clean, dry paper towel.\n"
        f"- If whole fruit: keep on the countertop at room temperature until ripe, then refrigerate below **4 °C** to extend shelf life.\n"
        f"- **Do not wash** before storage — excess surface moisture promotes premature microbial spoilage.\n"
        f"- Keep separated from heavy ethylene producers (apples, bananas) to prevent over-ripening.\n\n"
        f"Add **{name_title}** to your FoodFresh AI pantry to track its exact quality window! 🌱"
    )


def get_fresho_buddy_service() -> FreshoBuddyService:
    """Singleton getter for FreshoBuddyService."""
    return FreshoBuddyService.get_instance()
