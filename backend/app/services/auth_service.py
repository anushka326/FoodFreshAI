"""
FoodFresh AI — Backend authentication (SQLite users + session tokens).
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import sqlite3
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
    try:
        user = chat_db.create_user(
            user_id=user_id,
            email=clean_email,
            password_hash=f"{salt}${pwd_hash}",
            full_name=full_name.strip(),
            household_type=household_type,
        )
    except sqlite3.IntegrityError as e:
        logger.warning(f"Integrity error during registration for {clean_email}: {e}")
        raise ValueError("An account with this email already exists.")

    token = chat_db.create_session(user_id)
    return {"user": user, "token": token}


def _verify_legacy_hash(plain_password: str, stored_hash: str) -> bool:
    """Verify password against legacy formats (ad4fc0b 96-char PBKDF2 or BCrypt)."""
    if not stored_hash:
        return False

    # 1. Legacy ad4fc0b PBKDF2 (96 hex chars: 32 chars salt + 64 chars dk, 100,000 iterations)
    if len(stored_hash) == 96 and "$" not in stored_hash:
        try:
            salt_hex = stored_hash[:32]
            salt = bytes.fromhex(salt_hex)
            dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000)
            expected = salt.hex() + dk.hex()
            return secrets.compare_digest(expected, stored_hash)
        except Exception:
            pass

    # 2. Legacy BCrypt format ($2a$, $2b$, $2y$)
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ImportError:
            try:
                from passlib.context import CryptContext
                return CryptContext(schemes=["bcrypt"]).verify(plain_password, stored_hash)
            except ImportError:
                logger.warning("BCrypt password detected but neither bcrypt nor passlib is installed.")
                return False
    return False


def login_user(email: str, password: str) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    if not clean_email or not password:
        raise ValueError("Please enter both email and password.")

    record = chat_db.get_user_by_email(clean_email)
    if not record:
        raise ValueError("Invalid email or password.")

    stored = record.get("passwordHash") or ""
    is_valid = False
    needs_upgrade = False

    if "$" in stored and not stored.startswith(("$2a$", "$2b$", "$2y$")):
        salt, expected = stored.split("$", 1)
        is_valid = secrets.compare_digest(hash_password(password, salt), expected)
    else:
        is_valid = _verify_legacy_hash(password, stored)
        if is_valid:
            needs_upgrade = True

    if not is_valid:
        raise ValueError("Invalid email or password.")

    # Seamlessly upgrade legacy hash to the new secure standard upon successful login
    if needs_upgrade:
        try:
            new_salt = secrets.token_hex(16)
            new_hash = f"{new_salt}${hash_password(password, new_salt)}"
            chat_db.update_user_password(record["id"], new_hash)
            logger.info(f"Successfully upgraded legacy password hash for user {clean_email}")
        except Exception as e:
            logger.warning(f"Could not auto-upgrade legacy password hash for {clean_email}: {e}")

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


def update_profile(
    user_id: str,
    full_name: Optional[str] = None,
    avatar: Optional[str] = None,
) -> Dict[str, Any]:
    """Update authenticated user profile (display name or themed avatar)."""
    updated = chat_db.update_user_profile(user_id=user_id, full_name=full_name, avatar=avatar)
    if not updated:
        raise ValueError("User not found or update failed.")
    return updated
