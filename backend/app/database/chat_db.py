"""
FoodFresh AI - FreshoBuddy Persistent Chat Database
SQLite implementation providing persistent conversation and message storage with strict user isolation.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "fresho_buddy.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize database tables and indexes."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_user 
            ON conversations(user_id, updated_at DESC);

            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis_context TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conv 
            ON messages(conversation_id, created_at ASC);

            CREATE TABLE IF NOT EXISTS pantry_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                food_name TEXT NOT NULL,
                cultivar TEXT,
                status TEXT NOT NULL,
                status_category TEXT,
                quality_score INTEGER DEFAULT 80,
                quality_period TEXT,
                remaining_days INTEGER,
                storage_environment TEXT,
                storage_type TEXT,
                eat_first_priority TEXT,
                eat_first_score INTEGER,
                eat_first_reason TEXT,
                guidance TEXT,
                image_src TEXT,
                raw_metadata TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_pantry_user 
            ON pantry_history(user_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS pantry_meta (
                user_id TEXT PRIMARY KEY,
                has_seeded INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                household_type TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auth_sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_auth_sessions_user
            ON auth_sessions(user_id, expires_at DESC);
        """)
        conn.commit()
        _migrate_schema(conn)


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Schema extensions for real-time pantry countdown (documented migration).
    Adds: analysis_id, added_at, estimated_quality_days, estimated_end_at,
          freshness_state, freshness_confidence, updated_at
    """
    pantry_columns = [
        ("analysis_id", "TEXT"),
        ("added_at", "TEXT"),
        ("estimated_quality_days", "INTEGER"),
        ("estimated_end_at", "TEXT"),
        ("freshness_state", "TEXT"),
        ("freshness_confidence", "REAL"),
        ("updated_at", "TEXT"),
        ("days_stored_at_analysis", "INTEGER"),
        ("reference_min_days", "INTEGER"),
        ("reference_max_days", "INTEGER"),
        ("food_form", "TEXT"),
        ("legacy_timing", "INTEGER DEFAULT 0"),
        ("food_model_version", "TEXT"),
        ("freshness_model_version", "TEXT"),
        ("shelf_life_model_version", "TEXT"),
    ]
    for col, col_type in pantry_columns:
        if not _column_exists(conn, "pantry_history", col):
            conn.execute(f"ALTER TABLE pantry_history ADD COLUMN {col} {col_type}")

    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='ml_feedback'"
    )
    if not cur.fetchone():
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS ml_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                analysis_id TEXT,
                image_path TEXT,
                predicted_food TEXT,
                predicted_food_confidence REAL,
                predicted_food_form TEXT,
                predicted_freshness TEXT,
                predicted_freshness_confidence REAL,
                predicted_shelf_life TEXT,
                user_corrected_food TEXT,
                user_corrected_food_form TEXT,
                user_corrected_freshness TEXT,
                user_corrected_shelf_life TEXT,
                storage_type TEXT,
                days_stored INTEGER,
                feedback_source TEXT DEFAULT 'user',
                review_status TEXT DEFAULT 'COLLECTED',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_ml_feedback_user ON ml_feedback(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_ml_feedback_status ON ml_feedback(review_status);
        """)

    # Backfill added_at from created_at for legacy rows
    conn.execute(
        """
        UPDATE pantry_history
        SET added_at = created_at
        WHERE added_at IS NULL AND created_at IS NOT NULL
        """
    )
    # Backfill estimated_quality_days from legacy remaining_days snapshot
    conn.execute(
        """
        UPDATE pantry_history
        SET estimated_quality_days = remaining_days,
            legacy_timing = 1
        WHERE estimated_quality_days IS NULL AND remaining_days IS NOT NULL
        """
    )
    conn.commit()


# Run table initialization on import
init_db()


def create_conversation(user_id: str, title: str = "New Food Discussion", conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new conversation belonging to the specified user."""
    conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_title = (title or "New Food Discussion").strip()[:60]

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations (conversation_id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conv_id, user_id, clean_title, now_iso, now_iso)
        )
        conn.commit()

    return {
        "conversationId": conv_id,
        "userId": user_id,
        "title": clean_title,
        "createdAt": now_iso,
        "updatedAt": now_iso,
        "messages": []
    }


def list_conversations(user_id: str) -> List[Dict[str, Any]]:
    """List all conversations for a user, sorted newest first."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT conversation_id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

    return [
        {
            "conversationId": r["conversation_id"],
            "userId": r["user_id"],
            "title": r["title"],
            "createdAt": r["created_at"],
            "updatedAt": r["updated_at"]
        }
        for r in rows
    ]


def get_conversation(conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full conversation with its messages, ensuring strict user isolation."""
    with get_db_connection() as conn:
        conv_cur = conn.execute(
            """
            SELECT conversation_id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE conversation_id = ? AND user_id = ?
            """,
            (conversation_id, user_id)
        )
        conv = conv_cur.fetchone()
        if not conv:
            return None

        msg_cur = conn.execute(
            """
            SELECT message_id, conversation_id, role, content, analysis_context, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,)
        )
        msg_rows = msg_cur.fetchall()

    messages = []
    for m in msg_rows:
        ctx = None
        if m["analysis_context"]:
            try:
                ctx = json.loads(m["analysis_context"])
            except Exception:
                ctx = None
        messages.append({
            "messageId": m["message_id"],
            "conversationId": m["conversation_id"],
            "role": m["role"],
            "content": m["content"],
            "analysisContext": ctx,
            "createdAt": m["created_at"]
        })

    return {
        "conversationId": conv["conversation_id"],
        "userId": conv["user_id"],
        "title": conv["title"],
        "createdAt": conv["created_at"],
        "updatedAt": conv["updated_at"],
        "messages": messages
    }


def add_message(
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
    analysis_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Add a message to a conversation and bump its updated_at timestamp."""
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    ctx_json = json.dumps(analysis_context) if analysis_context else None

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (message_id, conversation_id, user_id, role, content, analysis_context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (msg_id, conversation_id, user_id, role, content, ctx_json, now_iso)
        )
        conn.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ? AND user_id = ?
            """,
            (now_iso, conversation_id, user_id)
        )
        conn.commit()

    return {
        "messageId": msg_id,
        "conversationId": conversation_id,
        "role": role,
        "content": content,
        "analysisContext": analysis_context,
        "createdAt": now_iso
    }


def update_conversation_title(conversation_id: str, user_id: str, title: str) -> bool:
    """Update conversation title."""
    clean_title = (title or "Food Discussion").strip()[:60]
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE conversation_id = ? AND user_id = ?
            """,
            (clean_title, now_iso, conversation_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """Delete a conversation and its messages."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM conversations
            WHERE conversation_id = ? AND user_id = ?
            """,
            (conversation_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0


# ==============================================================================
# AUTH USERS / SESSIONS
# ==============================================================================

def create_user(
    user_id: str,
    email: str,
    password_hash: str,
    full_name: str,
    household_type: Optional[str] = None,
) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, email, password_hash, full_name, household_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, password_hash, full_name, household_type, now_iso),
        )
        conn.commit()
    return user_record_to_public(
        {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "household_type": household_type,
            "created_at": now_iso,
        }
    )


def user_record_to_public(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("user_id") or record.get("id"),
        "email": record.get("email"),
        "fullName": record.get("full_name") or record.get("fullName"),
        "householdType": record.get("household_type") or record.get("householdType"),
        "avatarUrl": None,
        "status": "Pantry Guard Active",
        "temperatureUnit": "C",
        "remindersEnabled": True,
        "eatFirstRoadmapEnabled": True,
        "freshoBuddyEnabled": True,
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, email, password_hash, full_name, household_type, created_at FROM users WHERE email = ?",
            (email.strip().lower(),),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row["user_id"],
        "email": row["email"],
        "passwordHash": row["password_hash"],
        "full_name": row["full_name"],
        "household_type": row["household_type"],
        "created_at": row["created_at"],
    }


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, email, password_hash, full_name, household_type, created_at FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row["user_id"],
        "email": row["email"],
        "passwordHash": row["password_hash"],
        "full_name": row["full_name"],
        "household_type": row["household_type"],
        "created_at": row["created_at"],
    }


def create_session(user_id: str, ttl_days: int = 30) -> str:
    token = f"sess_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=ttl_days)
    now_iso = now.isoformat()
    exp_iso = expires.isoformat()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO auth_sessions (token, user_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, user_id, exp_iso, now_iso),
        )
        conn.commit()
    return token


def get_session(token: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT token, user_id, expires_at FROM auth_sessions WHERE token = ?",
            (token,),
        )
        row = cur.fetchone()
    if not row:
        return None
    exp = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc):
        delete_session(token)
        return None
    return {"token": row["token"], "userId": row["user_id"], "expiresAt": row["expires_at"]}


def delete_session(token: str) -> bool:
    with get_db_connection() as conn:
        cur = conn.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
        conn.commit()
        return cur.rowcount > 0


# ==============================================================================
# PANTRY PRODUCE LOG / HISTORY STORAGE
# ==============================================================================


def _format_pantry_row(row: sqlite3.Row) -> Dict[str, Any]:
    raw_meta = {}
    if row["raw_metadata"]:
        try:
            raw_meta = json.loads(row["raw_metadata"])
        except Exception:
            pass

    keys = row.keys()
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "analysisId": row["analysis_id"] if "analysis_id" in keys else None,
        "foodName": row["food_name"],
        "cultivar": row["cultivar"] or f"{row['food_name']} • Fresh Harvest",
        "status": row["status"],
        "statusCategory": row["status_category"] or "fresh",
        "qualityScore": row["quality_score"],
        "qualityPeriod": row["quality_period"],
        "remainingDays": row["remaining_days"],
        "storageEnvironment": row["storage_environment"] or "Countertop Ambient",
        "storageType": row["storage_type"] or "countertop",
        "eatFirstPriority": row["eat_first_priority"] or "NORMAL",
        "eatFirstScore": row["eat_first_score"],
        "eatFirstReason": row["eat_first_reason"],
        "guidance": row["guidance"] or "Store in optimal pantry conditions.",
        "imageSrc": row["image_src"] or "/src/assets/food/cutting-board-sourdough.jpg",
        "analyzedTime": row["created_at"],
        "analyzedAt": row["created_at"],
        "addedAt": row["added_at"] if "added_at" in keys else row["created_at"],
        "estimatedQualityDays": row["estimated_quality_days"] if "estimated_quality_days" in keys else None,
        "estimatedEndAt": row["estimated_end_at"] if "estimated_end_at" in keys else None,
        "freshnessState": row["freshness_state"] if "freshness_state" in keys else row["status"],
        "freshnessConfidence": row["freshness_confidence"] if "freshness_confidence" in keys else None,
        "updatedAt": row["updated_at"] if "updated_at" in keys else row["created_at"],
        "daysStoredAtAnalysis": row["days_stored_at_analysis"] if "days_stored_at_analysis" in keys else None,
        "referenceMinDays": row["reference_min_days"] if "reference_min_days" in keys else None,
        "referenceMaxDays": row["reference_max_days"] if "reference_max_days" in keys else None,
        "foodForm": row["food_form"] if "food_form" in keys else "unknown",
        "legacyTiming": bool(row["legacy_timing"]) if "legacy_timing" in keys and row["legacy_timing"] else False,
        "foodModelVersion": row["food_model_version"] if "food_model_version" in keys else None,
        "freshnessModelVersion": row["freshness_model_version"] if "freshness_model_version" in keys else None,
        "shelfLifeModelVersion": row["shelf_life_model_version"] if "shelf_life_model_version" in keys else None,
        "metadata": raw_meta,
    }


def get_pantry_items_raw(user_id: str) -> List[Dict[str, Any]]:
    """Load pantry rows without dynamic enrichment (used by pantry_state_service)."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM pantry_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        return [_format_pantry_row(r) for r in rows]


def get_pantry_items(user_id: str, allow_seed: bool = False) -> List[Dict[str, Any]]:
    """Retrieve pantry items with server-side remaining quality calculation."""
    from backend.app.services.pantry_state_service import get_current_pantry_state

    _ = allow_seed  # seeding removed from production path
    return get_current_pantry_state(user_id)


def add_pantry_item(user_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new analyzed food record to user's pantry history."""
    from backend.app.services.pantry_state_service import (
        compute_estimated_end_at,
        extract_initial_quality_days_from_save_payload,
        get_current_pantry_state,
        quality_period_label,
        utc_now,
    )

    item_id = item.get("id") or f"pantry_{uuid.uuid4().hex[:12]}"
    analysis_id = item.get("analysisId") or item.get("id")
    food_name = item.get("foodName") or item.get("detectedFood") or "Produce"
    cultivar = item.get("cultivar") or f"{food_name} • Fresh Harvest"
    freshness = item.get("freshness") if isinstance(item.get("freshness"), dict) else {}
    status_label = item.get("status") or freshness.get("label") or "Fresh"
    freshness_state = item.get("freshnessState") or freshness.get("label") or status_label
    status_category = item.get("statusCategory") or (
        "fresh"
        if "fresh" in str(status_label).lower()
        else "semi"
        if "slightly" in str(status_label).lower()
        else "attention"
    )
    quality_score = item.get("qualityScore") or 80
    freshness_confidence = item.get("freshnessConfidence")
    if freshness_confidence is None and freshness.get("confidence") is not None:
        freshness_confidence = float(freshness["confidence"])
    elif freshness_confidence is None and freshness.get("score") is not None:
        freshness_confidence = float(freshness["score"])

    est_quality_days = extract_initial_quality_days_from_save_payload(item)
    added_at_dt = utc_now()
    added_at_iso = added_at_dt.isoformat()
    analysis_at_iso = item.get("analyzedAt") or added_at_iso
    estimated_end_iso = None
    if est_quality_days is not None:
        estimated_end_iso = compute_estimated_end_at(added_at_dt, est_quality_days).isoformat()

    quality_period = item.get("qualityPeriod") or quality_period_label(est_quality_days)

    storage_env = item.get("storageEnvironment") or item.get("storageSuggestion") or "Countertop Ambient"
    storage_type = item.get("storageType") or (
        "fridge" if "fridge" in storage_env.lower() or "crisper" in storage_env.lower() else "countertop"
    )

    ef = item.get("eatFirstPriority")
    ef_priority = ef.get("priority") if isinstance(ef, dict) else ef or "NORMAL"
    ef_score = ef.get("score") if isinstance(ef, dict) else item.get("eatFirstScore") or 1
    ef_reason = ef.get("reason") if isinstance(ef, dict) else item.get("eatFirstReason") or ""

    guidance = item.get("guidance") or "Store in optimal conditions."
    image_src = item.get("imageSrc") or "/src/assets/food/cutting-board-sourdough.jpg"
    now_iso = added_at_iso

    metadata = dict(item)
    metadata["modelVersions"] = item.get("modelVersions") or item.get("model_versions")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO pantry_history (
                id, user_id, food_name, cultivar, status, status_category,
                quality_score, quality_period, remaining_days, storage_environment,
                storage_type, eat_first_priority, eat_first_score, eat_first_reason,
                guidance, image_src, raw_metadata, created_at,
                analysis_id, added_at, estimated_quality_days, estimated_end_at,
                freshness_state, freshness_confidence, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                user_id,
                food_name,
                cultivar,
                status_label,
                status_category,
                quality_score,
                quality_period,
                est_quality_days,
                storage_env,
                storage_type,
                ef_priority,
                ef_score,
                ef_reason,
                guidance,
                image_src,
                json.dumps(metadata),
                analysis_at_iso,
                analysis_id,
                added_at_iso,
                est_quality_days,
                estimated_end_iso,
                freshness_state,
                freshness_confidence,
                now_iso,
            ),
        )
        from backend.app.services.food_form_service import infer_food_form

        sl = item.get("shelfLife") if isinstance(item.get("shelfLife"), dict) else {}
        ref = sl.get("referenceDuration") or {}
        ref_min = ref.get("minDays")
        ref_max = ref.get("maxDays")
        days_stored = item.get("daysStoredAtAnalysis")
        if days_stored is None and sl.get("daysStored") is not None:
            days_stored = sl.get("daysStored")
        if days_stored is None and item.get("storageContext"):
            days_stored = item.get("storageContext", {}).get("daysInPantry")
        food_form = item.get("foodForm") or infer_food_form(
            food_name, freshness_label=freshness_state, analysis_context=metadata
        )
        mv = item.get("modelVersions") or {}
        conn.execute(
            """
            UPDATE pantry_history SET
                food_form = ?,
                days_stored_at_analysis = ?,
                reference_min_days = ?,
                reference_max_days = ?,
                food_model_version = ?,
                freshness_model_version = ?,
                shelf_life_model_version = ?,
                legacy_timing = 0
            WHERE id = ? AND user_id = ?
            """,
            (
                food_form,
                days_stored,
                ref_min,
                ref_max,
                mv.get("food") or mv.get("detector"),
                mv.get("freshness") or item.get("freshnessModelVersion"),
                sl.get("source") or mv.get("shelfLife"),
                item_id,
                user_id,
            ),
        )
        conn.commit()

    saved = get_current_pantry_state(user_id)
    for row in saved:
        if row["id"] == item_id:
            return row
    return get_pantry_items(user_id)[0] if get_pantry_items(user_id) else {}


def delete_pantry_item(item_id: str, user_id: str) -> bool:
    """Delete an item from user's pantry history."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM pantry_history WHERE id = ? AND user_id = ?",
            (item_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_pantry_items(user_id: str) -> bool:
    """Clear all pantry items for user (e.g. testing 0-items state)."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM pantry_history WHERE user_id = ?", (user_id,))
        conn.commit()
        return True


def insert_ml_feedback(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    feedback_id = payload.get("feedbackId") or f"fb_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    status = payload.get("reviewStatus") or "COLLECTED"
    if status not in {"COLLECTED", "VALIDATED", "TRAINING_READY", "USED_FOR_TRAINING", "REJECTED"}:
        status = "COLLECTED"
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO ml_feedback (
                feedback_id, user_id, analysis_id, image_path,
                predicted_food, predicted_food_confidence, predicted_food_form,
                predicted_freshness, predicted_freshness_confidence, predicted_shelf_life,
                user_corrected_food, user_corrected_food_form, user_corrected_freshness,
                user_corrected_shelf_life, storage_type, days_stored,
                feedback_source, review_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                feedback_id,
                user_id,
                payload.get("analysisId"),
                payload.get("imagePath"),
                payload.get("predictedFood"),
                payload.get("predictedFoodConfidence"),
                payload.get("predictedFoodForm"),
                payload.get("predictedFreshness"),
                payload.get("predictedFreshnessConfidence"),
                payload.get("predictedShelfLife"),
                payload.get("userCorrectedFood"),
                payload.get("userCorrectedFoodForm"),
                payload.get("userCorrectedFreshness"),
                payload.get("userCorrectedShelfLife"),
                payload.get("storageType"),
                payload.get("daysStored"),
                payload.get("feedbackSource") or "user",
                status,
                now_iso,
            ),
        )
        conn.commit()
    return {"feedbackId": feedback_id, "reviewStatus": status, "createdAt": now_iso}


def list_ml_feedback(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            """
            SELECT * FROM ml_feedback WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "feedbackId": r["feedback_id"],
                "analysisId": r["analysis_id"],
                "reviewStatus": r["review_status"],
                "predictedFood": r["predicted_food"],
                "createdAt": r["created_at"],
            }
        )
    return out

