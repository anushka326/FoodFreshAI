#!/usr/bin/env python3
"""
Export VALIDATED ml_feedback rows to data/feedback/manifest.csv (training-ready only).
Does not trigger training.
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import chat_db  # noqa: E402

MANIFEST = PROJECT_ROOT / "data" / "feedback" / "manifest.csv"
HEADER = [
    "image_path",
    "food_name",
    "food_form",
    "freshness_label",
    "storage_type",
    "days_stored",
    "shelf_life_label",
    "source",
    "validation_status",
]


def main():
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    import sqlite3

    conn = sqlite3.connect(str(chat_db.DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT * FROM ml_feedback
        WHERE review_status IN ('VALIDATED', 'TRAINING_READY')
        ORDER BY created_at ASC
        """
    ).fetchall()
    conn.close()

    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "image_path": r["image_path"] or "",
                    "food_name": r["user_corrected_food"] or r["predicted_food"] or "",
                    "food_form": r["user_corrected_food_form"] or r["predicted_food_form"] or "unknown",
                    "freshness_label": r["user_corrected_freshness"] or r["predicted_freshness"] or "",
                    "storage_type": r["storage_type"] or "",
                    "days_stored": r["days_stored"] if r["days_stored"] is not None else "",
                    "shelf_life_label": r["user_corrected_shelf_life"] or r["predicted_shelf_life"] or "",
                    "source": r["feedback_source"] or "user",
                    "validation_status": r["review_status"],
                }
            )
    print(f"Wrote {len(rows)} validated rows to {MANIFEST}")


if __name__ == "__main__":
    main()
