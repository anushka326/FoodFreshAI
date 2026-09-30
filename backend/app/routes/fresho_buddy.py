"""
FoodFresh AI - FreshoBuddy API Routes
Endpoints for conversational food companion guidance, database-backed message persistence,
and strict multi-user conversation isolation.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.database import chat_db
from backend.app.deps.auth import get_current_user
from backend.app.services.fresho_buddy_service import derive_conversation_title, get_fresho_buddy_service

logger = logging.getLogger("foodfresh.routes.fresho_buddy")

router = APIRouter(prefix="/api/fresho-buddy", tags=["fresho-buddy"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = Field(default="New Food Discussion", description="Title for the conversation")


class ChatMessageRequest(BaseModel):
    conversationId: Optional[str] = Field(default=None, description="ID of existing conversation or None to start new")
    message: str = Field(..., min_length=1, description="User's query or message")
    analysisContext: Optional[Dict[str, Any]] = Field(default=None, description="Structured food analysis context")


@router.get("/conversations")
def get_user_conversations(user: dict = Depends(get_current_user)):
    """List all saved conversations belonging to the user."""
    try:
        conversations = chat_db.list_conversations(user_id=user["id"])
        return {"success": True, "conversations": conversations}
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation list.",
        )


@router.post("/conversations")
def create_new_conversation(req: CreateConversationRequest, user: dict = Depends(get_current_user)):
    """Create a new conversation session."""
    try:
        conv = chat_db.create_conversation(user_id=user["id"], title=req.title or "New Food Discussion")
        return {"success": True, "conversation": conv}
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation.",
        )


@router.get("/conversations/{conversation_id}")
def get_conversation_history(conversation_id: str, user: dict = Depends(get_current_user)):
    """Load complete message history for a specific conversation."""
    conv = chat_db.get_conversation(conversation_id=conversation_id, user_id=user["id"])
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )
    return {"success": True, "conversation": conv}


@router.delete("/conversations/{conversation_id}")
def delete_conversation_by_id(conversation_id: str, user: dict = Depends(get_current_user)):
    """Delete a conversation belonging to the user."""
    deleted = chat_db.delete_conversation(conversation_id=conversation_id, user_id=user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or could not be deleted.",
        )
    return {"success": True, "message": "Conversation deleted."}


@router.post("/chat")
def chat_with_fresho_buddy(req: ChatMessageRequest, user: dict = Depends(get_current_user)):
    """
    Send a message to FreshoBuddy with structured food context.
    Persists user message and assistant reply into the conversation database.
    """
    user_id = user["id"]
    conv_id = req.conversationId

    conv = None
    if conv_id:
        conv = chat_db.get_conversation(conversation_id=conv_id, user_id=user_id)

    if not conv:
        title = derive_conversation_title(req.message, req.analysisContext)
        conv = chat_db.create_conversation(user_id=user_id, title=title)
        conv_id = conv["conversationId"]
    elif conv.get("title") == "New Food Discussion":
        new_title = derive_conversation_title(req.message, req.analysisContext)
        chat_db.update_conversation_title(conversation_id=conv_id, user_id=user_id, title=new_title)
        conv["title"] = new_title

    user_msg_record = chat_db.add_message(
        conversation_id=conv_id,
        user_id=user_id,
        role="user",
        content=req.message,
        analysis_context=req.analysisContext,
    )

    fresho_service = get_fresho_buddy_service()
    existing_messages = conv.get("messages", [])
    reply_dict = fresho_service.generate_reply(
        user_message=req.message,
        user_id=user_id,
        history=existing_messages,
        analysis_context=req.analysisContext,
        pantry_items=None,
    )

    bot_msg_record = chat_db.add_message(
        conversation_id=conv_id,
        user_id=user_id,
        role="assistant",
        content=reply_dict["text"],
        analysis_context=req.analysisContext,
    )

    return {
        "success": True,
        "conversationId": conv_id,
        "title": conv.get("title"),
        "userMessage": user_msg_record,
        "reply": {
            "id": bot_msg_record["messageId"],
            "sender": "bot",
            "text": reply_dict["text"],
            "status": reply_dict.get("status", "success"),
            "model": reply_dict.get("model"),
            "timestamp": bot_msg_record["createdAt"],
        },
    }
