# FoodFresh AI — Food Recognition V3 Dataset Preparation Report

## 1. Objective
Prepare a unified, leak-free, domain-aware dataset for Food Recognition V3 that introduces real-world visual diversity (domestic backgrounds, realistic ambient lighting, and natural produce degradation) from AgriFreshNET while preserving the full 24-class Fruits-360 benchmark.

## 2. Vocabulary & Class Taxonomy
- **Vocabulary Size:** 24 classes (Identical to V2 baseline)
- **Classes:** Apple, Avocado, Banana, Cherry, Corn, Cucumber, Eggplant, Grape, Guava, Lemon, Mango, Onion, Orange, Papaya, Peach, Pear, Pepper, Pineapple, Plum, Pomegranate, Potato, Strawberry, Tomato, Watermelon
- **Class Ordering:** Deterministically preserved from `data/processed/fruits360_v2/label_map.json`.

## 3. Cross-Dataset Mappings & Scope
- **Authoritative Mapping File:** `data/processed/cross_dataset/food_class_mapping_v3.json`
- **Approved AgriFreshNET Foods (7 classes):** Banana, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato.
- **Excluded AgriFreshNET Foods (1 class):** Bittermelon (1,770 images excluded; not in V2/V3 food taxonomy).
- **Freshness Decoupling:** Ingestion strictly maps `source_class` into canonical `food_class` (e.g. `Rotten banana(7-13)` $\rightarrow$ `Banana`). Freshness labels (`Fresh`, `Semi-Fresh`, `Rotten`) are preserved as auxiliary metadata and are strictly prohibited from becoming food identity classification targets.

## 4. Dataset Composition & Split Summary

| Split | Fruits-360 (Controlled) | AgriFreshNET (Real-World) | Real-World Manual | Total Split Images |
| :--- | :---: | :---: | :---: | :---: |
| **Training (`v3_train_manifest.csv`)** | 76,961 | 8,624 | 0 | **85,585** |
| **Validation (`v3_val_manifest.csv`)** | 19,233 | 1,862 | 0 | **21,095** |
| **Benchmark Test (`v3_benchmark_test_manifest.csv`)** | 32,016 | 0 | 0 | **32,016** |
| **Real-World Test (`v3_real_world_test_manifest.csv`)** | 0 | 1,904 | 0 | **1,904** |
| **Grand Total** | **128,210** | **12,390** | **0** | **140,600** |

## 5. Benchmark Test Set Protection
- The 32,016 Fruits-360 test images remain 100% untouched and isolated in `v3_benchmark_test_manifest.csv`.
- Real-world images are strictly segregated into `v3_real_world_test_manifest.csv`.
- Neither test split contains any overlap with training or validation splits.

## 6. Leakage Prevention Protocol
- **AgriFreshNET Burst Frame Containment:** Images were partitioned strictly based on the physical photo base stem (stripping augmentation prefixes `aug_\d+_`). All augmentations of a single physical photo reside exclusively in one partition.
- **Fruits-360 Containment:** Preserves the official training and test directory split from Fruits-360.

## 7. Real-World Coverage & Priority Roadmap
- **7 Multi-Domain Classes:** Banana, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato have strong real-world representation (1,770 total images each across train/val/test).
- **17 Single-Domain Classes:** Apple, Avocado, Cherry, Corn, Grape, Guava, Lemon, Mango, Onion, Peach, Pear, Pepper, Plum, Pomegranate, Potato, Strawberry, Watermelon currently rely on Fruits-360 studio images.
- **Immediate Manual Collection Priorities:**
  1. **Pomegranate & Apple:** Critical known domain-shift failure cases (target: 30–75 diverse consumer photos).
  2. **Onion, Mango, Potato:** Common kitchen staples currently lacking non-white backgrounds (target: 25–60 photos).

## 8. Artifacts Generated
- Manifest: `data\processed\food_recognition_v3\manifests\v3_train_manifest.csv`
- Manifest: `data\processed\food_recognition_v3\manifests\v3_val_manifest.csv`
- Manifest: `data\processed\food_recognition_v3\manifests\v3_benchmark_test_manifest.csv`
- Manifest: `data\processed\food_recognition_v3\manifests\v3_real_world_test_manifest.csv`
- Configuration: `data\processed\food_recognition_v3\dataset_config.json`
- Label Map: `data\processed\food_recognition_v3\label_map.json`
- Balance Report: `reports\food_recognition_v3_class_balance.csv`

## 9. Verification & Invariance Confirmation
- **Model Training Executed:** NO (0 epochs trained, no gradients computed).
- **Production Model Checkpoint:** `models/trained/food_classifier_v2.pth` (100% UNCHANGED).
- **Production Inference Service:** Unmodified (Serving V2).
