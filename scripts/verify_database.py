#!/usr/bin/env python3
"""Read-only schema and row-count verification for the existing SQLite database."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "app" / "database" / "fresho_buddy.db"
REPORT_PATH = PROJECT_ROOT / "reports" / "database_verification.md"

EXPECTED_TABLES = {
    "users", "auth_sessions", "conversations", "messages",
    "pantry_history", "ml_feedback",
}
PANTRY_FIELDS = {
    "analysis_id", "user_id", "food_name", "food_form", "freshness_state",
    "freshness_confidence", "freshness_model_version", "estimated_quality_days",
    "estimated_end_at", "days_stored_at_analysis", "eat_first_priority",
    "eat_first_score", "shelf_life_model_version", "created_at",
}


def inspect_database():
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"SQLite database not found: {DB_PATH}")
    with sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        names = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        tables = {}
        for name in sorted(names):
            columns = {row[1] for row in conn.execute(f'PRAGMA table_info("{name}")')}
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables[name] = {"rows": count, "columns": columns}
        return tables


def main():
    tables = inspect_database()
    pantry = tables.get("pantry_history", {"rows": 0, "columns": set()})
    feedback = tables.get("ml_feedback", {"rows": 0, "columns": set()})
    missing_tables = EXPECTED_TABLES - tables.keys()
    missing_pantry = PANTRY_FIELDS - pantry["columns"]
    lines = [
        "# Database Verification", "",
        f"- Verified: {datetime.now(timezone.utc).isoformat()}",
        f"- Database: `{DB_PATH}`",
        f"- Database size: {DB_PATH.stat().st_size:,} bytes",
        "- Mode: read-only inspection; no rows or schema changed", "",
        "## Tables", "", "| Table | Rows | Columns |", "|---|---:|---:|",
    ]
    lines += [f"| `{name}` | {info['rows']} | {len(info['columns'])} |"
              for name, info in sorted(tables.items())]
    lines += ["", "## Persistence fields", "",
              f"Pantry history has {len(PANTRY_FIELDS - missing_pantry)}/{len(PANTRY_FIELDS)} checked fields.",
              f"Missing checked fields: {', '.join(sorted(missing_pantry)) or 'none'}.",
              f"Expected tables missing: {', '.join(sorted(missing_tables)) or 'none'}.",
              "", "## Record counts", "",
              f"- Pantry records: {pantry['rows']}",
              f"- ML feedback records: {feedback['rows']}",
              f"- Analyses are represented in the existing `pantry_history` table; no separate analyses table exists.", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("Database:", DB_PATH)
    for name, info in sorted(tables.items()):
        print(f"{name}: {info['rows']} rows, {len(info['columns'])} columns")
    print("Missing tables:", sorted(missing_tables))
    print("Missing checked pantry fields:", sorted(missing_pantry))
    print("Report:", REPORT_PATH)
    return not missing_tables and not missing_pantry


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
