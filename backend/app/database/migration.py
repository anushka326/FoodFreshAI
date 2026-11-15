"""
FoodFresh AI — Non-Destructive Database Migration Engine
Safely identifies and migrates legacy user records and configuration from previous
SQLite databases (e.g. foodfresh.db from main branch PR #1) into the unified
production database (fresho_buddy.db).

Guarantees:
1. Never deletes, alters, or drops source databases.
2. Idempotent: safe to run multiple times with zero duplicates.
3. Preserves email addresses, display names, and legacy password hashes.
4. Preserves user IDs (mapped as usr_legacy_<id> or raw ID).
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.database import chat_db

logger = logging.getLogger("foodfresh.migration")


def find_candidate_legacy_databases() -> List[Path]:
    """Discover potential legacy SQLite databases in backend and workspace root."""
    candidates: List[Path] = []
    base_dir = Path(__file__).resolve().parent.parent.parent  # backend directory
    root_dir = base_dir.parent  # workspace root

    candidate_paths = [
        base_dir / "foodfresh.db",
        root_dir / "foodfresh.db",
        base_dir / "app" / "foodfresh.db",
    ]

    # Check DATABASE_URL from environment
    env_db = os.getenv("DATABASE_URL")
    if env_db and env_db.startswith("sqlite:///"):
        parsed_path = Path(env_db.replace("sqlite:///", "", 1))
        if not parsed_path.is_absolute():
            parsed_path = base_dir / parsed_path
        candidate_paths.append(parsed_path)

    for p in candidate_paths:
        try:
            if p.is_file() and p.resolve() != Path(chat_db.DB_PATH).resolve() and p not in candidates:
                candidates.append(p)
        except Exception:
            pass

    return candidates


def migrate_legacy_users(source_db_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Safely import legacy user accounts into the primary database.
    If source_db_path is not specified, scans candidate legacy locations.
    """
    sources_to_check: List[Path] = []
    if source_db_path:
        p = Path(source_db_path)
        if p.is_file():
            sources_to_check.append(p)
    else:
        sources_to_check = find_candidate_legacy_databases()

    result = {
        "sources_scanned": len(sources_to_check),
        "migrated_users": 0,
        "skipped_existing": 0,
        "details": [],
    }

    if not sources_to_check:
        return result

    target_conn = chat_db.get_db_connection()
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        for src_path in sources_to_check:
            logger.info(f"Checking candidate legacy database at {src_path}")
            try:
                # Open source strictly in read-only mode (URI=True) to prevent any accidental write
                src_uri = f"file:{src_path.resolve()}?mode=ro"
                src_conn = sqlite3.connect(src_uri, uri=True)
                src_conn.row_factory = sqlite3.Row
            except Exception as e:
                logger.warning(f"Could not open source db {src_path}: {e}")
                continue

            try:
                # Check for existence of users table
                cur = src_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                if not cur.fetchone():
                    src_conn.close()
                    continue

                # Query columns in source users table
                col_info = src_conn.execute("PRAGMA table_info(users)").fetchall()
                col_names = {c["name"] for c in col_info}

                # Ensure minimum required fields exist
                if not ({"email", "hashed_password"}.issubset(col_names) or {"email", "password_hash"}.issubset(col_names)):
                    src_conn.close()
                    continue

                pwd_col = "hashed_password" if "hashed_password" in col_names else "password_hash"
                name_col = "full_name" if "full_name" in col_names else ("name" if "name" in col_names else None)
                id_col = "id" if "id" in col_names else ("user_id" if "user_id" in col_names else None)

                cols_to_select = ["email", pwd_col]
                if id_col:
                    cols_to_select.append(id_col)
                if name_col:
                    cols_to_select.append(name_col)

                select_sql = f"SELECT {', '.join(cols_to_select)} FROM users"
                rows = src_conn.execute(select_sql).fetchall()

                for row in rows:
                    raw_email = row["email"]
                    if not raw_email:
                        continue
                    clean_email = str(raw_email).strip().lower()
                    raw_pwd = row[pwd_col] or ""
                    full_name = str(row[name_col]).strip() if (name_col and row[name_col]) else "FoodFresh User"
                    raw_id = row[id_col] if id_col else None

                    # Format preserved user ID
                    if raw_id:
                        user_id = str(raw_id) if str(raw_id).startswith("usr_") else f"usr_legacy_{raw_id}"
                    else:
                        user_id = f"usr_legacy_{clean_email.split('@')[0]}"

                    # Check if user already exists in target
                    existing = target_conn.execute(
                        "SELECT user_id FROM users WHERE LOWER(email) = ?", (clean_email,)
                    ).fetchone()

                    if existing:
                        result["skipped_existing"] += 1
                        continue

                    # Insert non-destructively
                    target_conn.execute(
                        """
                        INSERT INTO users (user_id, email, password_hash, full_name, household_type, created_at, avatar)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, clean_email, raw_pwd, full_name, None, now_iso, None),
                    )
                    target_conn.commit()
                    result["migrated_users"] += 1
                    result["details"].append({"email": clean_email, "user_id": user_id, "from": str(src_path)})
                    logger.info(f"Migrated legacy user {clean_email} -> {user_id}")

            except Exception as err:
                logger.warning(f"Error reading users from legacy db {src_path}: {err}")
            finally:
                src_conn.close()

    finally:
        target_conn.close()

    return result
