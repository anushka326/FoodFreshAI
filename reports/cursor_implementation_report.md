# FoodFresh AI — Architecture Implementation Report

**Date:** 2025-09-30  
**Scope:** Real-time pantry countdown, backend auth, FreshoBuddy grounding, Try Demo removal  
**Git:** No commits, no pushes (per request)

---

## 1. Actual database used

**SQLite** — single file: `backend/app/database/fresho_buddy.db`  
Same database as the audit; extended in place (no second DB).

---

## 2. Tables / schema

| Table | Purpose |
|--------|---------|
| `users` | **NEW** — `user_id`, `email`, `password_hash`, `full_name`, `household_type`, `created_at` |
| `auth_sessions` | **NEW** — bearer session tokens, `expires_at`, FK to `users` |
| `pantry_history` | Pantry/analysis records — **extended columns** (see below) |
| `conversations` | FreshoBuddy threads (unchanged) |
| `messages` | Chat messages (unchanged) |
| `pantry_meta` | Legacy; seeding no longer used in production paths |

### Pantry schema extensions (migration in `chat_db._migrate_schema`)

| Column | Type | Purpose |
|--------|------|---------|
| `analysis_id` | TEXT | Links to analysis run id |
| `added_at` | TEXT UTC | Pantry countdown anchor |
| `estimated_quality_days` | INTEGER | Initial window at save (nullable) |
| `estimated_end_at` | TEXT UTC | Audit anchor (last quality day 23:59:59 UTC) |
| `freshness_state` | TEXT | Model label at save |
| `freshness_confidence` | REAL | Model confidence at save |
| `updated_at` | TEXT UTC | Last write |

Legacy rows backfilled: `added_at ← created_at`, `estimated_quality_days ← remaining_days`.

**Removed:** automatic Mango/Cantaloupe/Watermelon seed data for new users.

---

## 3. Authentication architecture

- **Backend:** `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`
- Passwords: PBKDF2-SHA256 (120k iterations) + per-user salt
- Sessions: random `sess_*` tokens in `auth_sessions` (30-day TTL)
- **Frontend:** `Authorization: Bearer <token>` on pantry + FreshoBuddy APIs
- **Enforcement:** `get_current_user` dependency; client-supplied `user_id` query params removed from protected routes
- **Removed:** `loginAsDemo()`, landing/login Try Demo buttons

---

## 4. Pantry architecture

```
Analyze → save (added_at + estimated_quality_days + estimated_end_at + metadata)
       → GET /api/history → pantry_state_service.get_current_pantry_state()
       → enrich each row (remainingDays, priority, qualityPeriod)
       → History / Dashboard / FreshoBuddy
```

Central service: `backend/app/services/pantry_state_service.py`

---

## 5. Remaining-days calculation

UTC **calendar-day** math:

```text
elapsed_days = (today_utc_date - added_at_utc_date).days  // clamp elapsed >= 0
remaining_days = max(0, estimated_quality_days - elapsed_days)
```

If `estimated_quality_days` is null (shelf-life unavailable at save):

- `remaining_days = null`
- UI string: **"Remaining quality cannot currently be estimated."**

`estimated_end_at` retained for audit; not overwritten when remaining hits 0.

### Example (Green Chilli, added 30 Sep, 5-day window)

| UTC date | Remaining |
|----------|-----------|
| 30 Sep | 5 |
| 1 Oct | 4 |
| 2 Oct | 3 |
| 3 Oct | 2 |
| 4 Oct | 1 |
| 5 Oct | 0 |

No re-analysis required.

---

## 6. Files changed (primary)

**Backend**

- `backend/app/database/chat_db.py` — migrations, users/sessions, pantry save/load, seed removed
- `backend/app/services/pantry_state_service.py` — **new**
- `backend/app/services/auth_service.py` — **new**
- `backend/app/deps/auth.py` — **new**
- `backend/app/routes/auth.py` — **new**
- `backend/app/routes/pantry_history.py` — auth + dynamic pantry
- `backend/app/routes/fresho_buddy.py` — auth; no client pantry override
- `backend/app/services/fresho_intent_service.py` — **new** (NLP-style intents + context levels)
- `backend/app/services/fresho_buddy_service.py` — DB pantry, intents, follow-ups
- `backend/app/services/pantry_triage_service.py` — slightly-spoiled copy; unknown remaining handling
- `backend/app/main.py` — auth router

**Frontend**

- `frontend/src/services/authService.js` — backend auth
- `frontend/src/services/storageUtils.js` — token + headers
- `frontend/src/services/historyService.js` — bearer API
- `frontend/src/services/freshoBuddyService.js` — bearer API
- `frontend/src/services/roadmapService.js` — rebuild from pantry on load
- `frontend/src/hooks/useFoodFresh.js` — dashboard/history sync
- `frontend/src/config/api.js` — auth endpoints
- `frontend/src/pages/LandingPage/LandingPage.jsx` — Try Demo removed
- `frontend/src/pages/LoginPage/LoginPage.jsx` — demo login removed
- `frontend/src/pages/FreshoBuddyPage/FreshoBuddyPage.jsx` — auth API calls

**Tests**

- `tests/test_pantry_countdown.py`
- `tests/test_fresho_buddy_intents.py`
- `tests/test_auth_user_isolation.py`

---

## 7. API changes

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/auth/register` | No | Returns token + user |
| POST | `/api/auth/login` | No | Returns token + user |
| GET | `/api/auth/me` | Bearer | Current user |
| POST | `/api/auth/logout` | Optional Bearer | Deletes session |
| GET | `/api/history` | Bearer | Dynamic remaining days |
| GET | `/api/history/pantry` | Bearer | Alias |
| POST | `/api/history` | Bearer | Body: `{ item }` only |
| DELETE | `/api/history/{id}` | Bearer | Owner only |
| GET/POST/DELETE | `/api/fresho-buddy/...` | Bearer | No `userId` in body |

ML route `/api/food-recognition/predict` unchanged (not modified).

---

## 8. FreshoBuddy changes

- Pantry always loaded via `get_current_pantry_state(user_id)` (server time)
- Intent layers: **SIMPLE / MEDIUM / STRONG** (`fresho_intent_service.py`)
- Deterministic answers first; Gemini explains grounded context only
- Follow-ups: “that one” / “store it” resolved from last assistant recommendation
- Client `pantryItems` payload removed (no stale cache)

---

## 9. NLP intent handling

Normalized text + phrase rules → intents such as `PANTRY_PRIORITY`, `PANTRY_LIST`, `EXPIRING_SOON`, `COOK_TODAY`, `STORAGE_ADVICE`, `FRESHNESS_EXPLANATION`, `FOOD_WASTE`, `GENERAL_FOOD_QUESTION`, `FOLLOW_UP`.

Mapped to existing deterministic triage in `pantry_triage_service.py`.

---

## 10. Gemini integration

- Still loaded only in `fresho_buddy_service.py` from `GEMINI_API_KEY` / `.env`
- **Not** exposed to frontend (no Vite env, no token in browser storage)
- Fallback to deterministic Markdown answers when Gemini unavailable

---

## 11. Chat persistence

Unchanged storage: SQLite `conversations` + `messages`, user-scoped by authenticated `user_id`.

---

## 12. Try Demo removal

- Landing navbar: **Try Demo** button removed
- Login: **Explore with Demo Kitchen Account** removed
- `loginAsDemo` removed from production auth flow

---

## 13. Tests performed

```bash
python -m pytest tests/test_pantry_countdown.py tests/test_fresho_buddy_intents.py tests/test_auth_user_isolation.py -q
```

**Result:** 10 passed

**Not browser-automated:** full UI walkthrough (manual verification recommended).

---

## 14. Commands executed

- `pip install pytest`
- `python -m pytest tests/...` (above)
- `npm run dev` (frontend)
- `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` (failed on this machine without `torch` in active Python env)

---

## 15. URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000/ |
| Backend (intended) | http://127.0.0.1:8000/ |

---

## 16. Remaining issues

1. **Full backend startup** on the test machine requires project ML deps (`torch`, etc.) per `requirements.txt` — pantry/auth/FreshoBuddy code paths import cleanly without ML when food router is not loaded.
2. **`google-genai`** should be installed in the backend venv for Gemini (not listed in root `requirements.txt` previously).
3. **Legacy localStorage-only users** must **register/login** again to obtain backend tokens.
4. **Eat First roadmap** still stored in localStorage for “completed” state; **active** cards rebuild from server pantry on each dashboard/history load.
5. **ML freshness/shelf-life models** intentionally not retrained; unknown shelf-life at save stays unknown.

---

## Acceptance checklist (summary)

| Criterion | Status |
|-----------|--------|
| SQLite reused, extended | Yes |
| Dynamic remaining days (UTC) | Yes |
| Backend authoritative timing | Yes |
| User-specific pantry + chat | Yes (Bearer + DB) |
| Try Demo removed | Yes |
| Gemini backend-only | Yes |
| ML models unchanged | Yes |
| Automated pantry/intent tests | Yes (10) |
| Full stack running on CI machine | Partial (frontend OK; backend needs torch env) |
