# FoodFresh AI — Freshness Classification Pipeline Preparation Report
**Step 10: AgriFreshNET Freshness Pipeline & Manifest Preparation**

> Freshness model preparation is complete, but the freshness model has NOT been trained yet.

---

## 1. Dataset Path
- **Raw Root Path:** `data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase/Processed Data/Processed Data`
- **Processed Artifacts Path:** `data/processed/agrifreshnet/`

---

## 2. Number of Images
- **Total Images:** 14,160
- **Total Classes/Folders in Raw Dataset:** 24 folders (590 images each)

---

## 3. Number of Food Types
- **Total Distinct Produce Varieties:** 8
- **Varieties:**
  1. Banana (1,770 images)
  2. Bittermelon (1,770 images)
  3. Cucumber (1,770 images)
  4. Eggplant (1,770 images)
  5. Orange (1,770 images)
  6. Papaya (1,770 images)
  7. Pineapple (1,770 images)
  8. Tomato (1,770 images)

---

## 4. Fresh Count
- **Fresh Images:** 4,720 (33.33%)
- **Distribution:** Exactly 590 images across each of the 8 food varieties.

---

## 5. Semi-Fresh Count
- **Semi-Fresh Images:** 4,720 (33.33%)
- **Distribution:** Exactly 590 images across each of the 8 food varieties.

---

## 6. Rotten Count
- **Rotten Images:** 4,720 (33.33%)
- **Distribution:** Exactly 590 images across each of the 8 food varieties.

---

## 7. Train / Validation / Test Counts

| Split | Image Count | Percentage | Base Stems | Leakage Count |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 9,856 | 69.60% | 3,595 | 0 |
| **Validation** | 2,131 | 15.05% | 794 | 0 |
| **Test** | 2,173 | 15.35% | 799 | 0 |
| **Total** | **14,160** | **100.00%** | **5,188** | **0** |

### Freshness Distribution Across Splits
| Freshness Stage | Train Count | Validation Count | Test Count | Total Count |
| :--- | :---: | :---: | :---: | :---: |
| **Fresh** | 3,296 | 699 | 725 | 4,720 |
| **Semi-Fresh** | 3,295 | 709 | 716 | 4,720 |
| **Rotten** | 3,265 | 723 | 732 | 4,720 |

---

## 8. Split Strategy
- **Grouped Stratified Split:**
  - Grouping unit is the base image identifier (`base_stem`, removing `aug_<digits>_` prefixes).
  - All augmented variations derived from the same base camera exposure are kept together in exactly one split.
  - Stratified cumulative assignment ensures balanced proportions across all `(food_type, freshness_label)` combinations.
  - **Leak-Free Verification:** `train ∩ val = ∅`, `train ∩ test = ∅`, `val ∩ test = ∅` (0 stem overlap).

---

## 9. Random Seed
- **Fixed Random Seed:** `42` across Python, NumPy, and PyTorch.

---

## 10. Canonical Label Mapping
- **File:** `data/processed/agrifreshnet/freshness_label_map.json`
```json
{
  "freshness_to_id": {
    "Fresh": 0,
    "Semi-Fresh": 1,
    "Rotten": 2
  },
  "id_to_freshness": {
    "0": "Fresh",
    "1": "Semi-Fresh",
    "2": "Rotten"
  },
  "num_classes": 3
}
```

---

## 11. Invalid / Corrupted Image Count
- **Corrupted / Unreadable Images:** **0**
- All 14,160 images were validated with PIL verification and confirmed valid 3-channel RGB images with uniform 512x512 resolution.

---

## 12. Manifest Paths
- **Train Manifest:** `data/processed/agrifreshnet/freshness_train_manifest.csv` (9,856 rows)
- **Validation Manifest:** `data/processed/agrifreshnet/freshness_val_manifest.csv` (2,131 rows)
- **Test Manifest:** `data/processed/agrifreshnet/freshness_test_manifest.csv` (2,173 rows)
- **Config JSON:** `data/processed/agrifreshnet/freshness_config.json`
- **Balance CSV:** `reports/freshness_dataset_balance.csv`

Manifest columns: `image_path,food_type,freshness_label,freshness_id,original_class,base_stem`

---

## 13. Dataset Loader
- **Class:** `FreshnessDataset` in `ml/freshness/dataset.py`
  - Loads manifests, converts images to RGB, executes transforms, and returns `(image_tensor, label_id)` or metadata tuples.
- **Factory:** `create_freshness_data_loaders(config)` creates PyTorch DataLoaders with `pin_memory` and Windows-safe worker configuration (`num_workers=0`).

---

## 14. Transform Strategy
- **File:** `ml/freshness/transforms.py`
- **Input Dimensions:** `224 × 224` (EfficientNet-B0 standard).
- **Normalization:** ImageNet mean (`[0.485, 0.456, 0.406]`) and standard deviation (`[0.229, 0.224, 0.225]`).
- **Conservative Training Augmentation:**
  - `RandomHorizontalFlip(p=0.5)`
  - `RandomRotation(degrees=10)`
  - Subtle `ColorJitter(brightness=0.05, contrast=0.05, saturation=0.05)`: Strictly constrained to prevent washing out or artificially fabricating mold/rot coloration.
- **Evaluation Transforms:** Deterministic Resize + ToTensor + Normalization.

---

## 15. EfficientNet-B0 Architecture
- **Factory:** `create_freshness_model(num_classes=3, pretrained=True)` in `ml/freshness/model.py`.
- **Pretrained Weights:** Official TorchVision `EfficientNet_B0_Weights.DEFAULT`.
- **Classification Head:**
  - `Dropout(p=0.2)`
  - `Linear(in_features=1280, out_features=3)`

---

## 16. Number of Output Classes
- **Total Classes:** Exactly **3** (`Fresh`, `Semi-Fresh`, `Rotten`).

---

## 17. Training Configuration Prepared
- **Module:** `ml/freshness/config.py`
  - `batch_size`: 64
  - `image_size`: 224
  - `learning_rate`: 1e-3 (head tuning)
  - `fine_tune_learning_rate`: 1e-4 (backbone tuning)
  - `weight_decay`: 1e-4
  - `stage_1_epochs`: 3
  - `stage_2_epochs`: 2
  - `optimizer`: AdamW
  - `scheduler`: CosineAnnealingLR
  - `loss`: CrossEntropyLoss
  - `target_checkpoint`: `models/trained/freshness_classifier.pth`
- **Script:** `ml/freshness/train.py` (Prepared, NOT executed).

---

## 18. Evaluation Configuration Prepared
- **Script:** `ml/freshness/evaluate.py` (Prepared, NOT executed).
- **Outputs to be computed upon future training:**
  - Accuracy, Precision, Recall, Macro F1.
  - 3x3 Confusion Matrix.
  - Per-class precision, recall, and F1.
  - Sample predictions CSV (`reports/freshness_sample_predictions.csv`).

---

## 19. Architecture Smoke-Test Result
- **Execution Script:** `scripts/test_freshness_pipeline.py`
- **Output Shape Verified:** `(1, 3)`
- **Numerical Stability:** 0 NaN, 0 Inf values.
- **Untrained Checkpoint Saved:** **NO** (verified `freshness_classifier.pth` does NOT exist).
- **All 13 pipeline checks:** **PASS**.

---

## 20. Known Limitations
1. **Limited Food Domain in AgriFreshNET:** AgriFreshNET contains only 8 food varieties. While Fruits-360 handles broad food category classification (12 classes currently deployed), freshness estimation is grounded in these 8 core produce items.
2. **Controlled Studio Lighting:** AgriFreshNET images were captured in controlled conditions on neutral backgrounds; future real-world kitchen deployments may benefit from test-time domain adaptation.
3. **Downstream Systems Not Connected:** FoodKeeper, XGBoost shelf-life, Gemini FreshoBuddy, and backend freshness APIs remain strictly unintegrated per Step 10 constraints.
