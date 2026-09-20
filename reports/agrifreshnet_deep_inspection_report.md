# FoodFresh AI — AgriFreshNET Deep Inspection Report

## 1. Dataset Location
- **Base Archive Root:** `data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase`
- **Class Data Root:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\AgriFreshNET Freshness and Shelf-Life Image Datase\Processed Data\Processed Data`
- **Filesystem Integrity:** Verified and accessible. No archive extraction currently in progress.

---

## 2. Dataset Inspection Date
- **Date & Time:** 2026-09-18 00:34:55
- **Inspection Type:** Complete Programmatic Deep Scan (**FULL** — all 14,160 images inspected individually)
- **Execution Script:** `scripts/inspect_agrifreshnet.py`

---

## 3. Overall Statistics
- **Total Image Count:** **14,160** images
- **Total Class Count:** **24** class folders
- **Food Categories Count:** **8** distinct produce items
- **Freshness Stages Count:** **3** standardized quality stages (`Fresh`, `Semi-Fresh`, `Rotten`)
- **Image Format Distribution:**
  - `.jpg`: 13,890 images (98.09%)
  - `.jpeg`: 270 images (1.91%)
- **Image Dimensions & Modes:**
  - Width $\times$ Height: Uniformly **512 $\times$ 512** pixels across 100% of all 14,160 images.
  - Color Channel Mode: Uniformly **RGB** (3-channel color).

---

## 4. Class-Level Analysis
Every class folder contains exactly 590 images, representing a completely balanced design.

| Class | Food | Freshness Stage | Shelf-Life Range | Image Count |
| --- | --- | --- | --- | --- |
| `Fresh Banana(1-4)` | Banana | Fresh | 1–4 days | 590 |
| `Fresh Bittermelon(1-3)` | Bittermelon | Fresh | 1–3 days | 590 |
| `Fresh Cucumber(1-6)` | Cucumber | Fresh | 1–6 days | 590 |
| `Fresh eggplant(1-4)` | Eggplant | Fresh | 1–4 days | 590 |
| `Fresh Orange(1-9)` | Orange | Fresh | 1–9 days | 590 |
| `Fresh Papaya(1-4)` | Papaya | Fresh | 1–4 days | 590 |
| `Fresh pineapple(1-15)` | Pineapple | Fresh | 1–15 days | 590 |
| `Fresh Tomato(1-10)` | Tomato | Fresh | 1–10 days | 590 |
| `Rotten banana(7-13)` | Banana | Rotten | 7–13 days | 590 |
| `Rotten Bittermelon(5-8)` | Bittermelon | Rotten | 5–8 days | 590 |
| `Rotten Cucumber(12-20)` | Cucumber | Rotten | 12–20 days | 590 |
| `Rotten eggplant(8-15)` | Eggplant | Rotten | 8–15 days | 590 |
| `Rotten Orange(20-35)` | Orange | Rotten | 20–35 days | 590 |
| `Rotten Papaya(7-12)` | Papaya | Rotten | 7–12 days | 590 |
| `Rotten Pineapple(25-35)` | Pineapple | Rotten | 25–35 days | 590 |
| `Rotten Tomato(24-35)` | Tomato | Rotten | 24–35 days | 590 |
| `Semi fresh banana(4-7)` | Banana | Semi-Fresh | 4–7 days | 590 |
| `Semi Fresh Bittermelon ( 3-5)` | Bittermelon | Semi-Fresh | 3–5 days | 590 |
| `Semi Fresh Cucumber(6-12)` | Cucumber | Semi-Fresh | 6–12 days | 590 |
| `Semi fresh Orange(9-20)` | Orange | Semi-Fresh | 9–20 days | 590 |
| `Semi Fresh Papaya(4-7)` | Papaya | Semi-Fresh | 4–7 days | 590 |
| `Semi fresh Pineapple (15-25)` | Pineapple | Semi-Fresh | 15–25 days | 590 |
| `Semi fresh Tomato(10-24)` | Tomato | Semi-Fresh | 10–24 days | 590 |
| `Semi_Fresh eggplant(4-8)` | Eggplant | Semi-Fresh | 4–8 days | 590 |


---

## 5. Freshness Distribution
The dataset is perfectly balanced across all three freshness stages (33.33% each):

| Freshness Stage | Image Count | Class Count | Percentage of Images |
| --- | --- | --- | --- |
| **Fresh** | 4,720 | 8 | 33.33% |
| **Semi-Fresh** | 4,720 | 8 | 33.33% |
| **Rotten** | 4,720 | 8 | 33.33% |
| **UNKNOWN** | 0 | 0 | 0.00% |

---

## 6. Food Distribution
The dataset is uniformly distributed across all 8 food categories, with each food containing 1,770 images (12.5%):

| Food | Class Count | Image Count | Percentage of Images |
| --- | --- | --- | --- |
| **Banana** | 3 | 1,770 | 12.50% |
| **Bittermelon** | 3 | 1,770 | 12.50% |
| **Cucumber** | 3 | 1,770 | 12.50% |
| **Eggplant** | 3 | 1,770 | 12.50% |
| **Orange** | 3 | 1,770 | 12.50% |
| **Papaya** | 3 | 1,770 | 12.50% |
| **Pineapple** | 3 | 1,770 | 12.50% |
| **Tomato** | 3 | 1,770 | 12.50% |

---

## 7. Food × Freshness Coverage
Every single food category has 100% full coverage across all three freshness stages:

| Food Type | Fresh | Semi-Fresh | Rotten | Total Images |
| --- | --- | --- | --- | --- |
| **Banana** | 590 | 590 | 590 | 1,770 |
| **Bittermelon** | 590 | 590 | 590 | 1,770 |
| **Cucumber** | 590 | 590 | 590 | 1,770 |
| **Eggplant** | 590 | 590 | 590 | 1,770 |
| **Orange** | 590 | 590 | 590 | 1,770 |
| **Papaya** | 590 | 590 | 590 | 1,770 |
| **Pineapple** | 590 | 590 | 590 | 1,770 |
| **Tomato** | 590 | 590 | 590 | 1,770 |


---

## 8. Shelf-Life Annotation Analysis
Every class folder encodes a post-harvest day range in parentheses, e.g., `(1-4)`, `(4-7)`, `(7-13)`.

> [!IMPORTANT]
> The shelf-life ranges are treated as approximate dataset annotations and are not interpreted as guaranteed remaining food safety periods.
> These values reflect laboratory post-harvest monitoring intervals observed during dataset curation under specific storage conditions.

- **Range Parsing Success Rate:** **24 / 24 classes (100%)** successfully parsed.
- **Minimum Observed Annotated Bound:** **1 day** (Day 1 of harvest for all Fresh classes).
- **Maximum Observed Annotated Bound:** **35 days** (Day 35 for Rotten Tomato, Rotten Orange, and Rotten Pineapple).
- **Midpoint Values:** Midpoints provide continuous targets for regression modeling (ranging from 2.0 days for Fresh Bittermelon to 30.0 days for Rotten Pineapple and Rotten Tomato).

---

## 9. Image Quality
- **Corrupted / Unreadable Images:** **0** (All 14,160 image files opened, header verified, and dimensions confirmed without error).
- **Zero-Byte Files:** **0**
- **Non-Image Files:** **0** inside the class folders.
- **Unexpected Subdirectories:** **0** nested folders inside class folders.
- **Exact Hash Duplicates:**
  - **36 duplicate hash clusters** representing **40 redundant file instances** (14,120 unique image hashes).
  - *Intra-class duplicates:* Duplicate frame exports within identical classes (e.g., repeated burst captures in `Fresh Banana(1-4)`).
  - *Inter-class duplicates:* Exactly 17 image files are shared identically between `Fresh Orange(1-9)` and `Semi fresh Orange(9-20)` (representing day-9 boundary overlap).

---

## 10. Image Dimensions
A **FULL** inspection of all 14,160 images was performed:
- **Common Dimensions:** 512 $\times$ 512 pixels
- **Minimum Dimensions:** 512 $\times$ 512 pixels
- **Maximum Dimensions:** 512 $\times$ 512 pixels
- **Aspect Ratio:** 1:1 square across all classes.
- **Color Mode:** RGB (24-bit color).
- **No resizing or alteration of original images was performed.**

---

## 11. Class Imbalance
- **Total Classes:** 24
- **Smallest Class:** 590 images
- **Largest Class:** 590 images
- **Mean Images per Class:** 590.00
- **Median Images per Class:** 590.00
- **Standard Deviation:** 0.00
- **Imbalance Ratio:** **1.0000** (Perfect balance across all 24 classes).
- **Classes substantially fewer than median:** 0

---

## 12. Label Naming Variations
The folder naming convention contains several syntax variations that require normalized parsing:

| Original Folder Name | Normalized Stage | Normalized Food | Parsed Range | Notes / Formatting Quirks |
| --- | --- | --- | --- | --- |
| `Fresh Banana(1-4)` | Fresh | Banana | 1-4 days | Standard formatting |
| `Fresh Bittermelon(1-3)` | Fresh | Bittermelon | 1-3 days | Standard formatting |
| `Fresh Cucumber(1-6)` | Fresh | Cucumber | 1-6 days | Standard formatting |
| `Fresh eggplant(1-4)` | Fresh | Eggplant | 1-4 days | Lowercase food initial: `eggplant` |
| `Fresh Orange(1-9)` | Fresh | Orange | 1-9 days | Standard formatting |
| `Fresh Papaya(1-4)` | Fresh | Papaya | 1-4 days | Standard formatting |
| `Fresh pineapple(1-15)` | Fresh | Pineapple | 1-15 days | Lowercase food initial: `pineapple` |
| `Fresh Tomato(1-10)` | Fresh | Tomato | 1-10 days | Standard formatting |
| `Rotten banana(7-13)` | Rotten | Banana | 7-13 days | Lowercase food initial: `banana` |
| `Rotten Bittermelon(5-8)` | Rotten | Bittermelon | 5-8 days | Standard formatting |
| `Rotten Cucumber(12-20)` | Rotten | Cucumber | 12-20 days | Standard formatting |
| `Rotten eggplant(8-15)` | Rotten | Eggplant | 8-15 days | Lowercase food initial: `eggplant` |
| `Rotten Orange(20-35)` | Rotten | Orange | 20-35 days | Standard formatting |
| `Rotten Papaya(7-12)` | Rotten | Papaya | 7-12 days | Standard formatting |
| `Rotten Pineapple(25-35)` | Rotten | Pineapple | 25-35 days | Standard formatting |
| `Rotten Tomato(24-35)` | Rotten | Tomato | 24-35 days | Standard formatting |
| `Semi fresh banana(4-7)` | Semi-Fresh | Banana | 4-7 days | Stage casing: `Semi fresh`, Lowercase food initial: `banana` |
| `Semi Fresh Bittermelon ( 3-5)` | Semi-Fresh | Bittermelon | 3-5 days | Irregular spacing (`( 3-5)`, ` (15-25)`) |
| `Semi Fresh Cucumber(6-12)` | Semi-Fresh | Cucumber | 6-12 days | Standard formatting |
| `Semi fresh Orange(9-20)` | Semi-Fresh | Orange | 9-20 days | Stage casing: `Semi fresh` |
| `Semi Fresh Papaya(4-7)` | Semi-Fresh | Papaya | 4-7 days | Standard formatting |
| `Semi fresh Pineapple (15-25)` | Semi-Fresh | Pineapple | 15-25 days | Irregular spacing (`( 3-5)`, ` (15-25)`), Stage casing: `Semi fresh` |
| `Semi fresh Tomato(10-24)` | Semi-Fresh | Tomato | 10-24 days | Stage casing: `Semi fresh` |
| `Semi_Fresh eggplant(4-8)` | Semi-Fresh | Eggplant | 4-8 days | Underscore delimiter (`Semi_Fresh`), Lowercase food initial: `eggplant` |


All variations were successfully mapped to standard canonical tokens:
- Freshness: `Fresh`, `Semi-Fresh`, `Rotten`
- Food: `Banana`, `Bittermelon`, `Cucumber`, `Eggplant`, `Orange`, `Papaya`, `Pineapple`, `Tomato`

---

## 13. Shelf-Life Range Consistency
The shelf-life annotations show continuous contiguous boundaries across all 8 food categories:

| Food | Fresh Range | Semi-Fresh Range | Rotten Range | Continuity / Overlap Observation |
| --- | --- | --- | --- | --- |
| **Banana** | 1-4 days | 4-7 days | 7-13 days | Fresh max (4) equals Semi-Fresh min (4); Semi-Fresh max (7) equals Rotten min (7). |
| **Bittermelon** | 1-3 days | 3-5 days | 5-8 days | Fresh max (3) equals Semi-Fresh min (3); Semi-Fresh max (5) equals Rotten min (5). |
| **Cucumber** | 1-6 days | 6-12 days | 12-20 days | Fresh max (6) equals Semi-Fresh min (6); Semi-Fresh max (12) equals Rotten min (12). |
| **Eggplant** | 1-4 days | 4-8 days | 8-15 days | Fresh max (4) equals Semi-Fresh min (4); Semi-Fresh max (8) equals Rotten min (8). |
| **Orange** | 1-9 days | 9-20 days | 20-35 days | Fresh max (9) equals Semi-Fresh min (9); Semi-Fresh max (20) equals Rotten min (20). |
| **Papaya** | 1-4 days | 4-7 days | 7-12 days | Fresh max (4) equals Semi-Fresh min (4); Semi-Fresh max (7) equals Rotten min (7). |
| **Pineapple** | 1-15 days | 15-25 days | 25-35 days | Fresh max (15) equals Semi-Fresh min (15); Semi-Fresh max (25) equals Rotten min (25). |
| **Tomato** | 1-10 days | 10-24 days | 24-35 days | Fresh max (10) equals Semi-Fresh min (10); Semi-Fresh max (24) equals Rotten min (24). |


Every food exhibits contiguous boundary intervals where the upper day of one stage matches the starting day of the subsequent stage.

---

## 14. Dataset Limitations
1. **Limited Food Diversity:** Only 8 distinct produce varieties are represented in AgriFreshNET. For general food recognition, AgriFreshNET must be supplemented by Fruits-360 (which contains 262 classes across ~85 food types).
2. **Boundary Redundancy:** 17 duplicate images exist between Fresh and Semi-Fresh Orange at the day-9 boundary transition.
3. **Burst Captures:** Multiple images per class share near-identical camera angles and lighting (burst frames), meaning train/val/test splits must be constructed carefully to prevent data leakage.
4. **Controlled Environment:** Images are captured on uniform backgrounds under consistent lighting, which may require augmentation during future training to generalize to real-world kitchen and refrigerator conditions.

---

## 15. Suitability for FoodFresh AI
### A. Freshness Classification
AgriFreshNET is exceptionally well-suited for training our multi-class freshness classifier:
- Exact 3-stage taxonomy (`Fresh`, `Semi-Fresh`, `Rotten`).
- Perfectly balanced (4,720 images per stage).
- High visual resolution (512 $\times$ 512), easily downsampled to standard EfficientNet-B0 resolution (224 $\times$ 224).

### B. Shelf-Life Regression / Ranking
AgriFreshNET is well-suited for shelf-life estimation:
- Each class provides bounded intervals `(shelf_life_min, shelf_life_max)` and calculated midpoints `shelf_life_midpoint`.
- Can support dual-head architectures (classification for freshness stage + regression/interval estimation for shelf-life).

---

## 16. Recommendations for STEP 4
Based strictly on these inspection findings, the recommended next technical steps are:
1. **Canonical Metadata Indexing:** Use `reports/agrifreshnet_image_metadata.csv` and `reports/agrifreshnet_class_metadata.csv` as the foundation for the dataset loader.
2. **Leak-Free Partitioning:** Build a group-aware or stratified train/val/test split generator that avoids placing identical burst frames or boundary duplicates in both training and test splits.
3. **EfficientNet-B0 Input Pipeline Design:** Create a PyTorch `Dataset` and `DataLoader` pipeline that applies standard 224 $\times$ 224 transforms dynamically without modifying raw source files.
4. **Food Recognition Integration Plan:** Plan a unified inference pipeline where Fruits-360 models recognize the food category, and AgriFreshNET models determine freshness and remaining shelf life.
