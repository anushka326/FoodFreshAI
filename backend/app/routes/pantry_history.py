"""
FoodFresh AI - Pantry Produce History Routes
REST endpoints for managing saved food analysis records with strict user isolation,
synchronized with the SQLite database.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.database import chat_db
from backend.app.deps.auth import get_current_user
from backend.app.services.pantry_state_service import get_current_pantry_state

logger = logging.getLogger("foodfresh.routes.pantry_history")

router = APIRouter(prefix="/api/history", tags=["pantry-history"])


class SaveHistoryItemRequest(BaseModel):
    item: Dict[str, Any] = Field(..., description="Food analysis record to save")


@router.get("")
def get_user_pantry_history(user: dict = Depends(get_current_user)):
    """Retrieve pantry with server-calculated remaining quality (UTC)."""
    try:
        user_id = user["id"]
        items = get_current_pantry_state(user_id)
        return {"success": True, "items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Error fetching pantry history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pantry history."
        )


@router.get("/pantry")
def get_pantry_alias(user: dict = Depends(get_current_user)):
    """Alias for current pantry state."""
    return get_user_pantry_history(user)


@router.post("")
def save_pantry_item(req: SaveHistoryItemRequest, user: dict = Depends(get_current_user)):
    """Save an analyzed food item into the user's pantry history."""
    try:
        saved = chat_db.add_pantry_item(user_id=user["id"], item=req.item)
        return {"success": True, "item": saved}
    except Exception as e:
        logger.error(f"Error saving pantry item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save pantry item."
        )


@router.delete("/{item_id}")
def delete_pantry_item(item_id: str, user: dict = Depends(get_current_user)):
    """Delete a specific pantry history item."""
    deleted = chat_db.delete_pantry_item(item_id=item_id, user_id=user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found or unauthorized."
        )
    return {"success": True, "message": "Pantry item removed."}


@router.delete("")
def clear_all_pantry_items(user: dict = Depends(get_current_user)):
    """Clear all pantry history items for testing 0-item state."""
    chat_db.clear_pantry_items(user_id=user["id"])
    return {"success": True, "message": "All pantry items cleared."}
