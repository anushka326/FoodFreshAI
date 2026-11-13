#!/usr/bin/env python3
"""Safe SQLite inspection — no secrets printed."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import chat_db  # noqa: E402

SENSITIVE_COLUMNS = frozenset(
    {"password_hash", "token", "content", "raw_metadata", "analysis_context"}
)


def main():
    db_path = chat_db.DB_PATH
    print(f"Database path: {db_path}")
    print(f"Exists: {db_path.exists()}\n")

    import sqlite3

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for t in tables:
        name = t["name"]
        count = conn.execute(f"SELECT COUNT(*) AS c FROM {name}").fetchone()["c"]
        print(f"Table: {name}  rows={count}")
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        col_names = [c[1] for c in cols]
        print("  columns:", ", ".join(col_names))
        safe_sample_cols = [c for c in col_names if c not in SENSITIVE_COLUMNS][:6]
        if safe_sample_cols and count:
            sel = ", ".join(safe_sample_cols)
            row = conn.execute(f"SELECT {sel} FROM {name} LIMIT 1").fetchone()
            if row:
                print("  sample:", dict(row))
        print()
    conn.close()


if __name__ == "__main__":
    main()
