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
from typing import Any, Dict, List, Optional, Set

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
        ("barcode", "TEXT"),
        ("brand", "TEXT"),
        ("item_type", "TEXT DEFAULT 'fresh'"),
        ("mfg_date", "TEXT"),
        ("expiry_date", "TEXT"),
        ("ingredients", "TEXT"),
        ("nutrition", "TEXT"),
        ("storage_instructions", "TEXT"),
        ("is_archived", "INTEGER DEFAULT 0"),
        ("archived_at", "TEXT"),
        ("removal_reason", "TEXT"),
        ("removal_action", "TEXT"),
    ]
    for col, col_type in pantry_columns:
        if not _column_exists(conn, "pantry_history", col):
            conn.execute(f"ALTER TABLE pantry_history ADD COLUMN {col} {col_type}")

    # Ensure all existing pantry rows have is_archived = 0 if NULL
    conn.execute(
        """
        UPDATE pantry_history
        SET is_archived = 0
        WHERE is_archived IS NULL
        """
    )

    # Ensure users table has avatar column
    if not _column_exists(conn, "users", "avatar"):
        conn.execute("ALTER TABLE users ADD COLUMN avatar TEXT")

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

    # Notification read states table
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS notification_read_states (
            user_id TEXT NOT NULL,
            notification_id TEXT NOT NULL,
            read_at TEXT NOT NULL,
            PRIMARY KEY(user_id, notification_id)
        );
        CREATE INDEX IF NOT EXISTS idx_notif_read_user ON notification_read_states(user_id);
    """)

    # Food waste impact tracking logs table
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS food_impact_logs (
            log_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            pantry_item_id TEXT,
            food_name TEXT NOT NULL,
            cultivar TEXT,
            action TEXT NOT NULL,
            remaining_days INTEGER,
            was_saved INTEGER DEFAULT 0,
            reason TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_food_impact_user ON food_impact_logs(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_food_impact_action ON food_impact_logs(user_id, action);
    """)

    # Project-wide pantry activity logs (all food add, consume, waste, remove events)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pantry_activity_logs (
            activity_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            pantry_item_id TEXT,
            food_name TEXT NOT NULL,
            cultivar TEXT,
            action_type TEXT NOT NULL,
            details TEXT,
            quality_score INTEGER,
            image_src TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_activity_user ON pantry_activity_logs(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_activity_type ON pantry_activity_logs(user_id, action_type);
    """)

    # Backfill missing archived pantry rows from legacy food_impact_logs if needed
    try:
        cur_impact = conn.execute(
            """
            SELECT log_id, user_id, pantry_item_id, food_name, cultivar, action, reason, remaining_days, created_at
            FROM food_impact_logs
            """
        )
        impact_rows = cur_impact.fetchall()
        for imp in impact_rows:
            pid = imp[2]
            if pid:
                chk = conn.execute("SELECT id FROM pantry_history WHERE id = ?", (pid,)).fetchone()
                if not chk:
                    # Recreate archived row so history page displays all past removed produce
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO pantry_history (
                            id, user_id, food_name, cultivar, status, status_category,
                            quality_score, quality_period, remaining_days, storage_environment,
                            storage_type, eat_first_priority, eat_first_score, eat_first_reason,
                            guidance, image_src, created_at, added_at, is_archived, archived_at,
                            removal_action, removal_reason
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                        """,
                        (
                            pid,
                            imp[1],
                            imp[3],
                            imp[4] or f"{imp[3]} • Fresh Harvest",
                            "Archived",
                            "semi",
                            80,
                            "0 days remaining",
                            imp[7] or 0,
                            "Past Inventory",
                            "countertop",
                            "NORMAL",
                            0,
                            "Item recorded in history log",
                            "Past logged food item.",
                            "/src/assets/food/cutting-board-sourdough.jpg",
                            imp[8],
                            imp[8],
                            imp[8],
                            imp[5],
                            imp[6] or f"Item marked as {imp[5]}",
                        )
                    )
    except Exception:
        pass

    # Backfill activity logs if empty
    try:
        act_count = conn.execute("SELECT COUNT(*) FROM pantry_activity_logs").fetchone()[0]
        if act_count == 0:
            # Backfill from pantry_history
            cur_pantry = conn.execute("SELECT id, user_id, food_name, cultivar, quality_score, image_src, created_at, is_archived, archived_at, removal_action, removal_reason FROM pantry_history")
            for r in cur_pantry.fetchall():
                aid = f"act_{uuid.uuid4().hex[:12]}"
                conn.execute(
                    """
                    INSERT INTO pantry_activity_logs (
                        activity_id, user_id, pantry_item_id, food_name, cultivar,
                        action_type, details, quality_score, image_src, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'added', 'Analyzed and added to pantry.', ?, ?, ?)
                    """,
                    (aid, r[1], r[0], r[2], r[3], r[4], r[5], r[6])
                )
                if r[7]: # is_archived
                    aid2 = f"act_{uuid.uuid4().hex[:12]}"
                    act_type = r[9] or "removed"
                    conn.execute(
                        """
                        INSERT INTO pantry_activity_logs (
                            activity_id, user_id, pantry_item_id, food_name, cultivar,
                            action_type, details, quality_score, image_src, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (aid2, r[1], r[0], r[2], r[3], act_type, r[10] or f"Product marked as {act_type}.", r[4], r[5], r[8] or r[6])
                    )
    except Exception:
        pass

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

    # Automatic safe migration of legacy users from previous SQLite databases
    try:
        from backend.app.database.migration import migrate_legacy_users
        migrate_legacy_users()
    except Exception as e:
        logger.debug(f"Legacy migration skipped: {e}")


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
    avatar: Optional[str] = None,
) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, email, password_hash, full_name, household_type, avatar, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, password_hash, full_name, household_type, avatar, now_iso),
        )
        conn.commit()
    return user_record_to_public(
        {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "household_type": household_type,
            "avatar": avatar,
            "created_at": now_iso,
        }
    )


def user_record_to_public(record: Dict[str, Any]) -> Dict[str, Any]:
    avatar_val = record.get("avatar") or record.get("avatarUrl")
    return {
        "id": record.get("user_id") or record.get("id"),
        "email": record.get("email"),
        "fullName": record.get("full_name") or record.get("fullName"),
        "householdType": record.get("household_type") or record.get("householdType"),
        "avatar": avatar_val,
        "avatarUrl": avatar_val,
        "status": "Pantry Guard Active",
        "temperatureUnit": "C",
        "remindersEnabled": True,
        "eatFirstRoadmapEnabled": True,
        "freshoBuddyEnabled": True,
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    if not email or not str(email).strip():
        return None
    clean = str(email).strip().lower()

    # Common account aliases mapping
    aliases = {
        "anushka": "anushka@gmail.com",
        "anushka326": "anushka@gmail.com",
        "anushkanpise@gmail.com": "anushka@gmail.com",
        "anushkanpise": "anushka@gmail.com",
        "demo": "anushka@gmail.com",
        "demo_chef": "demo_chef@foodfresh.ai",
        "demochef": "demo_chef@foodfresh.ai",
    }
    clean = aliases.get(clean, clean)

    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, email, password_hash, full_name, household_type, avatar, created_at FROM users WHERE LOWER(TRIM(email)) = ?",
            (clean,),
        )
        row = cur.fetchone()
        if not row and "@" not in clean:
            # Check by username prefix (e.g. "anushka" matching "anushka@...") or exact full_name
            cur = conn.execute(
                "SELECT user_id, email, password_hash, full_name, household_type, avatar, created_at FROM users WHERE LOWER(TRIM(email)) LIKE ? OR LOWER(TRIM(full_name)) = ? ORDER BY created_at DESC LIMIT 1",
                (f"{clean}@%", clean),
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
        "avatar": row["avatar"] if "avatar" in row.keys() else None,
        "created_at": row["created_at"],
    }


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, email, password_hash, full_name, household_type, avatar, created_at FROM users WHERE user_id = ?",
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
        "avatar": row["avatar"] if "avatar" in row.keys() else None,
        "created_at": row["created_at"],
    }


def update_user_profile(
    user_id: str,
    full_name: Optional[str] = None,
    avatar: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Update user's display name or selected avatar.
    Isolated strictly by authenticated user_id.
    """
    updates = []
    params = []
    if full_name is not None and str(full_name).strip():
        updates.append("full_name = ?")
        params.append(str(full_name).strip())
    if avatar is not None:
        updates.append("avatar = ?")
        params.append(str(avatar).strip() if avatar else None)

    if updates:
        params.append(user_id)
        with get_db_connection() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?",
                params,
            )
            conn.commit()

    record = get_user_by_id(user_id)
    return user_record_to_public(record) if record else None


def update_user_password(user_id: str, new_password_hash: str) -> bool:
    """Update password hash for an existing user (e.g. hash upgrade)."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (new_password_hash, user_id),
        )
        conn.commit()
        return cur.rowcount > 0


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
        "barcode": row["barcode"] if "barcode" in keys else None,
        "brand": row["brand"] if "brand" in keys else None,
        "itemType": row["item_type"] if "item_type" in keys else "fresh",
        "mfgDate": row["mfg_date"] if "mfg_date" in keys else None,
        "expiryDate": row["expiry_date"] if "expiry_date" in keys else None,
        "ingredients": row["ingredients"] if "ingredients" in keys else None,
        "nutrition": row["nutrition"] if "nutrition" in keys else None,
        "storageInstructions": row["storage_instructions"] if "storage_instructions" in keys else None,
        "isArchived": bool(row["is_archived"]) if "is_archived" in keys and row["is_archived"] else False,
        "archivedAt": row["archived_at"] if "archived_at" in keys else None,
        "removalReason": row["removal_reason"] if "removal_reason" in keys else None,
        "removalAction": row["removal_action"] if "removal_action" in keys else None,
        "metadata": raw_meta,
    }


def get_pantry_items_raw(user_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
    """Load pantry rows without dynamic enrichment (used by pantry_state_service). By default, only active items."""
    with get_db_connection() as conn:
        if include_archived:
            query = """
                SELECT * FROM pantry_history
                WHERE user_id = ?
                ORDER BY created_at DESC
            """
        else:
            query = """
                SELECT * FROM pantry_history
                WHERE user_id = ? AND (is_archived = 0 OR is_archived IS NULL)
                ORDER BY created_at DESC
            """
        cursor = conn.execute(query, (user_id,))
        rows = cursor.fetchall()
        return [_format_pantry_row(r) for r in rows]


def get_archived_pantry_items(user_id: str) -> List[Dict[str, Any]]:
    """Retrieve all past items removed/archived from the pantry."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM pantry_history
            WHERE user_id = ? AND is_archived = 1
            ORDER BY archived_at DESC, created_at DESC
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

    # Support explicit expiry date from packaged food OCR / barcode scanning
    exp_input = item.get("expiryDate") or item.get("estimatedEndAt")
    if exp_input:
        exp_str = str(exp_input).strip()
        if "T" not in exp_str and len(exp_str) == 10:
            exp_str = f"{exp_str}T23:59:59+00:00"
        estimated_end_iso = exp_str
        from backend.app.services.pantry_state_service import compute_remaining_days_from_end_at
        rem_from_exp = compute_remaining_days_from_end_at(estimated_end_iso, now=added_at_dt)
        if rem_from_exp is not None:
            est_quality_days = rem_from_exp
    elif est_quality_days is not None:
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
        item_type = item.get("itemType") or ("packaged" if item.get("barcode") or item.get("expiryDate") else "fresh")
        raw_ingredients = item.get("ingredients")
        if isinstance(raw_ingredients, list):
            ingredients_str = ", ".join(str(x) for x in raw_ingredients)
        else:
            ingredients_str = str(raw_ingredients) if raw_ingredients else None

        raw_nutrition = item.get("nutrition")
        nutrition_str = json.dumps(raw_nutrition) if isinstance(raw_nutrition, dict) else (str(raw_nutrition) if raw_nutrition else None)

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
                legacy_timing = 0,
                barcode = ?,
                brand = ?,
                item_type = ?,
                mfg_date = ?,
                expiry_date = ?,
                ingredients = ?,
                nutrition = ?,
                storage_instructions = ?
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
                item.get("barcode"),
                item.get("brand"),
                item_type,
                item.get("mfgDate"),
                item.get("expiryDate"),
                ingredients_str,
                nutrition_str,
                item.get("storageInstructions") or item.get("storage_instructions"),
                item_id,
                user_id,
            ),
        )
        # Ensure newly added item is active
        conn.execute(
            """
            UPDATE pantry_history SET
                is_archived = 0,
                archived_at = NULL,
                removal_action = NULL,
                removal_reason = NULL
            WHERE id = ? AND user_id = ?
            """,
            (item_id, user_id),
        )
        conn.commit()

    # Record item added in project-wide activity log
    record_activity_log(
        user_id=user_id,
        food_name=food_name,
        action_type="added",
        pantry_item_id=item_id,
        cultivar=cultivar,
        details=f"Analyzed and added to pantry storage ({storage_env}).",
        quality_score=quality_score,
        image_src=image_src,
        created_at=now_iso,
    )

    saved = get_current_pantry_state(user_id)
    for row in saved:
        if row["id"] == item_id:
            return row
    return get_pantry_items(user_id)[0] if get_pantry_items(user_id) else {}


def delete_pantry_item(
    item_id: str,
    user_id: str,
    action: str = "removed",
    reason: Optional[str] = None,
) -> bool:
    """
    Soft-delete / archive an item from user's active pantry.
    Retains all historical data, analysis metadata, timestamps, and logs the activity.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_action = str(action).lower().strip() if action else "removed"
    if clean_action not in {"consumed", "wasted", "removed"}:
        clean_action = "removed"

    row_data = None
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM pantry_history WHERE id = ? AND user_id = ? AND (is_archived = 0 OR is_archived IS NULL)",
            (item_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            return False
        row_data = dict(row)

        cursor = conn.execute(
            """
            UPDATE pantry_history
            SET is_archived = 1,
                archived_at = ?,
                removal_action = ?,
                removal_reason = ?,
                updated_at = ?
            WHERE id = ? AND user_id = ? AND (is_archived = 0 OR is_archived IS NULL)
            """,
            (
                now_iso,
                clean_action,
                reason or f"Food product marked as {clean_action}.",
                now_iso,
                item_id,
                user_id,
            ),
        )
        conn.commit()
        success = cursor.rowcount > 0

    if success and row_data:
        food_name = row_data.get("food_name") or "Produce"
        cultivar = row_data.get("cultivar") or f"{food_name} • Fresh Harvest"
        q_score = row_data.get("quality_score") or 80
        img = row_data.get("image_src") or "/src/assets/food/cutting-board-sourdough.jpg"

        record_activity_log(
            user_id=user_id,
            food_name=food_name,
            action_type=clean_action,
            pantry_item_id=item_id,
            cultivar=cultivar,
            details=reason or f"Item removed from active pantry inventory ({clean_action}).",
            quality_score=q_score,
            image_src=img,
            created_at=now_iso,
        )

    return success


def restore_pantry_item(item_id: str, user_id: str) -> bool:
    """Restore an archived item back to active pantry inventory."""
    now_iso = datetime.now(timezone.utc).isoformat()
    row_data = None
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM pantry_history WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            return False
        row_data = dict(row)

        cursor = conn.execute(
            """
            UPDATE pantry_history
            SET is_archived = 0,
                archived_at = NULL,
                removal_action = NULL,
                removal_reason = NULL,
                updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (now_iso, item_id, user_id),
        )
        conn.commit()
        success = cursor.rowcount > 0

    if success and row_data:
        record_activity_log(
            user_id=user_id,
            food_name=row_data.get("food_name") or "Produce",
            action_type="restored",
            pantry_item_id=item_id,
            cultivar=row_data.get("cultivar"),
            details="Restored back into active pantry inventory.",
            quality_score=row_data.get("quality_score") or 80,
            image_src=row_data.get("image_src"),
            created_at=now_iso,
        )

    return success


def permanently_delete_pantry_item(item_id: str, user_id: str) -> bool:
    """Permanently delete an item from user's pantry history if explicitly requested."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM pantry_history WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_pantry_items(user_id: str) -> bool:
    """Soft-delete all active pantry items for user (archives them)."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute(
            """
            UPDATE pantry_history
            SET is_archived = 1,
                archived_at = ?,
                removal_action = 'removed',
                removal_reason = 'Pantry cleared by user'
            WHERE user_id = ? AND (is_archived = 0 OR is_archived IS NULL)
            """,
            (now_iso, user_id),
        )
        conn.commit()
        return True


# ==============================================================================
# AUDIT LOGS FOR PANTRY & PRODUCT ACTIVITIES
# ==============================================================================

def record_activity_log(
    user_id: str,
    food_name: str,
    action_type: str,
    pantry_item_id: Optional[str] = None,
    cultivar: Optional[str] = None,
    details: Optional[str] = None,
    quality_score: Optional[int] = None,
    image_src: Optional[str] = None,
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Record an audit trail activity for any food action."""
    activity_id = f"act_{uuid.uuid4().hex[:12]}"
    now_iso = created_at or datetime.now(timezone.utc).isoformat()
    clean_action = str(action_type).lower().strip()

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO pantry_activity_logs (
                activity_id, user_id, pantry_item_id, food_name, cultivar,
                action_type, details, quality_score, image_src, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                activity_id,
                user_id,
                pantry_item_id,
                food_name,
                cultivar or f"{food_name} • Fresh Harvest",
                clean_action,
                details or f"Action {clean_action} performed on {food_name}.",
                quality_score or 80,
                image_src or "/src/assets/food/cutting-board-sourdough.jpg",
                now_iso,
            ),
        )
        conn.commit()

    return {
        "activityId": activity_id,
        "userId": user_id,
        "pantryItemId": pantry_item_id,
        "foodName": food_name,
        "cultivar": cultivar,
        "actionType": clean_action,
        "details": details,
        "qualityScore": quality_score,
        "imageSrc": image_src,
        "createdAt": now_iso,
    }


def list_activity_logs(user_id: str, limit: int = 300) -> List[Dict[str, Any]]:
    """Retrieve chronologically ordered audit logs of all user food activities."""
    with get_db_connection() as conn:
        cur = conn.execute(
            """
            SELECT * FROM pantry_activity_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()

    return [
        {
            "activityId": r["activity_id"],
            "userId": r["user_id"],
            "pantryItemId": r["pantry_item_id"],
            "foodName": r["food_name"],
            "cultivar": r["cultivar"] or f"{r['food_name']} • Fresh Harvest",
            "actionType": r["action_type"],
            "details": r["details"],
            "qualityScore": r["quality_score"],
            "imageSrc": r["image_src"] or "/src/assets/food/cutting-board-sourdough.jpg",
            "createdAt": r["created_at"],
        }
        for r in rows
    ]


def clear_activity_logs(user_id: str) -> bool:
    """Clear activity logs for a user."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM pantry_activity_logs WHERE user_id = ?", (user_id,))
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


# ==============================================================================
# NOTIFICATION READ STATES
# ==============================================================================

def get_read_notification_ids(user_id: str) -> Set[str]:
    """Retrieve all notification IDs marked as read by the user."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT notification_id FROM notification_read_states WHERE user_id = ?",
            (user_id,),
        )
        return {row["notification_id"] for row in cur.fetchall()}


def mark_notification_read(user_id: str, notification_id: str) -> bool:
    """Mark a single notification as read for a user."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO notification_read_states (user_id, notification_id, read_at)
            VALUES (?, ?, ?)
            """,
            (user_id, notification_id, now_iso),
        )
        conn.commit()
    return True


def mark_notification_unread(user_id: str, notification_id: str) -> bool:
    """Mark a notification back as unread for a user."""
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM notification_read_states WHERE user_id = ? AND notification_id = ?",
            (user_id, notification_id),
        )
        conn.commit()
    return True


def mark_all_notifications_read(user_id: str, notification_ids: List[str]) -> bool:
    """Mark multiple notifications as read for a user in a single transaction."""
    if not notification_ids:
        return True
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO notification_read_states (user_id, notification_id, read_at)
            VALUES (?, ?, ?)
            """,
            [(user_id, nid, now_iso) for nid in notification_ids],
        )
        conn.commit()
    return True


# ==============================================================================
# FOOD-WASTE IMPACT ANALYTICS STORAGE
# ==============================================================================

def record_food_impact(
    user_id: str,
    food_name: str,
    action: str,
    remaining_days: Optional[int] = None,
    was_saved: int = 0,
    pantry_item_id: Optional[str] = None,
    cultivar: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Log an actual user action (consumed or wasted) for a pantry food item.
    """
    log_id = f"imp_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_action = "consumed" if action.lower() == "consumed" else "wasted"

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO food_impact_logs (
                log_id, user_id, pantry_item_id, food_name, cultivar,
                action, remaining_days, was_saved, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log_id,
                user_id,
                pantry_item_id,
                food_name,
                cultivar,
                clean_action,
                remaining_days,
                1 if was_saved else 0,
                reason,
                now_iso,
            ),
        )
        conn.commit()

    return {
        "logId": log_id,
        "userId": user_id,
        "pantryItemId": pantry_item_id,
        "foodName": food_name,
        "cultivar": cultivar,
        "action": clean_action,
        "remainingDays": remaining_days,
        "wasSaved": bool(was_saved),
        "reason": reason,
        "createdAt": now_iso,
    }


def list_food_impact_logs(user_id: str, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
    """Retrieve chronologically ordered food impact action logs for a user."""
    with get_db_connection() as conn:
        if limit is not None and limit > 0:
            cur = conn.execute(
                """
                SELECT * FROM food_impact_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
        else:
            cur = conn.execute(
                """
                SELECT * FROM food_impact_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
        rows = cur.fetchall()

    return [
        {
            "logId": r["log_id"],
            "userId": r["user_id"],
            "pantryItemId": r["pantry_item_id"],
            "foodName": r["food_name"],
            "cultivar": r["cultivar"] or f"{r['food_name']} • Fresh Harvest",
            "action": r["action"],
            "remainingDays": r["remaining_days"],
            "wasSaved": bool(r["was_saved"]),
            "reason": r["reason"],
            "createdAt": r["created_at"],
        }
        for r in rows
    ]


def delete_food_impact_log(user_id: str, log_id: str) -> bool:
    """Delete a specific impact log (e.g. undo action)."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "DELETE FROM food_impact_logs WHERE log_id = ? AND user_id = ?",
            (log_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0


def clear_food_impact_logs(user_id: str) -> bool:
    """Clear all impact logs for testing."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM food_impact_logs WHERE user_id = ?", (user_id,))
        conn.commit()
        return True




