"""
FoodFresh AI - FreshoBuddy Gemini AI Service
Official Google GenAI backend integration providing context-aware food companion guidance,
strict food safety disclaimers, deterministic pantry triage, and transparent integration with the hybrid vision pipeline.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.database import chat_db
from backend.app.services.pantry_triage_service import (
    PantryIntent,
    triage_pantry_items,
    build_deterministic_answer,
)
from backend.app.services.fresho_intent_service import (
    ContextLevel,
    FreshoIntent,
    detect_fresho_intent,
    map_fresho_intent_to_pantry_intent,
)
from backend.app.services.pantry_state_service import get_current_pantry_state

logger = logging.getLogger("foodfresh.fresho_buddy")

# Load environment variables from .env or backend/.env if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
for env_candidate in [PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"]:
    if env_candidate.exists():
        try:
            with open(env_candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            logger.warning(f"Could not load {env_candidate}: {e}")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

FRESHO_BUDDY_SYSTEM_PROMPT = """You are FreshoBuddy AI 🌱, the food intelligence assistant inside FoodFresh AI.

Your job is to help users understand their currently logged foods, reduce food waste, choose what to use first, understand freshness and storage, and make practical meal decisions.

CORE RULES:
1. PANTRY AS SOURCE OF TRUTH: When pantry/history data is supplied, treat it as the primary source for questions about the user's foods. Never invent pantry items, freshness values, shelf-life values, analysis results, dates, or confidence values.
2. DETERMINISTIC PRIORITY: For history-based questions, use the supplied structured pantry data and explain the deterministic priority calculated by the application. Do not override or invent a different ranking.
3. FOOD SAFETY DISCLAIMER: You are not a laboratory food-safety inspector. Visual freshness analysis is an estimate of visible condition and does not guarantee food safety. If an item appears visibly spoiled, moldy, rotten, leaking, or otherwise questionable, advise the user not to rely only on the model and to use appropriate sensory judgment (smell, texture, firmness).
4. MARKDOWN FORMATTING & BOLDING: Use Markdown formatting. Bold important food names, decisions, and key values (for example: **Mango should be used first**, **0 days remaining**). Never output literal asterisks in a way that escapes Markdown formatting.
5. CONCISE & ACTIONABLE: Keep responses practical, concise, friendly, and easy for a normal household user to understand. Avoid generic boilerplate when user history is provided.
"""


def derive_conversation_title(first_user_message: str, food_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Deterministic generation of a clean, meaningful conversation title from the first message and context.
    Matches user expectations (e.g. 'Pantry Priority', 'Apple Storage Advice', 'Banana Browning').
    """
    msg_lower = first_user_message.lower()

    if "eat first" in msg_lower or "which food" in msg_lower or "use first" in msg_lower:
        return "Pantry Priority"
    if "cook today" in msg_lower or "cook tonight" in msg_lower or "what to make" in msg_lower:
        return "Pantry Meal Ideas"
    if "expir" in msg_lower or "attention" in msg_lower:
        return "Expiring Foods"
    if "reduce" in msg_lower and "waste" in msg_lower:
        return "Reduce Food Waste"
    if "brown spot" in msg_lower or "banana" in msg_lower:
        return "Banana Browning"
    if "pantry" in msg_lower or "inventory" in msg_lower or "what food" in msg_lower:
        return "Pantry Overview"

    if food_context and (food_context.get("detectedFood") or food_context.get("foodName")):
        food = (food_context.get("detectedFood") or food_context.get("foodName")).strip().title()
        if "store" in msg_lower or "keep" in msg_lower or "fridge" in msg_lower:
            return f"{food} Storage Advice"
        if "fresh" in msg_lower or "spoil" in msg_lower or "rot" in msg_lower:
            return f"{food} Freshness"
        if "recipe" in msg_lower or "cook" in msg_lower or "eat" in msg_lower:
            return f"{food} Ideas"
        return f"{food} Discussion"

    # Specific storage questions (e.g. "How should I store apples?")
    store_match = re.search(r"how (?:should|to|do) i store (?:this |the |my )?([a-z\s]+)", msg_lower)
    if store_match:
        target = store_match.group(1).replace("?", "").strip().title()
        if target:
            return f"{target} Storage Advice"

    # Fallback to message text summary
    clean = re.sub(r"[^\w\s]", "", first_user_message).strip()
    words = clean.split()
    if not words:
        return "New Food Discussion"

    title_words = words[:4]
    title = " ".join(title_words).title()
    return title[:40]


class FreshoBuddyService:
    """
    Manages conversational interactions with Google Gemini, incorporating
    pantry produce history, produce analysis context, and persistent conversation history.
    """

    _instance: Optional["FreshoBuddyService"] = None

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self.client = None
        self.is_configured = False

        self._init_gemini_client()

    @classmethod
    def get_instance(cls) -> "FreshoBuddyService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_gemini_client(self):
        # Refresh key in case it was updated dynamically in os.environ
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
        if not self.api_key:
            logger.info("GEMINI_API_KEY is not configured in environment. FreshoBuddy running in unconfigured mode.")
            self.is_configured = False
            self.client = None
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.is_configured = True
            logger.info(f"FreshoBuddy initialized with official Google GenAI SDK (Model: {self.model_name})")
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI client: {e}")
            self.is_configured = False
            self.client = None

    def generate_reply(
        self,
        user_message: str,
        user_id: str = "guest",
        history: Optional[List[Dict[str, Any]]] = None,
        analysis_context: Optional[Dict[str, Any]] = None,
        pantry_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Gemini given conversation history, pantry history, and analysis context.
        Ensures deterministic triage for pantry-related questions.
        """
        # Re-check key in case it was added
        if not self.is_configured or not self.client:
            self._init_gemini_client()

        history = history or []
        is_follow_up = _is_conversational_follow_up(user_message, history)
        fresho_intent, context_level, target_food = detect_fresho_intent(
            user_message,
            has_analysis_context=bool(analysis_context),
            is_short_follow_up=is_follow_up,
        )
        if is_follow_up:
            resolved = _resolve_follow_up_food(history)
            if resolved:
                target_food = resolved
                fresho_intent = FreshoIntent.STORAGE_ADVICE
                context_level = ContextLevel.MEDIUM

        intent = map_fresho_intent_to_pantry_intent(fresho_intent)
        is_pantry_query = context_level == ContextLevel.STRONG or (
            context_level == ContextLevel.MEDIUM
            and fresho_intent
            in (
                FreshoIntent.PANTRY_LIST,
                FreshoIntent.STORAGE_ADVICE,
                FreshoIntent.FOOD_WASTE,
            )
        )

        # Always load authoritative pantry state from backend (current remaining days)
        try:
            pantry_items = get_current_pantry_state(user_id)
        except Exception as e:
            logger.warning(f"Could not load pantry items for user {user_id}: {e}")
            pantry_items = pantry_items or []

        triage = triage_pantry_items(pantry_items)

        # Handle empty pantry state for pantry questions
        if is_pantry_query and not triage["hasItems"]:
            empty_msg = (
                "Your pantry history is currently empty, so I can't identify a specific food to prioritize yet. "
                "Analyze and save a food first, and I'll track its freshness and prioritize it for you 🌱"
            )
            return {
                "text": empty_msg,
                "status": "success",
                "model": "deterministic_rule_engine"
            }

        # Step 3: Compute deterministic fallback answer
        deterministic_fallback = build_deterministic_answer(intent, triage, target_food)

        # Structured pantry decisions stay under application control; a
        # generative response must not replace authoritative stored values.
        if intent == PantryIntent.EAT_FIRST:
            return {
                "text": deterministic_fallback,
                "status": "success",
                "model": "deterministic_pantry_triage",
            }

        if is_follow_up and _is_why_follow_up(user_message) and triage["hasItems"]:
            ranked = triage["rankedItems"]
            top = triage["topUrgent"]
            remaining = top.get("remainingDays")
            remaining_text = (
                f"{remaining} days remaining in the saved quality estimate"
                if remaining is not None
                else "no remaining-day estimate in the saved pantry record"
            )
            if triage["isTie"]:
                tied_names = " and ".join(f"**{item['foodName']}**" for item in triage["tiedTop"])
                answer = (
                    f"{tied_names} are tied for the highest calculated urgency "
                    f"({top['tier']}, {remaining_text}). The saved pantry values give them equal priority."
                )
            else:
                answer = (
                    f"**{top['foodName']}** is first because it has the highest calculated urgency "
                    f"({top['tier']}) and {remaining_text}."
                )
                comparison = ranked[1] if len(ranked) > 1 else None
                if comparison:
                    other_remaining = comparison.get("remainingDays")
                    other_text = (
                        f"{other_remaining} days remaining"
                        if other_remaining is not None
                        else "no remaining-day estimate"
                    )
                    answer += (
                        f" **{comparison['foodName']}** has {other_text}, "
                        "so the application ranks it after the first item."
                    )
            return {
                "text": answer,
                "status": "success",
                "model": "deterministic_pantry_triage",
            }

        # If Gemini is not configured, immediately return deterministic answer
        if not self.is_configured or not self.client:
            return {
                "text": deterministic_fallback,
                "status": "deterministic_fallback",
                "model": "rule_engine"
            }

        # Step 4: Build Grounded Context for Gemini
        pantry_context_block = ""
        if triage["hasItems"] and context_level in (ContextLevel.STRONG, ContextLevel.MEDIUM):
            top = triage["topUrgent"]
            ranked = triage["rankedItems"]
            if context_level == ContextLevel.MEDIUM and fresho_intent == FreshoIntent.STORAGE_ADVICE and target_food:
                ranked = [it for it in ranked if target_food.lower() in it["foodName"].lower()] or ranked[:3]
            elif context_level == ContextLevel.MEDIUM:
                ranked = ranked[:5]
            items_summary = []
            for it in ranked:
                rem = it.get("remainingDays")
                rem_txt = (
                    f"{rem} days remaining"
                    if rem is not None
                    else "remaining quality cannot currently be estimated"
                )
                items_summary.append(
                    f"- {it['foodName']}: {it['status']} • {rem_txt} • Priority: {it['tier']} • Storage: {it['storageEnvironment']}"
                )
            
            pantry_context_block = (
                f"\n[USER'S ACTUAL SAVED PANTRY PRODUCE LOG ({triage['totalCount']} items)]\n"
                + "\n".join(items_summary)
                + f"\n\n[APPLICATION DETERMINISTIC TRIAGE CALCULATION]\n"
                + f"- Question Intent: {intent}\n"
                + f"- Calculated Priority Recommendation: {top['foodName']} (Score: {top['urgencyScore']}, Tier: {top['tier']})\n"
                + f"- Remaining Quality Window: {top['remainingDays']} days remaining\n"
                + f"- Is Top Tier Tied: {triage['isTie']} (Tied foods: {[it['foodName'] for it in triage['tiedTop']] if triage['isTie'] else 'None'})\n"
                + f"- Reason: {top['remainingDays']} days remaining ({top['status']})\n"
                + f"\nCRITICAL INSTRUCTION FOR THIS RESPONSE:\n"
            )

            if intent == PantryIntent.SPECIFIC_FOOD_STORAGE and target_food:
                pantry_context_block += (
                    f"- The user is asking how to store **{target_food.title()}**.\n"
                    f"- If {target_food} is in the pantry list above, cite its saved storage environment and remaining days.\n"
                    f"- If {target_food} is NOT in the pantry list above, state that it is not currently logged, and provide expert, practical FoodKeeper storage advice for {target_food.title()}.\n"
                    f"- BOLD important food names and storage instructions in markdown.\n"
                )
            else:
                pantry_context_block += (
                    f"- Ground your answer ONLY in the above saved produce items.\n"
                    f"- DO NOT invent other foods (such as apples, bread, etc.) if they are not in the list.\n"
                    f"- State the application's calculated recommendation clearly.\n"
                    f"- BOLD the key food name and decision in markdown (e.g., **{top['foodName']} should be used first**).\n"
                    f"- If there is a tie, explain the tie clearly.\n"
                    f"- Do NOT output literal unrendered asterisks.\n"
                )

        # Single Food Scan Context (from Analyze Food)
        scan_context_block = ""
        if analysis_context and (analysis_context.get("detectedFood") or analysis_context.get("foodName")):
            food = analysis_context.get("detectedFood") or analysis_context.get("foodName")
            freshness = analysis_context.get("freshness", {})
            f_label = freshness.get("label") if isinstance(freshness, dict) else str(freshness)
            f_conf = freshness.get("confidence") if isinstance(freshness, dict) else None
            shelf_life = analysis_context.get("shelfLife", {})
            rem = shelf_life.get("remaining", {}) if isinstance(shelf_life, dict) else {}
            rem_str = f"{rem.get('minDays', '?')}–{rem.get('maxDays', '?')} days" if rem else "Guidance unavailable"
            storage = analysis_context.get("storageType", "countertop")
            days_stored = analysis_context.get("daysStored", 0)

            scan_context_block = (
                f"\n[CURRENT SCANNED FOOD CONTEXT]\n"
                f"- Food Item: {food}\n"
                f"- Estimated Visible Freshness: {f_label or 'Uncertain'} ({f_conf or 'N/A'}% confidence)\n"
                f"- Estimated Remaining Quality Window: {rem_str}\n"
                f"- Storage Environment: {storage}\n"
                f"- Days Stored So Far: {days_stored} days\n"
            )

        # Assemble Prompt with History
        formatted_contents = []
        if history:
            for msg in history[-8:]:  # Recent turns
                role = "user" if msg.get("role") == "user" else "model"
                text = msg.get("content", "")
                if text:
                    formatted_contents.append(f"{role.upper()}: {text}")

        current_input = f"{pantry_context_block}{scan_context_block}\nUSER: {user_message}\nASSISTANT:"
        formatted_contents.append(current_input)
        full_prompt = "\n\n".join(formatted_contents)

        try:
            from google.genai import types

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=FRESHO_BUDDY_SYSTEM_PROMPT,
                    temperature=0.5,  # Lower temperature for grounded factual consistency
                    max_output_tokens=650,
                )
            )

            reply_text = response.text.strip() if response and response.text else deterministic_fallback
            return {
                "text": reply_text,
                "status": "success",
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}", exc_info=True)
            # Graceful deterministic fallback ensures zero downtime or broken chats
            return {
                "text": deterministic_fallback,
                "status": "fallback",
                "error": str(e),
                "model": "deterministic_rule_engine"
            }


def _is_conversational_follow_up(message: str, history: List[Dict[str, Any]]) -> bool:
    if not history:
        return False
    q = (message or "").lower().strip()
    if len(q.split()) > 8:
        return False
    return any(
        p in q
        for p in (
            "why that one",
            "why that",
            "that one",
            "store it",
            "how should i store it",
            "what about it",
            "tell me more about it",
        )
    ) or q in ("why?", "why", "how?", "how")


def _is_why_follow_up(message: str) -> bool:
    return bool(re.fullmatch(r"\s*(?:why|why\s+is\s+that|why\s+that)\s*[?.!]*\s*", message, re.IGNORECASE))


def _resolve_follow_up_food(history: List[Dict[str, Any]]) -> Optional[str]:
    """Resolve 'that one' / 'it' from the most recent assistant pantry recommendation."""
    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        text = msg.get("content") or ""
        match = re.search(r"\*\*([A-Za-z][A-Za-z\s]{1,30}?)\s+should be used first\*\*", text)
        if match:
            return match.group(1).strip()
        match2 = re.search(r"\*\*([A-Za-z][A-Za-z\s]{1,30}?)\*\*", text)
        if match2:
            return match2.group(1).strip()
    return None


def get_fresho_buddy_service() -> FreshoBuddyService:
    return FreshoBuddyService.get_instance()
