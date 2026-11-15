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
    """Retrieve pantry items, archived/removed produce records, and activity audit logs."""
    try:
        user_id = user["id"]
        items = get_current_pantry_state(user_id)
        archived = chat_db.get_archived_pantry_items(user_id)
        activity_logs = chat_db.list_activity_logs(user_id)
        return {
            "success": True,
            "items": items,
            "archived_items": archived,
            "activity_logs": activity_logs,
            "count": len(items),
            "archived_count": len(archived),
            "activity_count": len(activity_logs),
            "total_tracked": len(items) + len(archived),
        }
    except Exception as e:
        logger.error(f"Error fetching pantry history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pantry history."
        )


@router.get("/archived")
def get_archived_history(user: dict = Depends(get_current_user)):
    """Retrieve produce records removed or archived from pantry."""
    try:
        user_id = user["id"]
        archived = chat_db.get_archived_pantry_items(user_id)
        return {"success": True, "items": archived, "count": len(archived)}
    except Exception as e:
        logger.error(f"Error fetching archived history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve archived history."
        )


@router.get("/activity-logs")
def get_activity_logs(user: dict = Depends(get_current_user)):
    """Retrieve chronological audit trail of all project food activities."""
    try:
        user_id = user["id"]
        logs = chat_db.list_activity_logs(user_id)
        return {"success": True, "logs": logs, "count": len(logs)}
    except Exception as e:
        logger.error(f"Error fetching activity logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity logs."
        )


@router.get("/pantry")
def get_pantry_alias(user: dict = Depends(get_current_user)):
    """Alias for current active pantry state."""
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
def delete_pantry_item(
    item_id: str,
    action: str = "removed",
    reason: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    Remove an item from active pantry.
    Archives it in pantry history and logs the activity so it is never lost.
    """
    user_id = user["id"]
    clean_action = str(action).lower().strip() if action else "removed"

    # If action is consumed or wasted, also trigger impact logging
    if clean_action in {"consumed", "wasted"}:
        from backend.app.services.analytics_service import record_user_food_action
        try:
            record_user_food_action(
                user_id=user_id,
                food_name="",
                action=clean_action,
                pantry_item_id=item_id,
                reason=reason,
            )
            return {"success": True, "message": f"Pantry item recorded as {clean_action} and archived."}
        except Exception as e:
            logger.warning(f"Error recording impact action on delete: {e}")

    deleted = chat_db.delete_pantry_item(item_id=item_id, user_id=user_id, action=clean_action, reason=reason)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found or unauthorized."
        )
    return {"success": True, "message": "Pantry item archived in history logs."}


@router.post("/{item_id}/restore")
def restore_pantry_item(item_id: str, user: dict = Depends(get_current_user)):
    """Restore an archived item back to active pantry."""
    restored = chat_db.restore_pantry_item(item_id=item_id, user_id=user["id"])
    if not restored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found or unauthorized."
        )
    return {"success": True, "message": "Pantry item restored to active pantry."}


@router.delete("/{item_id}/permanent")
def permanently_delete_pantry_item(item_id: str, user: dict = Depends(get_current_user)):
    """Permanently delete an item from the database."""
    deleted = chat_db.permanently_delete_pantry_item(item_id=item_id, user_id=user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found or unauthorized."
        )
    return {"success": True, "message": "Pantry item permanently purged."}


@router.delete("")
def clear_all_pantry_items(user: dict = Depends(get_current_user)):
    """Clear all pantry history items for testing 0-item state."""
    chat_db.clear_pantry_items(user_id=user["id"])
    return {"success": True, "message": "All pantry items cleared."}
