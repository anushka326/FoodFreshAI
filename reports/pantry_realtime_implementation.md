# Pantry Real-Time Implementation

## Database
SQLite `backend/app/database/fresho_buddy.db`, table `pantry_history`.

## Timing anchors
- `added_at` — UTC when item entered pantry
- `estimated_quality_days` — initial window from analysis (not invented)
- `estimated_end_at` — `added_date + estimated_quality_days` (end 23:59:59 UTC)
- `legacy_timing` — 1 for rows backfilled from old `remaining_days` snapshots

## Dynamic remaining days
`pantry_state_service.compute_remaining_days_from_end_at`:
`max(0, (estimated_end_date - today_utc_date).days)`

## Single source
`get_current_pantry_state(user_id)` — History, Dashboard (via API), FreshoBuddy, Eat First enrichment.

## Seeding
Production seed (Mango/Cantaloupe/Watermelon) removed.

## Auth
Backend SQLite `users` + `auth_sessions`; Bearer token required for `/api/history` and FreshoBuddy.
