# FoodFresh AI — Fruits-360 Preparation Report

## 1. Dataset Location
- **Base Dataset Path:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\fruits-360-100x100-main`
- **Training Directory:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\fruits-360-100x100-main\Training`
- **Test Directory:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\fruits-360-100x100-main\Test`
- **Processed Manifests Directory:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360`

---

## 2. Original Dataset Statistics
- **Total Original Class Count:** **262 classes** in Training, **262 classes** in Test (263 distinct folder names across splits due to casing: `BlackBerry 4` vs `Blackberry 4`).
- **Total Original Training Images:** **138,642**
- **Total Original Test Images:** **46,196**
- **Total Original Images:** **184,838**
- Complete class inventory saved to [`reports/fruits360_original_classes.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_original_classes.csv).

---

## 3. Food-Level Mapping
The fine-grained botanical and variety classes in Fruits-360 (e.g. `Apple Braeburn 1`, `Apple Crimson Snow 1`, `Apple Golden 1-3`, `Apple Granny Smith 1`, `Apple Pink Lady 1`, `Apple Red 1-3`, etc.) were systematically grouped into broad produce categories using deterministic botanical noun extraction and known multi-word rules:
- **Total Derived Food Categories:** **81** high-level food groups.
- No semantic guessing was performed; distinct produce items (such as Apple vs Pear or Grapefruit vs Grape) remain separate.
- Full mapping inventory saved to [`reports/fruits360_food_mapping.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_food_mapping.csv) and [`data/processed/fruits360/original_to_food.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/original_to_food.json).

---

## 4. Fruits-360 + AgriFreshNET Overlap
Cross-dataset analysis against AgriFreshNET shows exactly **7 overlapping produce categories**:

| Food | Fruits-360 Classes | Fruits-360 Images | AgriFreshNET Classes | AgriFreshNET Images | AgriFreshNET Freshness Coverage |
| --- | --- | --- | --- | --- | --- |
| **Banana** | 5 | 2,562 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Bittermelon** | 0 | 0 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Cucumber** | 12 | 8,290 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Eggplant** | 2 | 944 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Orange** | 5 | 4,427 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Papaya** | 2 | 1,621 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Pineapple** | 2 | 1,312 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |
| **Tomato** | 19 | 13,672 | 3 | 1,770 | Full (Fresh + Semi-Fresh + Rotten) |


*Note:* `Bittermelon` is unique to AgriFreshNET and does not exist in Fruits-360.

---

## 5. Initial Food Recognition Set
To build an effective, high-performing initial food-recognition model, an **INITIAL FOOD RECOGNITION SET** of **12 normalized food categories** was selected based on measurable criteria:
1. **Core Priority 1:** All 7 produce categories present in both Fruits-360 and AgriFreshNET (`Banana`, `Cucumber`, `Eggplant`, `Orange`, `Papaya`, `Pineapple`, `Tomato`).
2. **Core Priority 2:** Top high-volume staple supermarket produce items in Fruits-360 (`Apple`, `Grape`, `Peach`, `Pear`, `Pepper`) that provide substantial visual diversity and match USDA FoodKeeper storage categories.

| Food Category | Fruits-360 Classes | Training Images | Test Images | Total Images | AgriFreshNET Overlap | Selection Reason |
| --- | --- | --- | --- | --- | --- | --- |
| **Apple** | 30 | 16,571 | 5,506 | 22,077 | No | High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories. |
| **Banana** | 5 | 1,917 | 645 | 2,562 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Cucumber** | 12 | 6,225 | 2,065 | 8,290 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Eggplant** | 2 | 708 | 236 | 944 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Grape** | 8 | 4,599 | 1,538 | 6,137 | No | High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories. |
| **Orange** | 5 | 3,325 | 1,102 | 4,427 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Papaya** | 2 | 1,217 | 404 | 1,621 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Peach** | 7 | 4,803 | 1,597 | 6,400 | No | High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories. |
| **Pear** | 20 | 12,281 | 4,087 | 16,368 | No | High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories. |
| **Pepper** | 11 | 6,242 | 2,074 | 8,316 | No | High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories. |
| **Pineapple** | 2 | 983 | 329 | 1,312 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |
| **Tomato** | 19 | 10,259 | 3,413 | 13,672 | Yes (3 classes, 1770 imgs) | Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count. |


---

## 6. Selected Dataset Statistics
Across the 12 selected food categories:
- **Original Fruits-360 Classes Covered:** **123 classes** (46.9% of all Fruits-360 classes)
- **Selected Training Images:** **69,130** (49.86% of total Fruits-360 training images)
- **Selected Test Images:** **22,996** (49.78% of total Fruits-360 test images)
- **Total Selected Images:** **92,126**

---

## 7. Label Mapping
Deterministic alphabetical indexing was established for the 12 classes:

```json
{
  "0": "Apple",
  "1": "Banana",
  "2": "Cucumber",
  "3": "Eggplant",
  "4": "Grape",
  "5": "Orange",
  "6": "Papaya",
  "7": "Peach",
  "8": "Pear",
  "9": "Pepper",
  "10": "Pineapple",
  "11": "Tomato"
}
```

The mapping is saved in [`data/processed/fruits360/label_map.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/label_map.json) with bidirectional lookup (`id_to_food` and `food_to_id`).

---

## 8. Manifest Structure
Two CSV manifest files were generated referencing the original raw image paths without copying any files:
- **Training Manifest:** [`data/processed/fruits360/fruits360_train_manifest.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/fruits360_train_manifest.csv) (69,130 rows)
- **Test Manifest:** [`data/processed/fruits360/fruits360_test_manifest.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/fruits360_test_manifest.csv) (22,996 rows)
- **Manifest Columns:**
  `image_path, original_class, normalized_food, split, label_id`

---

## 9. Validation Results
Full automated validation was executed across every manifest record:
- **Missing Training Files:** 0
- **Missing Test Files:** 0
- **Duplicate Paths in Training:** 0
- **Duplicate Paths in Test:** 0
- **Train / Test Overlap (Data Leakage):** 0 (0 overlapping files)
- **Invalid Labels:** 0
- **Validation Status:** `train_manifest_valid = True`, `test_manifest_valid = True`
- Detailed validation output saved in [`reports/fruits360_manifest_validation.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_manifest_validation.json).

---

## 10. Class Balance
Class distribution across the 12 normalized food categories:

| Normalized Food | Training Images | % of Train | Test Images | % of Test | Total Images |
| --- | --- | --- | --- | --- | --- |
| **Apple** | 16,571 | 23.97% | 5,506 | 23.94% | 22,077 |
| **Banana** | 1,917 | 2.77% | 645 | 2.8% | 2,562 |
| **Cucumber** | 6,225 | 9.0% | 2,065 | 8.98% | 8,290 |
| **Eggplant** | 708 | 1.02% | 236 | 1.03% | 944 |
| **Grape** | 4,599 | 6.65% | 1,538 | 6.69% | 6,137 |
| **Orange** | 3,325 | 4.81% | 1,102 | 4.79% | 4,427 |
| **Papaya** | 1,217 | 1.76% | 404 | 1.76% | 1,621 |
| **Peach** | 4,803 | 6.95% | 1,597 | 6.94% | 6,400 |
| **Pear** | 12,281 | 17.77% | 4,087 | 17.77% | 16,368 |
| **Pepper** | 6,242 | 9.03% | 2,074 | 9.02% | 8,316 |
| **Pineapple** | 983 | 1.42% | 329 | 1.43% | 1,312 |
| **Tomato** | 10,259 | 14.84% | 3,413 | 14.84% | 13,672 |


- **Minimum Training Count:** 708 images (`Eggplant`)
- **Maximum Training Count:** 16,571 images (`Apple`)
- **Mean Training Count:** 5,760.83 images
- **Median Training Count:** 4,701.0 images
- **Minimum Test Count:** 236 images (`Eggplant`)
- **Maximum Test Count:** 5,506 images (`Apple`)
- **Imbalance Ratio:** **23.41** (Natural variation due to variety count; Apple has 30 sub-varieties while Eggplant has 2 sub-varieties).
- *Note:* No artificial oversampling or undersampling was performed, preserving original image distributions. Class weights or stratified sampling can be utilized during training.

---

## 11. Dataset Limitations
1. **Turntable Capture Condition:** Fruits-360 images were captured on white backgrounds rotated on a motor axis, which differs from kitchen table backgrounds. Data augmentation (color jitter, rotation, random background blend) will be critical during model training.
2. **Resolution:** Original Fruits-360 images are 100 $\times$ 100 pixels, requiring bilinear/bicubic resizing to 224 $\times$ 224 for EfficientNet-B0 inputs.
3. **Category Imbalance:** Food categories with many sub-varieties (Apple, Pear, Tomato) contain higher image volumes than single/dual-variety foods (Eggplant, Papaya, Pineapple).
4. **Non-Selected Classes:** 139 Fruits-360 classes were excluded from the initial 12-class recognition set to prioritize clean convergence on core kitchen produce. All 139 excluded classes remain intact in raw storage.

---

## 12. Next Step
The next stage will configure the PyTorch `Dataset` and `DataLoader` pipelines for the 12-class initial food-recognition model using the validated manifests, followed by setting up the EfficientNet-B0 transfer learning architecture.
