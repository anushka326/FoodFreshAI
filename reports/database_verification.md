# Database Verification

- Verified: 2026-09-30T09:17:11.656192+00:00
- Database: `D:\VIT TY SEM5\ML Project\FOODFRESHAI\backend\app\database\fresho_buddy.db`
- Database size: 2,674,688 bytes
- Mode: read-only inspection; no rows or schema changed

## Tables

| Table | Rows | Columns |
|---|---:|---:|
| `auth_sessions` | 9 | 4 |
| `conversations` | 12 | 5 |
| `messages` | 34 | 7 |
| `ml_feedback` | 0 | 19 |
| `pantry_history` | 37 | 33 |
| `pantry_meta` | 7 | 2 |
| `users` | 6 | 6 |

## Persistence fields

Pantry history has 14/14 checked fields.
Missing checked fields: none.
Expected tables missing: none.

## Record counts

- Pantry records: 37
- ML feedback records: 0
- Analyses are represented in the existing `pantry_history` table; no separate analyses table exists.
