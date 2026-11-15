"""
FoodFresh AI — Food-Waste Impact Analytics Routes
FastAPI endpoints for retrieving and recording user-specific food waste metrics.
Strictly isolated by user_id and based entirely on actual recorded user actions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.database import chat_db
from backend.app.deps.auth import get_current_user
from backend.app.services.analytics_service import (
    get_user_analytics,
    record_user_food_action,
)

logger = logging.getLogger("foodfresh.routes.analytics")

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class RecordFoodActionRequest(BaseModel):
    food_name: str = Field(..., description="Name of the food item")
    action: str = Field(..., description="'consumed' or 'wasted'")
    pantry_item_id: Optional[str] = Field(default=None, description="ID of the pantry record if recorded from active pantry")
    cultivar: Optional[str] = Field(default=None, description="Cultivar or variety")
    reason: Optional[str] = Field(default=None, description="Optional note on consumption or waste reason")


@router.get("")
def get_analytics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve real-time food-waste impact analytics for the authenticated user.
    Includes total consumed, total wasted, waste %, food saved count, and monthly trends.
    """
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view analytics.",
        )

    try:
        data = get_user_analytics(user_id)
        return {
            "success": True,
            **data,
        }
    except Exception as exc:
        logger.error("Failed to calculate analytics for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve food-waste analytics.",
        ) from exc


@router.post("/action")
def log_food_action(
    req: RecordFoodActionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Record an actual user action: food was consumed or wasted.
    Updates impact analytics and removes item from active pantry stock if pantry_item_id is provided.
    """
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to record food outcome.",
        )

    clean_action = req.action.strip().lower()
    if clean_action not in {"consumed", "wasted"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be either 'consumed' or 'wasted'.",
        )

    try:
        log = record_user_food_action(
            user_id=user_id,
            food_name=req.food_name.strip(),
            action=clean_action,
            pantry_item_id=req.pantry_item_id,
            cultivar=req.cultivar,
            reason=req.reason,
        )
        return {
            "success": True,
            "log": log,
            "message": f"Successfully recorded {req.food_name} as {clean_action}.",
        }
    except Exception as exc:
        logger.error("Failed to record food action for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record food action.",
        ) from exc


@router.delete("/action/{log_id}")
def delete_action(
    log_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a recorded food impact log (e.g. undo action)."""
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    deleted = chat_db.delete_food_impact_log(user_id, log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impact log not found or unauthorized.",
        )
    return {
        "success": True,
        "message": "Impact log removed.",
    }

