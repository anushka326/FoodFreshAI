"""
FoodFresh AI — Smart Notifications & Expiry Alerts Routes
FastAPI endpoints for retrieving and managing user pantry notifications.
Strictly isolated by user_id and dynamically evaluated from actual pantry records.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.database import chat_db
from backend.app.deps.auth import get_current_user
from backend.app.services.notification_service import generate_user_notifications

logger = logging.getLogger("foodfresh.routes.notifications")

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class MarkReadAllRequest(BaseModel):
    notification_ids: Optional[List[str]] = Field(default=None, description="Optional specific list of notification IDs to mark read")


@router.get("")
def get_user_notifications(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve live notifications and expiry alerts for the authenticated user's pantry.
    Automatically identifies expiring soon, expiring today, expired, and high-priority items.
    """
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view notifications.",
        )

    try:
        data = generate_user_notifications(user_id)
        return {
            "success": True,
            **data,
        }
    except Exception as exc:
        logger.error("Failed to generate notifications for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate pantry notifications.",
        ) from exc


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Mark a specific notification as read."""
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    chat_db.mark_notification_read(user_id, notification_id)
    return {
        "success": True,
        "notificationId": notification_id,
        "isRead": True,
    }


@router.post("/{notification_id}/unread")
def mark_as_unread(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Mark a specific notification back as unread."""
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    chat_db.mark_notification_unread(user_id, notification_id)
    return {
        "success": True,
        "notificationId": notification_id,
        "isRead": False,
    }


@router.post("/read-all")
def mark_all_as_read(
    payload: Optional[MarkReadAllRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Mark all current notifications for the user as read."""
    user_id: str = current_user.get("user_id") or current_user.get("id") or ""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    # If specific notification IDs provided in request payload, use them
    target_ids = payload.notification_ids if payload and payload.notification_ids else None

    # Otherwise, resolve all active notification IDs for this user
    if not target_ids:
        active_data = generate_user_notifications(user_id)
        target_ids = [n["id"] for n in active_data.get("notifications", [])]

    chat_db.mark_all_notifications_read(user_id, target_ids)
    return {
        "success": True,
        "markedCount": len(target_ids),
        "notificationIds": target_ids,
    }
