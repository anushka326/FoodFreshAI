# FoodFresh AI continuation audit

**Audit date:** 2026-09-30 (Asia/Calcutta)  
**Scope:** Existing repository state before integration changes. Existing working-tree changes were preserved; no reset, commit, push, or remote change was made.

## Verified initial state

- Git branch was `main` with a large pre-existing modified/untracked working tree. No pre-existing edits were reverted.
- A Freshness V3 training process was active: `ml/freshness/train_efficientnet_v3.py` (PID 24764). It was found during the later process audit; its checkpoint continued changing while this audit ran. No second V3 training process was started.
- `models/candidates/freshness_v3_efficientnet_b0.pth` existed and loaded strictly into the configured three-class EfficientNet-B0 architecture. It is a raw state dict, with no epoch/history metadata. A training history CSV or final V3 report was absent. Candidate file was last observed updating at 12:16 local time while the trainer remained active.
- The first test evaluation of the then-current V3 checkpoint returned 88.68% accuracy, 88.38% macro F1, and 88.60% macro recall/balanced accuracy. These are preliminary because training was still active and may replace the checkpoint; see the evaluation report before treating these as final.
- Existing freshness production is the local fine-tuned ResNet-18 V2 at `models/trained/freshness_model_v2.pth`, with the Nathan Sekar model as fallback. The API freshness path is the hybrid pipeline, not `ml/freshness/predict.py`.
- No production shelf-life ML checkpoint exists. The live path uses USDA FoodKeeper lookup and freshness/storage-duration heuristics. Existing plan/report explicitly said shelf-life ML was not integrated.
- AgriFreshNET manifests contain 14,160 images: train 9,856, validation 2,131, test 2,173; eight produce types and three freshness stages, 4,720 examples per stage. All manifest paths resolve locally. Grouping by `base_stem` showed no stem crossing between splits. The source class names encode interval ranges; they do not supply image-specific elapsed storage time, storage conditions, temperature, or humidity.
- Existing food recognition is the hybrid Grounding DINO + SigLIP 2 + raw-food ResNet-50 pipeline. Food form is inferred separately by `food_form_service.py`. Exact runtime outputs remain to be verified once the application can run after V3 training.
- SQLite remains at `backend/app/database/fresho_buddy.db`. It initially contained seven tables, 27 pantry rows and no ML feedback rows. The saved schema has 33 pantry columns, including model version, freshness confidence/state, interval reference days, form, analysis ID, and estimated end time. Four additional `Food A`/`Food C` rows from the requested auth isolation tests were present after two explicit test runs; no records were deleted.
- The old `scripts/verify_database.py` assumed nonexistent columns (`freshness_label`, `confidence`, `feedback_status`) and failed. It was replaced with a read-only verifier against the actual schema; its report is `reports/database_verification.md`.
- No backend/frontend server was running at the initial process check. Frontend `node_modules` and Vite scripts are present. Browser automation tooling was not available in the environment.

## Final continuation results (2026-09-30)

- The Freshness V3 process completed 20 epochs. Its saved checkpoint loaded, but its claimed trainer test metrics could not be reproduced; same-split evaluation was 82.60% accuracy / 0.8212 macro F1 versus production V2 at 96.04% / 0.9605. V3 remains unpromoted. Details and confusion matrices: `freshness_model_v3_evaluation.md`.
- Validation-fitted temperature T=1.1118 is integrated for production V2. The V2 calibration improved held-out NLL from 0.1523 to 0.1426 and ECE from 0.0231 to 0.0196. Health reports the active checkpoint and temperature.
- Trained and evaluated an experimental 24-class shelf-life interval classifier. The selected epoch-7 checkpoint scored 94.29% test interval accuracy and 0.9430 macro F1 (2,173 examples). These are taxonomy interval-classification scores, not errors in remaining days. The FoodKeeper rules remain production and the candidate was not integrated.
- Freshness service predictions, calibration, API version reporting, health, and the local tomato real-image smoke flow were checked. The V2/V3 selected-image smoke results are in `production_model_smoke_test.md`; dried chilli had no local test image.
- Authenticated HTTP flow passed: register/login, tomato recognition, V2 freshness, FoodKeeper interval, save and reload pantry history, deterministic eat-first and why responses, chat persistence, and persistence after logout/login. See `application_e2e_test.md`. Browser automation was unavailable; frontend HTTP returned 200.
- Final read-only SQLite verification found 7 expected tables, all 14 checked pantry fields, 37 pantry rows, 6 users, 12 conversations, 34 messages, and 0 feedback rows. Test-created accounts and records were preserved.
- Focused regression suite: 30 passed. Python compile check passed. Frontend production build passed earlier in the run. Full pytest collection had unrelated network-dependent scratch modules and environment-specific Torch collection failures; see the session summary.
- Existing user working tree and database were preserved. No commit, push, or remote change was made.

## Initial audit notes (historical)

- Freshness V3 final evaluation and calibration must be rerun after the active trainer exits and the checkpoint stops changing.
- A shelf-life interval classifier was prepared using only the dataset's annotated food/stage interval classes. The first training attempt was stopped after discovering the existing V3 trainer, to avoid competing training. No shelf-life candidate was produced or promoted.
- Full application API inference, persistent save/reload, FreshoBuddy database reasoning, browser workflow, and final server startup remain unverified.
- `python -m pytest -q` did not complete: collection hit network-dependent scratch tests, scripts that are not test modules, and tests requiring Torch unavailable in the system Python. The explicitly requested relevant non-vision regression set passed 31 tests.
