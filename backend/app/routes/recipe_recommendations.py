"""
FoodFresh AI — Recipe Recommendation Routes
Provides pantry-aware recipe recommendations based on the user's current pantry state.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.deps.auth import get_current_user
from backend.app.services.pantry_state_service import get_current_pantry_state
from backend.app.services.recipe_recommendation_service import (
    RECIPE_DATABASE,
    generate_recipe_recommendations,
)

logger = logging.getLogger("foodfresh.recipe_recommendations")

router = APIRouter(prefix="/api/recipes", tags=["recipe-recommendations"])


@router.get("/recommendations")
def get_recommendations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Return pantry-aware recipe recommendations for the authenticated user.

    Groups recipes into:
    - **use_soon**: recipes that use items expiring within 3 days
    - **best_match**: recipes with the highest ingredient overlap
    - **quick**: recipes ready in under 15 minutes
    """
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view pantry recipes.",
        )

    try:
        pantry_items = get_current_pantry_state(user_id)
    except Exception as exc:
        logger.error("Failed to load pantry state for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load pantry items. Please try again.",
        ) from exc

    try:
        recommendations = generate_recipe_recommendations(pantry_items)
    except Exception as exc:
        logger.error("Recipe recommendation generation failed for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate recipe recommendations. Please try again.",
        ) from exc

    return {
        "success": True,
        "recommendations": recommendations,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/recommendations/{recipe_id}")
def get_recipe_detail(
    recipe_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Return full details for a single recipe by its id.
    Also includes live availability info based on the user's current pantry.
    """
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view pantry recipes.",
        )

    # Locate the recipe in the static database
    recipe = next((r for r in RECIPE_DATABASE if r["id"] == recipe_id), None)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe '{recipe_id}' not found.",
        )

    # Enrich with live pantry availability
    try:
        pantry_items = get_current_pantry_state(user_id)
        recs = generate_recipe_recommendations(pantry_items)
        # Look for this recipe in the matched results (may not appear if score < 30 %)
        enriched = next((r for r in recs["all"] if r["id"] == recipe_id), None)
    except Exception as exc:
        logger.warning("Could not enrich recipe %s with pantry data: %s", recipe_id, exc)
        enriched = None

    if enriched:
        return {"success": True, "recipe": enriched}

    # Recipe exists but didn't pass the match threshold — return static data with empty availability
    return {
        "success": True,
        "recipe": {
            "id": recipe["id"],
            "name": recipe["name"],
            "category": recipe["category"],
            "cuisine": recipe.get("cuisine", "Global"),
            "prep_time_minutes": recipe["prep_time_minutes"],
            "steps": recipe["steps"],
            "required_ingredients": recipe["required_ingredients"],
            "available_ingredients": [],
            "missing_ingredients": recipe["required_ingredients"],
            "match_score": 0,
            "reason": "None of these ingredients are currently in your pantry.",
            "image_emoji": recipe["image_emoji"],
            "youtube_url": recipe.get("youtube_url", ""),
            "expiry_urgency": False,
        },
    }
