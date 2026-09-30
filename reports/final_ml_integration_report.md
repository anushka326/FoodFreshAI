# FoodFresh AI ML integration completion report

Date: 2026-09-30

## Freshness models

Production remains Freshness V2 (fine-tuned ResNet-18). The saved V3 EfficientNet-B0 completed training, but its trainer-reported test metrics (93.65% accuracy, 0.9357 macro F1) did not reproduce. Evaluation of the saved checkpoint against the same 2,173-example held-out split produced 82.60% accuracy and 0.8212 macro F1. V2 scored 96.04% accuracy and 0.9605 macro F1 on that split, so V3 was not promoted. See `freshness_model_v3_evaluation.md` for per-class metrics, confusion matrices, calibration, and the unresolved discrepancy.

Temperature scaling fitted on validation data was integrated for V2 at T=1.111828. It lowered held-out ECE from 0.0231 to 0.0196 and NLL from 0.1523 to 0.1426. Backend health and result version fields now identify the active V2 checkpoint consistently.

## Shelf-life model candidate

The interval classifier candidate, `models/candidates/shelf_life_interval_efficientnet_b0.pth`, predicts one of 24 food-by-freshness-stage classes derived from the dataset taxonomy. It achieved 94.29% test interval accuracy and 0.9430 macro F1 on 2,173 held-out examples. The best validation checkpoint was epoch 7, at 95.07% accuracy.

The dataset provides taxonomy-level shelf-life ranges, but no image-level observed remaining days, age, or storage conditions. These metrics measure interval-class agreement only; MAE, RMSE, and R² would be misleading. FoodKeeper remains the active production baseline, and this candidate is not integrated or promoted.

## Application and persistence

An authenticated local HTTP smoke flow passed with a tomato image: registration/login, hybrid food identification, calibrated freshness inference, FoodKeeper lookup, saving and reloading pantry history, deterministic eat-first/why chat, chat history persistence, and data persistence after logout/login. Freshness model version reporting was corrected to agree with the active V2 service. Frontend and backend health endpoints returned HTTP 200. Browser automation was unavailable.

Read-only SQLite verification confirmed all seven expected tables and all 14 checked pantry fields. Final counts: 37 pantry records, 6 users, 12 conversations, 34 messages, and 0 ML feedback records. Test-created data was left intact.

## Verification

- Focused regression suite: 30 passed.
- Python syntax compilation: passed for changed backend, model, and integration scripts.
- Frontend production build: passed earlier in the run.
- Full pytest collection did not complete because scratch modules perform network work during collection and the system Python lacks Torch for vision tests.
- Existing working tree changes were preserved. No commit, push, or remote operation was performed.

Related details: `codex_continuation_audit.md`, `freshness_model_v3_evaluation.md`, `shelf_life_model_training.md`, `shelf_life_model_evaluation.md`, `production_model_smoke_test.md`, `application_e2e_test.md`, and `database_verification.md`.
