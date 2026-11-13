# HTTP end-to-end application smoke test

- Result: PASS
- Run: `12917088d3`
- SQLite: `backend/app/database/fresho_buddy.db`
- Browser automation: unavailable in this environment; this run exercises the same backend APIs and checks the frontend HTTP entry point.

## Steps

- Frontend HTTP 200; backend health HTTP 200.
- Registered a unique test account.
- Logged in and verified the authenticated account.
- Analyzed local image `data\real_world_eval\tomato.jpg`: Tomato; freshness Fresh; models {"detector": "IDEA-Research/grounding-dino-base", "food": "Hybrid Pretrained V1", "foodSpecialist": "ibrahimdaud/raw-food-recognition-models", "freshness": "AgriFreshNET Fine-Tuned ResNet-18 (V2)", "semantic": "google/siglip2-base-patch16-224", "shelfLife": "foodkeeper_rules_v1"}.
- Saved the actual analysis result to pantry history.
- Refetched history; record remains, remainingDays=7.
- Asked eat-first and why; both replies used deterministic DB-backed pantry triage and persisted conversation history.
- Logged out/in again; pantry record and chat remained available.

No secrets or password/token values are written to this report.
