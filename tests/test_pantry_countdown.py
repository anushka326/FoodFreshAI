"""
Tests for UTC calendar-day pantry remaining quality countdown.
"""

from datetime import datetime, timezone, timedelta

from backend.app.services.pantry_state_service import (
    compute_remaining_days,
    compute_estimated_end_at,
    enrich_pantry_row,
)


def test_countdown_same_day_through_expiration():
    added = datetime(2025, 9, 30, 10, 0, 0, tzinfo=timezone.utc)
    added_iso = added.isoformat()
    quality_days = 5

    assert compute_remaining_days(added_iso, quality_days, now=added) == 5
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=1)) == 4
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=2)) == 3
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=3)) == 2
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=4)) == 1
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=5)) == 0
    assert compute_remaining_days(added_iso, quality_days, now=added + timedelta(days=10)) == 0


def test_estimated_end_at_preserves_audit_anchor():
    added = datetime(2026, 9, 30, 8, 0, 0, tzinfo=timezone.utc)
    end = compute_estimated_end_at(added, 5)
    assert end.date().isoformat() == "2026-10-05"


def test_remaining_from_end_at_sept_30_to_oct_5():
    added = datetime(2026, 9, 30, 12, 0, 0, tzinfo=timezone.utc)
    end_iso = compute_estimated_end_at(added, 5).isoformat()
    from backend.app.services.pantry_state_service import compute_remaining_days_from_end_at

    assert compute_remaining_days_from_end_at(end_iso, now=added) == 5
    assert compute_remaining_days_from_end_at(
        end_iso, now=added + timedelta(days=1)
    ) == 4
    assert compute_remaining_days_from_end_at(
        end_iso, now=added + timedelta(days=5)
    ) == 0


def test_enrich_row_unknown_quality():
    row = {
        "foodName": "Mystery",
        "addedAt": datetime.now(timezone.utc).isoformat(),
        "estimatedQualityDays": None,
        "status": "Fresh",
        "storageType": "countertop",
    }
    out = enrich_pantry_row(row)
    assert out["remainingDays"] is None
    assert "cannot currently be estimated" in out["qualityPeriod"]
