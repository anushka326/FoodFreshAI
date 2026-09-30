# FoodFresh AI — ML Model Reset Inventory

**Inventory Date:** 2026-09-25  
**Auditor:** Antigravity AI  
**Scope:** Complete project audit of all ML model artifacts, weights, and checkpoints across the FoodFresh AI repository.

---

## 1. Inventory Summary

An exhaustive filesystem search for all model file extensions (`*.pth`, `*.pt`, `*.onnx`, `*.keras`, `*.h5`, `*.joblib`, `*.pkl`, `*.safetensors`) was conducted across the FoodFresh AI workspace.

| Metric | Count | Details |
|---|---|---|
| **Active Production Checkpoints** | 1 | `food_classifier_v2.pth` (currently referenced by backend) |
| **Obsolete Food Recognition Checkpoints** | 2 | `food_classifier.pth`, `food_classifier_backup.pth` |
| **Freshness Model Checkpoints** | 0 | None trained/saved in `models/` |
| **Shelf-Life Model Artifacts** | 0 | None trained/saved in `models/` |
| **Pretrained Weights (`models/pretrained/`)** | 0 | Directory exists but is empty |
| **Total Artifacts to Archive/Remove** | 3 | All 3 in `models/trained/` |

---

## 2. Model Artifact Details

### Checkpoint 1: Food Recognition V2 (Production)
- **Exact File Path:** `models/trained/food_classifier_v2.pth`
- **Model Name / Version:** Food Recognition V2 (EfficientNet-B0)
- **Purpose:** 24-class fruit & vegetable classification (Fruits-360 V2 dataset)
- **Size:** 48,948,925 bytes (~48.9 MB)
- **Connected to Production:** **YES** (loaded by `backend/app/services/food_recognition_service.py`)
- **Trained Locally:** Yes (trained using local RTX 4050 GPU via `ml/food_recognition_v2/train.py`)
- **Downloaded / Pretrained:** Pretrained EfficientNet-B0 backbone with custom fine-tuned head
- **Action Required:** **REMOVE & ARCHIVE** to `models/archive_old/trained/` (causes false classifications such as Pomegranate → Pear at 93.6% confidence)

### Checkpoint 2: Food Recognition V1
- **Exact File Path:** `models/trained/food_classifier.pth`
- **Model Name / Version:** Food Recognition V1 (12-class prototype)
- **Purpose:** Initial food recognition prototype
- **Size:** 41,823,598 bytes (~41.8 MB)
- **Connected to Production:** No (inactive)
- **Trained Locally:** Yes
- **Downloaded / Pretrained:** Pretrained backbone fine-tuned locally
- **Action Required:** **REMOVE & ARCHIVE** to `models/archive_old/trained/`

### Checkpoint 3: Food Recognition Backup Checkpoint
- **Exact File Path:** `models/trained/food_classifier_backup.pth`
- **Model Name / Version:** Food Recognition V1 Backup
- **Purpose:** Intermediate/backup weights from V1 experiment
- **Size:** 16,518,694 bytes (~16.5 MB)
- **Connected to Production:** No (inactive)
- **Trained Locally:** Yes
- **Downloaded / Pretrained:** Pretrained backbone fine-tuned locally
- **Action Required:** **REMOVE & ARCHIVE** to `models/archive_old/trained/`

---

## 3. Pretrained & Secondary Model Assets

- **`models/pretrained/`**: Verified empty. No obsolete pretrained models present.
- **Freshness Models**: No `.pth` checkpoint exists in `models/trained/` or `ml/freshness/`. Freshness pipeline has training code and transforms ready, but no active model artifact was linked to production.
- **Shelf-Life Models**: No `.joblib`, `.pkl`, or `.json` model artifact exists in `models/trained/` or `ml/shelf_life/`. FoodKeeper reference data (`FoodKeeper.json`) is intact and preserved.

---

## 4. Preservation Confirmation

The following critical non-model assets remain strictly untouched and preserved:
- `data/raw/` (AgriFreshNET, Fruits-360, FoodKeeper.json)
- `data/processed/`
- Training and evaluation scripts (`ml/food_recognition/`, `ml/food_recognition_v2/`, `ml/food_recognition_v3/`, `ml/freshness/`, `ml/shelf_life/`)
- Test scripts and dataset inspection tools
