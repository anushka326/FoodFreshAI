"""
FoodFresh AI — Backend authentication (SQLite users + session tokens).
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from backend.app.database import chat_db

logger = logging.getLogger("foodfresh.auth")

SESSION_TTL_DAYS = 30
PBKDF2_ITERATIONS = 120_000


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return digest.hex()


def register_user(
    email: str,
    password: str,
    full_name: str,
    household_type: Optional[str] = None,
) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise ValueError("Please enter a valid email address.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if not full_name or not full_name.strip():
        raise ValueError("Please enter your full name.")

    if chat_db.get_user_by_email(clean_email):
        raise ValueError("An account with this email already exists.")

    user_id = f"usr_{uuid.uuid4().hex[:16]}"
    salt = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt)
    user = chat_db.create_user(
        user_id=user_id,
        email=clean_email,
        password_hash=f"{salt}${pwd_hash}",
        full_name=full_name.strip(),
        household_type=household_type,
    )
    token = chat_db.create_session(user_id)
    return {"user": user, "token": token}


def login_user(email: str, password: str) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    if not clean_email or not password:
        raise ValueError("Please enter both email and password.")

    record = chat_db.get_user_by_email(clean_email)
    if not record:
        raise ValueError("Invalid email or password.")

    stored = record.get("passwordHash") or ""
    if "$" not in stored:
        raise ValueError("Invalid email or password.")
    salt, expected = stored.split("$", 1)
    if hash_password(password, salt) != expected:
        raise ValueError("Invalid email or password.")

    token = chat_db.create_session(record["id"])
    user = chat_db.user_record_to_public(record)
    return {"user": user, "token": token}


def resolve_session(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token or not str(token).strip():
        return None
    session = chat_db.get_session(str(token).strip())
    if not session:
        return None
    user = chat_db.get_user_by_id(session["userId"])
    if not user:
        return None
    return chat_db.user_record_to_public(user)


def logout_user(token: Optional[str]) -> bool:
    if not token:
        return False
    return chat_db.delete_session(str(token).strip())
