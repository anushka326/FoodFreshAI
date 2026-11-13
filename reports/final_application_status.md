# Final Application Status

## Fixed
- `getAuthToken` import in `authService.js`
- Real-time pantry via `estimated_end_at`
- Backend-authoritative pantry for FreshoBuddy
- Try Demo removed; Household Pantry Scope removed from Register
- ML feedback table + API scaffold
- Food form separation; dried chilli shelf-life unavailable by design

## Auth
Real backend: password hash, sessions, Bearer tokens (development-grade, not enterprise SSO).

## URLs
- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8000 (use `.venv`)

## Inspect DB
`python scripts/inspect_database.py`

## Tests
`python -m pytest tests/test_pantry_countdown.py tests/test_fresho_buddy_intents.py tests/test_auth_user_isolation.py tests/test_food_form_regression.py tests/test_shelf_life_regression.py -q`
