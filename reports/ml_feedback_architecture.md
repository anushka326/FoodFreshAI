# ML Feedback Architecture

## Table: `ml_feedback` (SQLite)
Stores predictions, optional user corrections, `review_status`, `image_path` (filesystem).

## Image storage
`data/feedback/images/` (gitignored). SQLite holds path + metadata only.

## Manifest
`data/feedback/manifest.csv` — training-ready rows only when `validation_status=VALIDATED`.

## Workflow
COLLECTED → VALIDATED → TRAINING_READY → USED_FOR_TRAINING  
**No automatic training** from web requests.

## API
`POST /api/ml-feedback` (authenticated) — collect corrections.

## Offline training (future)
- Freshness: `ml/freshness/` scripts (candidate checkpoints under `models/trained/`, manual promotion)
- Shelf-life: separate experiment; see `reports/shelf_life_model_plan.md`
