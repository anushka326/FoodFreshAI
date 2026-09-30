# FoodFresh AI — Synthetic Dataset Integration Report

**Date:** September 30, 2026  
**System:** FoodFresh AI Platform  
**Integration Status:** Successfully Integrated as Auxiliary Reference Resource  
**Training Status:** **NO MODEL TRAINING WAS PERFORMED**  

---

## 1. Executive Summary

Three synthetic dataset files located in `data/raw/Synthetic data/` have been integrated into the FoodFresh AI platform strictly as an **auxiliary, supporting reference and testing resource**.

The existing production architecture has been fully preserved:
- Existing trained model checkpoints in `models/trained/` were **NOT** retrained, modified, or overwritten.
- Real-world training datasets (**AgriFreshNET** and **Fruits-360**) remain the exclusive image sources for model development.
- Authoritative reference knowledge (**USDA FoodKeeper**) remains primary for canonical shelf-life rules.
- The SQLite persistent database (`backend/app/database/fresho_buddy.db`) was completely preserved without resets, migrations, or data alterations.
- Synthetic labels are explicitly marked as **rule-based synthetic prototypes** and are **never** presented as laboratory or medical ground truth.

---

## 2. Dataset Files & Structural Verification

| Property | Details |
| :--- | :--- |
| **Exact Directory** | `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\Synthetic data\` |
| **File 1 (Data CSV)** | `FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv` (11,107,116 bytes) |
| **File 2 (Schema JSON)** | `FoodFreshAI_Synthetic_Dataset_Schema.json` (1,310 bytes) |
| **File 3 (README)** | `FoodFreshAI_Synthetic_Dataset_README.md` (4,676 bytes) |
| **Total Rows** | 41,280 rows |
| **Total Columns** | 27 columns |
| **Missing Values** | 0 null values across all 41,280 rows |
| **Food Classes** | 43 classes across 2 domains (`produce`, `bakery`) |

### Detected Column Schema (27 fields)
1. `image_id`
2. `food_name`
3. `food_category`
4. `food_domain`
5. `food_form` (`whole`, `cut`, `sliced`, `diced`)
6. `lighting_condition` (`warm`, `backlit`, `high`, `normal`, `uneven`, `low`)
7. `brightness_index_0_100`
8. `background_type`
9. `camera_angle`
10. `image_quality`
11. `visibility_penalty`
12. `storage_type` (`countertop`, `refrigerated`)
13. `temperature_c`
14. `days_since_purchase`
15. `reference_max_days`
16. `visual_brownness_score`
17. `mold_spot_score`
18. `bruise_damage_score`
19. `wrinkle_wilt_score`
20. `texture_degradation_score`
21. `freshness_score_0_100`
22. `freshness_stage` (18 distinct stage labels)
23. `remaining_shelf_life_days` (0 to 15 days)
24. `shelf_life_source` (`SYNTHETIC_PROJECT_POLICY`)
25. `is_real_image` (`False`)
26. `is_training_ground_truth` (`False`)
27. `notes`

---

## 3. Data Role & Provenance Separation

The FoodFresh AI platform enforces strict taxonomy separation:

```
REAL IMAGE DATA (AgriFreshNET, Fruits-360)
  --> Used for computer vision training and validation.

EXISTING TRAINED MODELS (Grounding DINO, SigLIP 2, ResNet-50, Freshness ResNet-18 V2)
  --> Connected to production inference. Unaltered.

USDA FOODKEEPER (661 Products across 25 categories)
  --> Primary authoritative food storage guidance and reference windows.

SYNTHETIC STRUCTURED DATA (41,280 prototype rows)
  --> Auxiliary reference for testing, edge cases, food form capping, and policy calibration.
```

### Provenance Labeling
- **USDA FoodKeeper**: Authoritative empirical guidance.
- **FoodFresh AI Estimate**: Estimated remaining quality window based on visible freshness and FoodKeeper guidelines.
- **FoodFresh AI Synthetic Prototype Reference**: Auxiliary prototype scenarios for testing and edge cases.

---

## 4. Key Fixes & Policy Protections Implemented

1. **Elimination of Unrealistic 19-Day Fresh-Cut Apple Window**:
   - Integrated form-aware shelf-life constraints: fresh-cut produce (`food_form in ('cut', 'sliced', 'diced')`) is constrained to **1–2 days** on countertop, or **3–5 days** in crisper chill. Cut apple on countertop no longer returns whole-apple 21-day window.

2. **Elimination of 0-Day Fresh Watermelon Bug**:
   - Added zero-day protection for visibly fresh items: items stored for 0 days with `fresh` condition retain a minimum remaining window of at least 1 day rather than collapsing to 0.

3. **Produce Prototype Policy Constraints**:
   - Ambient countertop produce: constrained up to approximately 7 days.
   - Refrigerated crisper produce: constrained up to approximately 15 days.

4. **Canonical Produce Resolution Fixes**:
   - Fixed false substring matches in canonical table (e.g., `grape` matching `grapefruit`, `cherry` matching `cherry tomato`, `avocado` matching `avocado oil`).
   - Mapped `Avocados` (ID 250.0), `Grapes` (ID 261.0), `Cherries` (ID 483.0), `Carrots` (ID 279.0), `Onions` (ID 294.0), and `Garlic` (ID 285.0).

5. **Beetroot & Bakery Freshness Safeguards**:
   - Protected Beetroot from being falsely classified as "Rotten" due to its dark purple pigmentation and lack of AgriFreshNET model coverage.
   - Guarded Bakery items (`bread`, `bun`, `roti`, `toast`, `cake`) from receiving produce-specific "Rotten" labels, mapping them appropriately to `Stale` / `Mold Suspected`.

6. **Decoupled Lighting from Spoilage**:
   - Verified that image lighting conditions (`low`, `backlit`, `warm`, `uneven`) do not drive spoilage determinations.

---

## 5. Verification Checklist

| Requirement | Status | Confirmation |
| :--- | :--- | :--- |
| **No Model Training Started** | **CONFIRMED** | Zero training scripts run; no GPU/CPU training started. |
| **Models in `models/trained/` Unchanged** | **CONFIRMED** | `freshness_model_v2.pth` unchanged (46,916,994 bytes). |
| **SQLite Database Preserved** | **CONFIRMED** | `backend/app/database/fresho_buddy.db` preserved (3,399,680 bytes; all 7 tables intact). |
| **FoodKeeper Reference Preserved** | **CONFIRMED** | `FoodKeeper.json` remains primary shelf-life engine. |
| **AgriFreshNET Preserved** | **CONFIRMED** | Real image dataset intact; ResNet-18 V2 checkpoint intact. |
| **Synthetic Dataset Auxiliary** | **CONFIRMED** | Registered as auxiliary development reference; `is_training_ground_truth=False`. |
| **No Automatic Git Actions** | **CONFIRMED** | No `git add`, `git commit`, or `git push` executed. |

---

## 6. Automated Testing Results

- **Existing Unit & Regression Tests**: 31 passed (pantry countdown, FreshoBuddy intents, auth user isolation, food form regression, shelf-life regression).
- **Synthetic Integration Scenario Tests**: 19 passed across all 15 scenarios.
- **Combined Test Suite**: **50 passed in 0.77s**.
- **Smoke Inference Test**: `scripts/integration_test.py` completed with `PASS` (code 0).

---

## 7. Known Dataset Limitations

1. **No Image Pixels**: The synthetic dataset is a metadata CSV; it does not contain pixel data and cannot directly train image recognition models.
2. **Rule-Based Prototype Values**: Remaining days and defect scores in the synthetic dataset are synthetically generated heuristics; they must never be presented as laboratory measurements.
3. **Domain Coverage**: Synthetic data covers 43 commodities; items outside this set must continue to return transparent uncertainty states.
