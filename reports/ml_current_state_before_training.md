# FoodFreshAI: ML Current State Before Training
**Audit Date:** 2026-09-30
**Purpose:** Document exact architecture and models before implementing improvements

---

## PART 0: REPOSITORY AUDIT FINDINGS

### 1. Project Architecture Overview

**Frontend:** React 19 + Vite 6 + TailwindCSS
- Location: `frontend/src/`
- Main flow: AnalyzeFoodPage → analysisService → Backend API

**Backend:** FastAPI + Uvicorn
- Location: `backend/app/`
- Main inference: `/api/food-recognition/predict` → FoodRecognitionService → HybridVisionPipeline

**ML Pipeline:** Hybrid Vision Pipeline (Master V1)
- Location: `ml/hybrid_vision/`
- Components:
  1. Grounding DINO (object detection)
  2. Raw Food ResNet-50 (specialist classifier)
  3. SigLIP 2 (zero-shot semantic)
  4. Freshness ResNet-18 (freshness prediction)
  5. FoodKeeperService (shelf-life heuristics)
  6. Eat First Service (priority ranking)

**Database:** SQLite
- Location: `backend/app/database/fresho_buddy.db`
- Schema: users, auth_sessions, conversations, messages, pantry_history, ml_feedback

---

## PART 1: CURRENT FOOD RECOGNITION MODEL

**Status:** ✅ Active
**Type:** Hybrid Vision Pipeline
**Components:**

1. **Grounding DINO** (IDEA-Research/grounding-dino-base)
   - Path: `models/pretrained/grounding_dino/`
   - Purpose: Open-vocabulary object detection
   - Loaded: Yes

2. **Raw Food ResNet-50** (ibrahimdaud/raw-food-recognition-models)
   - Path: `models/pretrained/raw_food_resnet50/`
   - Classes: 90 raw food categories
   - Loaded: Yes

3. **SigLIP 2** (google/siglip2-base-patch16-224)
   - Path: `models/pretrained/siglip2/`
   - Purpose: Zero-shot semantic classification
   - Loaded: Yes

**Fusion Engine:**
- Rule 1: Direct top-1 agreement → SUCCESS
- Rule 2: Cross-model support (top-3) → SUCCESS
- Rule 3: Detector support → SUCCESS
- Rule 4: Contradictory evidence → UNCERTAIN
- Rule 5: Low confidence <30% → UNCERTAIN

**Inference Code:**
- `ml/hybrid_vision/hybrid_pipeline.py`
- `backend/app/services/food_recognition_service.py`

---

## PART 2: CURRENT FRESHNESS MODEL

**Status:** ⚠️ Partially Implemented
**Type:** ResNet-18 with fastai-style head

**Primary Model:** ResNet-18 (AgriFreshNET Fine-Tuned V2)
- Checkpoint: `models/trained/freshness_model_v2.pth`
- Status: EXISTS (but may not be properly trained)
- Architecture: ResNet-18 body + AdaptiveConcatPool2d + Flatten + BatchNorm + Linear head
- Classes: fresh, slightly_spoiled, rotten
- Calibration: Confidence gating (top_score <50% or margin <10% → uncertain)

**Fallback Model:** nathansekar/food-freshness-detector
- Path: `models/pretrained/freshness_resnet18/`
- Status: Falls back if V2 not available

**Inference Code:**
- `ml/hybrid_vision/freshness_service.py`

**Current Issues Documented:**
- Fresh green chilli → Misclassified as Rotten with very high confidence
- Dried chilli → Misclassified as Rotten 100%
- Unclear why existing V2 checkpoint has these failures

---

## PART 3: CURRENT SHELF-LIFE MODEL

**Status:** ❌ No ML Model
**Type:** Heuristic + USDA FoodKeeper Lookup Only

**Implementation:**
- File: `backend/app/services/shelf_life_service.py`
- Data: `data/raw/foodkeeper/FoodKeeper.json`
- Method: Canonical food name mapping → FoodKeeper product ID → Storage conditions

**Canonical Mapping Examples:**
```
"green chilli" → ID 548.0 "Hot peppers"
"dried chilli" → Same ID but form="dried" → "unavailable"
"bell pepper" → ID 296.0 "Peppers"
"apple" → ID 248.0 "Apples"
```

**Form-Based Gating:**
- Fresh whole produce → Lookup available
- Dried/powdered/processed/cooked → "Remaining quality cannot be estimated for this form"

**Issues:**
- No actual ML model for shelf-life
- Many foods not in FoodKeeper → "Not available"
- No support for dried chilli (form-gated to unavailable)
- No multi-storage-type modeling

---

## PART 4: DATASETS DISCOVERED

### AgriFreshNET Dataset

**Location:** `data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase/Processed Data/`

**Processed Manifests:** `data/processed/agrifreshnet/`
- `freshness_train_manifest.csv` - Training data with leakage-free splits
- `freshness_val_manifest.csv` - Validation data
- `freshness_test_manifest.csv` - Test data
- `freshness_label_map.json` - Class mappings
- `freshness_config.json` - Configuration

**Manifest Columns:**
```
image_path, food_type, freshness_label, freshness_id, original_class, base_stem
```

**Freshness Labels (verified in data):**
- Fresh (ID 0)
- Semi-Fresh (ID 1)
- Rotten (ID 2)

**Base Foods in Dataset (observed):**
- Banana (with state prefixes: "Fresh Banana(1-4)", "Semi-Fresh Banana", "Rotten Banana")
- And presumably others (Apple, Orange, Tomato, Mango, etc.)

**Image Format:**
- Augmented images: `aug_<number>_<original_filename>`
- Base stem tracking: Enables leakage-free train/val/test splits

### FoodKeeper Dataset

**Location:** `data/raw/foodkeeper/FoodKeeper.json`
**Format:** JSON with sheets containing categories and products
**Loaded:** Yes, by FoodKeeperService
**Contents:** 200+ food items with storage guidance

### Fruits-360 Dataset

**Location:** `data/raw/fruits-360-100x100-main/`
**Status:** Available but not currently used for freshness training

---

## PART 5: DATABASE SCHEMA (PRODUCTION)

**File:** `backend/app/database/fresho_buddy.db`

**Key Tables:**

### pantry_history
```sql
id, user_id, food_name, cultivar, status, status_category, quality_score,
quality_period, remaining_days, storage_environment, storage_type,
eat_first_priority, eat_first_score, eat_first_reason, guidance, image_src,
raw_metadata, analysis_id, added_at, estimated_quality_days, estimated_end_at,
freshness_state, freshness_confidence, updated_at, days_stored_at_analysis,
reference_min_days, reference_max_days, food_form, legacy_timing,
food_model_version, freshness_model_version, shelf_life_model_version, created_at
```

### ml_feedback
```sql
feedback_id, user_id, analysis_id, image_path, predicted_food,
predicted_food_confidence, predicted_food_form, predicted_freshness,
predicted_freshness_confidence, predicted_shelf_life,
user_corrected_food, user_corrected_food_form, user_corrected_freshness,
user_corrected_shelf_life, storage_type, days_stored,
feedback_source, review_status, created_at
```

### users, auth_sessions, conversations, messages
- Full authentication and chat persistence implemented

---

## PART 6: INFERENCE FLOW (CURRENT)

```
POST /api/food-recognition/predict
  ├─ Image validation (PIL readability)
  ├─ FoodRecognitionService.predict_image()
  │  └─ HybridVisionPipeline.analyze()
  │     ├─ Grounding DINO detection
  │     ├─ Crop + normalize
  │     ├─ Raw Food ResNet-50 inference
  │     ├─ SigLIP 2 inference
  │     ├─ Deterministic fusion
  │     ├─ Freshness ResNet-18 inference (V2 or fallback)
  │     ├─ FoodKeeperService shelf-life lookup
  │     ├─ Eat First priority calculation
  │     └─ Return complete analysis result
  │
  └─ format response
```

**Response Includes:**
- food_name, recognition_confidence
- freshness_label, freshness_confidence, freshness_model_version
- shelf_life (status, remaining, source)
- eat_first_priority, eat_first_score
- model_versions
- detectedObjects, topPredictions

---

## PART 7: API ENDPOINTS (CURRENT)

| Endpoint | Method | Status | Note |
|----------|--------|--------|------|
| `/api/food-recognition/predict` | POST | ✅ | Main inference |
| `/api/health` | GET | ✅ | Model status |
| `/api/history` | GET/POST | ✅ | Pantry management |
| `/api/fresho-buddy/chat` | POST | ✅ | FreshoBuddy chat |
| `/api/auth/register` | POST | ✅ | User registration |
| `/api/auth/login` | POST | ✅ | User login |

---

## PART 8: FRONTEND-TO-BACKEND API FLOW

**AnalyzeFoodPage.jsx:**
1. User uploads image
2. Calls `analysisService.analyzeSingleFood(image, {storage, daysInPantry})`
3. Sends FormData with file, storage_type, days_stored to `/api/food-recognition/predict`
4. Backend returns complete analysis
5. Frontend displays: food, confidence, freshness, shelf-life, eat-first
6. User can save to history

**Current Issue:**
- If shelf-life returns `status="unavailable"`, frontend shows "Not available"
- For many foods: No FoodKeeper match → shows "Not available"

---

## PART 9: PROTECTING REGRESSION CASES

**Fresh Green Chilli**
- Current behavior: Classified as Rotten with 99%+ confidence (WRONG)
- Expected: Fresh with reasonable confidence
- Regression test: YES (protected case)

**Dried Red Chilli**
- Current behavior: Classified as Rotten 100% (WRONG)
- Expected: Either Unsupported (form-aware) or proper dried classification
- Regression test: YES (protected case)

**Other Important Cases:**
- Moldy/visibly degraded orange
- Rotten tomato
- Bell pepper
- Potato
- Apple
- Pomegranate
- Mango

---

## PART 10: CURRENT MODEL_CONFIG.py STATE

```python
MODEL_CONFIG = {
    "food_recognition": {
        "status": "ACTIVE",
        "pipeline": "hybrid_pretrained_vision",
        "is_loaded": True
    },
    "freshness": {
        "status": "ACTIVE",
        "model_architecture": "resnet18_fastai_head",
        "model_version": "nathansekar/food-freshness-detector",  # ← Falls back here
        "is_loaded": True
    },
    "shelf_life": {
        "status": "AWAITING_INTEGRATION",
        "model_architecture": "xgboost_foodkeeper",
        "model_version": None,
        "checkpoint_path": None,
        "is_loaded": False
    }
}
```

---

## PART 11: EXISTING PREPROCESSING & TRAINING SCRIPTS

**Preprocessing:**
- `scripts/prepare_agrifreshnet.py` - Dataset preparation (already run)
- `ml/freshness/train_v2.py` - Freshness model training script

**Training Features (train_v2.py includes):**
- Corrupted image detection ✅
- Duplicate detection via base_stem ✅
- RGB conversion ✅
- Label normalization ✅
- Leak-free train/val/test splits ✅
- Augmentation (rotation, brightness, contrast) ✅
- Early stopping ✅
- Best model checkpointing ✅

**Status:** Script exists but model not verified to be properly trained

---

## PART 12: AUDIO

**Existing Models NOT Working Correctly:**
- Freshness V2 checkpoint exists but likely not trained properly (based on chilli failures)

**Missing Models:**
- Shelf-life ML model (only heuristics exist)
- Food form classification model (inferred from name only)

---

## PART 13: SUMMARY TABLE

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Food Recognition (Hybrid) | ✅ Working | `ml/hybrid_vision/` | Active, pretrained models |
| Freshness V2 (ResNet-18) | ⚠️ Questionable | `models/trained/freshness_model_v2.pth` | Exists but failures reported |
| Freshness Fallback | ✅ Available | `models/pretrained/freshness_resnet18/` | nathansekar model |
| Shelf-Life ML | ❌ Not Built | N/A | Only heuristics exist |
| FoodKeeper Heuristics | ✅ Working | `backend/app/services/shelf_life_service.py` | Lookup-based |
| Database | ✅ Ready | `backend/app/database/fresho_buddy.db` | Full schema implemented |
| Frontend | ✅ Ready | `frontend/src/` | All pages implemented |
| AgriFreshNET Data | ✅ Prepared | `data/processed/agrifreshnet/` | Manifests ready for training |

---

## NEXT STEPS

This audit establishes the baseline. The implementation will:

1. Train Freshness V3 (improved architecture, better evaluation)
2. Train Shelf-Life ML Model (multimodal)
3. Integrate both into production inference
4. Fix the chilli regression cases
5. Remove "Not available" for supported foods
6. Persist all predictions to SQLite
7. Real end-to-end testing

**Critical Objective:**
Replace vague "Not available" with actual ML-driven predictions.

