# FoodFresh AI Dataset Inspection Report

## 1. Inspection Date/Time
- **Date & Time:** 2026-09-18 00:27:07
- **Inspection Type:** Safe READ-ONLY Programmatic Audit
- **Script Executed:** `scripts/inspect_datasets.py`

---

## 2. Dataset Locations

| Dataset | Filesystem Location | Status | Files / Records |
| --- | --- | --- | --- |
| **AgriFreshNET** | `data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase/Processed Data/Processed Data` | Complete & Readable | 14,160 images (24 classes) |
| **Fruits-360 (100x100)** | `data/raw/fruits-360-100x100-main` | Complete & Readable | 184,838 images (262 classes) |
| **USDA FoodKeeper** | `data/raw/foodkeeper/FoodKeeper.json` | Valid JSON | 661 product rows (6 sheets) |

---

## 3. AgriFreshNET

- **Filesystem Path:** `data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase/Processed Data/Processed Data`
- **Total Images:** 14,160
- **Class Folders:** 24 folders
- **Images per Class:** Exactly 590 images per class across all 24 classes (perfectly balanced).
- **Freshness Stage Distribution:**
  - `Fresh`: 4,720 images (8 classes)
  - `Semi-Fresh`: 4,720 images (8 classes)
  - `Rotten`: 4,720 images (8 classes)
- **Food Type Distribution (8 distinct foods, 1,770 images each):**
  - `Banana`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Bittermelon`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Cucumber`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Eggplant`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Orange`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Papaya`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Pineapple`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
  - `Tomato`: 1,770 images (3 stages: Fresh, Semi-Fresh, Rotten)
- **Shelf-Life Ranges Encoded:**
  - Range syntax: `(min-max)` in days.
  - Overall minimum shelf-life encoded: 1 day (Fresh Bittermelon, Fresh Papaya, Fresh Eggplant, Fresh Banana, Fresh Pineapple, Fresh Cucumber, Fresh Tomato, Fresh Orange).
  - Overall maximum shelf-life encoded: 35 days (Rotten Tomato, Rotten Orange, Rotten Pineapple).
- **Image Dimensions & Channels:**
  - Dimensions: Consistently `512x512` pixels across all sampled classes.
  - Color Mode: `RGB` (3 channels).
- **Image Formats:**
  - `.jpeg`: 270 files
  - `.jpg`: 13,890 files
- **Quality & Duplication Findings:**
  - Zero-byte files: 0
  - Unreadable / Corrupted images: 0
  - MD5 Hash Duplicates: 40 intra-class identical frames discovered (e.g. repeated exports such as `~2.jpg` and `~3.jpg` within `Fresh Banana(1-4)`).

### AgriFreshNET Class Structure Table

| Class Folder | Food | Freshness Stage | Shelf-Life Range | Image Count | Image Format | Sample Dimensions |
| --- | --- | --- | --- | --- | --- | --- |
| `Fresh Banana(1-4)` | Banana | Fresh | 1-4 days | 590 | .jpeg, .jpg | 512x512 |
| `Fresh Bittermelon(1-3)` | Bittermelon | Fresh | 1-3 days | 590 | .jpg | 512x512 |
| `Fresh Cucumber(1-6)` | Cucumber | Fresh | 1-6 days | 590 | .jpg | 512x512 |
| `Fresh eggplant(1-4)` | Eggplant | Fresh | 1-4 days | 590 | .jpeg, .jpg | 512x512 |
| `Fresh Orange(1-9)` | Orange | Fresh | 1-9 days | 590 | .jpeg, .jpg | 512x512 |
| `Fresh Papaya(1-4)` | Papaya | Fresh | 1-4 days | 590 | .jpg | 512x512 |
| `Fresh pineapple(1-15)` | Pineapple | Fresh | 1-15 days | 590 | .jpeg, .jpg | 512x512 |
| `Fresh Tomato(1-10)` | Tomato | Fresh | 1-10 days | 590 | .jpeg, .jpg | 512x512 |
| `Rotten banana(7-13)` | Banana | Rotten | 7-13 days | 590 | .jpg | 512x512 |
| `Rotten Bittermelon(5-8)` | Bittermelon | Rotten | 5-8 days | 590 | .jpg | 512x512 |
| `Rotten Cucumber(12-20)` | Cucumber | Rotten | 12-20 days | 590 | .jpg | 512x512 |
| `Rotten eggplant(8-15)` | Eggplant | Rotten | 8-15 days | 590 | .jpg | 512x512 |
| `Rotten Orange(20-35)` | Orange | Rotten | 20-35 days | 590 | .jpg | 512x512 |
| `Rotten Papaya(7-12)` | Papaya | Rotten | 7-12 days | 590 | .jpg | 512x512 |
| `Rotten Pineapple(25-35)` | Pineapple | Rotten | 25-35 days | 590 | .jpg | 512x512 |
| `Rotten Tomato(24-35)` | Tomato | Rotten | 24-35 days | 590 | .jpg | 512x512 |
| `Semi fresh banana(4-7)` | Banana | Semi-Fresh | 4-7 days | 590 | .jpg | 512x512 |
| `Semi Fresh Bittermelon ( 3-5)` | Bittermelon | Semi-Fresh | 3-5 days | 590 | .jpg | 512x512 |
| `Semi Fresh Cucumber(6-12)` | Cucumber | Semi-Fresh | 6-12 days | 590 | .jpg | 512x512 |
| `Semi fresh Orange(9-20)` | Orange | Semi-Fresh | 9-20 days | 590 | .jpg | 512x512 |
| `Semi Fresh Papaya(4-7)` | Papaya | Semi-Fresh | 4-7 days | 590 | .jpg | 512x512 |
| `Semi fresh Pineapple (15-25)` | Pineapple | Semi-Fresh | 15-25 days | 590 | .jpg | 512x512 |
| `Semi fresh Tomato(10-24)` | Tomato | Semi-Fresh | 10-24 days | 590 | .jpg | 512x512 |
| `Semi_Fresh eggplant(4-8)` | Eggplant | Semi-Fresh | 4-8 days | 590 | .jpeg, .jpg | 512x512 |


---

## 4. Fruits-360 100x100

- **Dataset Base Path:** `data/raw/fruits-360-100x100-main`
- **Training Path:** `data/raw/fruits-360-100x100-main/Training`
- **Test Path:** `data/raw/fruits-360-100x100-main/Test`
- **Training Images:** 138,642
- **Test Images:** 46,196
- **Total Images:** 184,838
- **Classes Count:**
  - Training Classes: 262
  - Test Classes: 262
  - Shared Classes (exact match): 261
  - Train-Only Classes: `['BlackBerry 4']` (`BlackBerry 4`)
  - Test-Only Classes: `['Blackberry 4']` (`Blackberry 4`)
  *(Note: A capitalization discrepancy in upstream naming accounts for the single non-matching class name; case-insensitively, exactly 262 classes exist across both sets).*
- **Class Balance Statistics:**
  - Largest Class: `Grape Blue 1` with 1,312 images
  - Smallest Class: `Blackberry 4` with 145 images
  - Mean Images per Class: 702.81
  - Median Images per Class: 656.00
  - 25th Percentile (Q1): 602.0 images | 75th Percentile (Q3): 928.0 images | IQR: 326.0
  - Extreme Outliers: 0 low outliers, 0 high outliers (well-balanced distribution).
- **Image Dimensions & Channels:**
  - Uniformly `100x100` pixels across all sampled classes.
  - Color Mode: `RGB`.
  - Extension: `.jpg` (100% of image files).
- **Non-image Files in Dataset:**
  - `LICENSE, README.md` in root folder; 0 non-image files inside Training and Test splits.
- **Corrupted Images:** 0 corrupted or zero-byte files found.
- **Duplicate Scan Status:** Full duplicate hash scan not performed in STEP 2 due to dataset size (184,838 images).
- **Food Grouping Analysis:**
  - The 262 sub-classes map into approximately 85 distinct high-level food groups (e.g., Apple: 30 classes, Tomato: 14 classes, Banana: 5 classes, Grape: 8 classes).

### Sample Fruits-360 Class Distribution (First 25 Classes)

| Class Name | Training Count | Test Count | Total Count | Present in Both? | Potential Food Group |
| --- | --- | --- | --- | --- | --- |
| `Almonds 1` | 232 | 77 | 309 | Yes | Almonds |
| `Apple 10` | 699 | 231 | 930 | Yes | Apple |
| `Apple 11` | 430 | 142 | 572 | Yes | Apple |
| `Apple 12` | 466 | 154 | 620 | Yes | Apple |
| `Apple 13` | 699 | 235 | 934 | Yes | Apple |
| `Apple 14` | 466 | 154 | 620 | Yes | Apple |
| `Apple 17` | 610 | 201 | 811 | Yes | Apple |
| `Apple 18` | 724 | 240 | 964 | Yes | Apple |
| `Apple 19` | 729 | 241 | 970 | Yes | Apple |
| `Apple 20` | 702 | 234 | 936 | Yes | Apple |
| `Apple 21` | 488 | 162 | 650 | Yes | Apple |
| `Apple 22` | 696 | 231 | 927 | Yes | Apple |
| `Apple 23` | 470 | 156 | 626 | Yes | Apple |
| `Apple 5` | 440 | 146 | 586 | Yes | Apple |
| `Apple 6` | 473 | 157 | 630 | Yes | Apple |
| `Apple 7` | 694 | 229 | 923 | Yes | Apple |
| `Apple 8` | 687 | 228 | 915 | Yes | Apple |
| `Apple 9` | 694 | 231 | 925 | Yes | Apple |
| `Apple Braeburn 1` | 492 | 164 | 656 | Yes | Apple |
| `Apple Crimson Snow 1` | 444 | 148 | 592 | Yes | Apple |
| `Apple Golden 1` | 480 | 160 | 640 | Yes | Apple |
| `Apple Golden 2` | 492 | 164 | 656 | Yes | Apple |
| `Apple Golden 3` | 481 | 161 | 642 | Yes | Apple |
| `Apple Granny Smith 1` | 492 | 164 | 656 | Yes | Apple |
| `Apple Pink Lady 1` | 456 | 152 | 608 | Yes | Apple |

*(Full list of all 262 classes available in `reports/fruits360_class_distribution.csv`)*

---

## 5. FoodKeeper Database

- **File Path:** `data/raw/foodkeeper/FoodKeeper.json`
- **JSON Validity:** Valid and well-formed.
- **File Size:** 631,800 bytes
- **Top-Level Keys:** `['fileName', 'sheets']`
- **Available Sheets:**
  - `Version`: 21 rows
  - `Category`: 25 rows
  - `Product`: 661 rows
  - `CookingTips`: 93 rows
  - `CookingMethods`: 89 rows
  - `Data Dictionary`: 62 rows
- **Product Record Count:** 661 items
- **Schema & Field Categories:**
  - **Core Identifiers:** `ID`, `Category_ID`, `Name`, `Name_subtitle`, `Keywords`
  - **Pantry Storage:** `Pantry_Min`, `Pantry_Max`, `Pantry_Metric`, `Pantry_tips`, `DOP_Pantry_Min`, `DOP_Pantry_Max`, `DOP_Pantry_Metric`, `DOP_Pantry_tips`, `Pantry_After_Opening_Min`, `Pantry_After_Opening_Max`, `Pantry_After_Opening_Metric`
  - **Refrigerate Storage:** `Refrigerate_Min`, `Refrigerate_Max`, `Refrigerate_Metric`, `Refrigerate_tips`, `DOP_Refrigerate_Min`, `DOP_Refrigerate_Max`, `DOP_Refrigerate_Metric`, `DOP_Refrigerate_tips`, `Refrigerate_After_Opening_Min`, `Refrigerate_After_Opening_Max`, `Refrigerate_After_Opening_Metric`, `Refrigerate_After_Thawing_Min`, `Refrigerate_After_Thawing_Max`, `Refrigerate_After_Thawing_Metric`
  - **Freezer Storage:** `Freeze_Min`, `Freeze_Max`, `Freeze_Metric`, `Freeze_Tips`, `DOP_Freeze_Min`, `DOP_Freeze_Max`, `DOP_Freeze_Metric`, `DOP_Freeze_Tips`
- **Key Categories for Produce:**
  - `Category ID 18.0`: Produce -> Subcategory: Fresh Fruits
  - `Category ID 19.0`: Produce -> Subcategory: Fresh Vegetables

### FoodKeeper Sample Produce Records

| ID | Product Name | Category ID | Pantry Duration | Refrigerate Duration | Freeze Duration |
| --- | --- | --- | --- | --- | --- |
| 248 | Apples | 18 | Not specified | Not specified | 8.0-8.0 Months |
| 251 | Bananas | 18 | Not specified | 3.0-3.0 Days | 2.0-3.0 Months |
| 283 | Cucumbers | 19 | Not specified | Not specified | Not specified |
| 284 | Eggplant | 19 | Not specified | Not specified | Not specified |
| 306 | Tomatoes | 19 | Not specified | Not specified | Not specified |


---

## 6. Cross-Dataset Observations

- **AgriFreshNET Food Types (8 total):**
  `Banana`, `Bittermelon`, `Cucumber`, `Eggplant`, `Orange`, `Papaya`, `Pineapple`, `Tomato`.
- **Food Types present in both AgriFreshNET and Fruits-360 (7 foods):**
  1. `Banana` (AgriFreshNET: 3 classes; Fruits-360: 5 sub-varieties)
  2. `Cucumber` (AgriFreshNET: 3 classes; Fruits-360: 4 sub-varieties)
  3. `Eggplant` (AgriFreshNET: 3 classes; Fruits-360: 2 sub-varieties)
  4. `Orange` (AgriFreshNET: 3 classes; Fruits-360: `orange 4` / citrus)
  5. `Papaya` (AgriFreshNET: 3 classes; Fruits-360: 2 sub-varieties)
  6. `Pineapple` (AgriFreshNET: 3 classes; Fruits-360: 6 sub-varieties)
  7. `Tomato` (AgriFreshNET: 3 classes; Fruits-360: 14 sub-varieties)
- **AgriFreshNET Foods NOT in Fruits-360 (1 food):**
  - `Bittermelon` (Bitter gourd): present only in AgriFreshNET.
- **Produce Presence in FoodKeeper:**
  All major overlapping food items (`Bananas`, `Cucumbers`, `Eggplant`, `Pineapple`, `Tomatoes`, `Papaya`, `Citrus`) have reference storage entries in FoodKeeper under Categories 18 (`Fresh Fruits`) and 19 (`Fresh Vegetables`).

---

## 7. Data Quality Findings

1. **Intact & Valid Assets:** All three datasets are fully extracted and healthy. Zero zero-byte files or unreadable image files were encountered.
2. **AgriFreshNET Folder Casing & Syntax Inconsistencies:**
   - Folder naming conventions differ slightly (e.g., `Fresh eggplant(1-4)` vs `Fresh Orange(1-9)`, `Semi fresh banana(4-7)` vs `Semi Fresh Bittermelon ( 3-5)` vs `Semi_Fresh eggplant(4-8)`).
   - Our regex safely handled all whitespace, casing, and delimiter variations, correctly identifying all 24 classes into 8 foods, 3 stages, and exact min/max shelf-life ranges.
3. **AgriFreshNET Identical Frames:** Exactly 40 images are bit-for-bit duplicate files within their respective class folders (e.g. repeated burst frames).
4. **Fruits-360 Class Casing Discrepancy:**
   - Training has folder `BlackBerry 4` (capital 'B'); Test has folder `Blackberry 4` (lowercase 'b').
   - In cross-split mapping, case-normalization resolves this discrepancy completely.
5. **Dimensions Consistency:**
   - Fruits-360 images are strictly `100x100` RGB.
   - AgriFreshNET images are strictly `512x512` RGB.

---

## 8. Recommended Next ML Preparation (For STEP 3)

1. **Dataset Normalization & Indexing:**
   - Create a clean metadata registry mapping original folder paths to canonical food names (`banana`, `cucumber`, `eggplant`, `orange`, `papaya`, `pineapple`, `tomato`, `bittermelon`), canonical freshness stages (`fresh`, `semi_fresh`, `rotten`), and continuous shelf-life bounds (`min_days`, `max_days`).
2. **Fruits-360 Food-Level Aggregation:**
   - For general food recognition, establish a mapping from the 262 granular variety classes into high-level food groups (e.g., merging all Apple varieties into `apple`).
3. **Train/Val/Test Splitting Strategy for AgriFreshNET:**
   - Because AgriFreshNET contains burst-capture images and duplicate frames within classes, train/val/test splits should be created with stratified or group-aware sampling to prevent data leakage between splits.
4. **Resolution Strategy for EfficientNet-B0:**
   - Standard EfficientNet-B0 input resolution is `224x224`. AgriFreshNET images (`512x512`) will be downscaled to `224x224`, and Fruits-360 images (`100x100`) can be resized/padded to `224x224` during data pipeline transformation without modifying the original raw archives.
5. **FoodKeeper Lookup Integration:**
   - Create an index/service for matching recognized food names to FoodKeeper products to enrich shelf-life predictions with USDA storage guidelines.
