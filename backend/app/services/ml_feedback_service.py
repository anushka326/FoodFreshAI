"""
ML feedback collection — COLLECTED → VALIDATED → TRAINING_READY → USED_FOR_TRAINING.
Does not trigger automatic training.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.database import chat_db

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FEEDBACK_IMAGE_DIR = PROJECT_ROOT / "data" / "feedback" / "images"
MANIFEST_PATH = PROJECT_ROOT / "data" / "feedback" / "manifest.csv"

VALID_STATUSES = frozenset(
    {"COLLECTED", "VALIDATED", "TRAINING_READY", "USED_FOR_TRAINING", "REJECTED"}
)


def save_feedback_image_bytes(user_id: str, analysis_id: str, image_bytes: bytes, ext: str = "jpg") -> str:
    FEEDBACK_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = (analysis_id or uuid.uuid4().hex[:12]).replace("/", "_")
    rel = Path("data") / "feedback" / "images" / f"{user_id}_{safe_id}.{ext}"
    path = PROJECT_ROOT / rel
    path.write_bytes(image_bytes)
    return str(rel).replace("\\", "/")


def create_feedback_record(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return chat_db.insert_ml_feedback(user_id=user_id, payload=payload)


def list_feedback_for_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    return chat_db.list_ml_feedback(user_id=user_id, limit=limit)
