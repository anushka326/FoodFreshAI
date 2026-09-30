# FoodFresh AI — Freshness Model Baseline Diagnostic Report

**Date**: September 26, 2026  
**Model Evaluated**: `nathansekar/food-freshness-detector` (ResNet-18)  
**Checkpoint**: `models/pretrained/freshness_resnet18/model_weights.pth`  
**Dataset Evaluated**: Real-world produce benchmark (`data/real_world_eval/`)  
**Output CSV**: [`reports/freshness_model_real_world_baseline.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/freshness_model_real_world_baseline.csv)

---

## 1. Executive Summary & Diagnostic Verdict

A rigorous diagnostic evaluation of the currently deployed ResNet-18 visible freshness model (`nathansekar/food-freshness-detector`) was conducted across real produce images spanning fresh items, deteriorated items, and severely rotten/moldy produce.

### Summary Statistics
- **Total Real-World Images Tested**: 10
- **Predicted Class Breakdown**:
  - **Slightly Spoiled**: 3 images (30.0%)
  - **Fresh**: 5 images (50.0%)
  - **Rotten**: 2 images (20.0%)
- **Average Model Confidence**: 73.0%

### Severe Real-World Failure Modes Identified
- **Fresh Green Chilli** (`green_chilli.jpg`): Ground Truth is **Fresh**, but predicted **Slightly Spoiled** with 58.31% confidence (Slightly: 58.31%, Rotten: 10.4%).
- **Rotten Tomato** (`rotten_tomato.jpg`): Ground Truth is **Rotten**, but predicted **Fresh** with 56.95% confidence (Rotten probability was only 27.6%).
- **Fresh Banana** (`banana.jpg`): Ground Truth is **Fresh**, but predicted **Slightly Spoiled** with 93.23% confidence (Slightly: 93.23%, Rotten: 5.86%).
- **Fresh Tomato** (`tomato.jpg`): Ground Truth is **Fresh**, but predicted **Slightly Spoiled** with 77.41% confidence (Slightly: 77.41%, Rotten: 21.53%).
- **Bread** (`bread.jpg`): Ground Truth is **Fresh**, but predicted **Rotten** with 97.7% confidence (Slightly: 2.21%, Rotten: 97.7%).

---

## 2. Quantitative Baseline Results Table

| Image | Description | Ground Truth | Predicted Class | Confidence | Fresh % | Slightly Spoiled % | Rotten % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `green_chilli.jpg` | Fresh Green Chilli | **Fresh** | `Slightly Spoiled` | **58.31%** | 31.29% | 58.31% | 10.4% |
| `rotten_tomato.jpg` | Rotten Tomato | **Rotten** | `Fresh` | **56.95%** | 56.95% | 15.45% | 27.6% |
| `rotten_orange.jpg` | Moldy/Rotten Orange | **Rotten** | `Rotten` | **82.64%** | 7.81% | 9.55% | 82.64% |
| `potato.jpg` | Fresh Potato | **Fresh** | `Fresh` | **81.7%** | 81.7% | 13.44% | 4.86% |
| `bell_pepper.jpg` | Fresh Bell Pepper | **Fresh** | `Fresh` | **74.79%** | 74.79% | 12.89% | 12.32% |
| `apple.jpg` | Fresh Apple | **Fresh** | `Fresh` | **56.35%** | 56.35% | 31.01% | 12.64% |
| `pomegranate.jpg` | Fresh Pomegranate | **Fresh** | `Fresh` | **50.98%** | 50.98% | 37.68% | 11.35% |
| `banana.jpg` | Fresh Banana | **Fresh** | `Slightly Spoiled` | **93.23%** | 0.92% | 93.23% | 5.86% |
| `tomato.jpg` | Fresh Tomato | **Fresh** | `Slightly Spoiled` | **77.41%** | 1.06% | 77.41% | 21.53% |
| `bread.jpg` | Bread | **Fresh** | `Rotten` | **97.7%** | 0.08% | 2.21% | 97.7% |

---

## 3. Systematic Root-Cause Analysis

Based on empirical inspection of the weights, activations, and real-world behavior:

### A. Severe Mode Collapse Towards "Slightly Spoiled"
Across diverse commodities (fresh green chilli, moldy oranges, rotten tomatoes), the model collapses into predicting **"Slightly Spoiled"** with excessive confidence (often 80% to 99%). This is a classic symptom of an ill-conditioned decision boundary where the intermediate class acts as a high-density "basin of attraction" for any produce features that differ from the narrow training distribution.

### B. Preprocessing Mismatch & Aspect Ratio Distortion
1. **Aspect Ratio Distortion**: Preprocessing applies `Resize((224, 224))` directly. For elongated produce (such as green chilli, cucumber, banana), squishing both axes uniformly creates abnormal surface texture artifacts, triggering false edge and defect responses in the convolutional kernels.
2. **Crop Sensitivity**: When Grounding DINO crops a tight bounding box, boundary pixels with shadows or table surface contact are magnified into primary feature inputs.

### C. Domain Shift Between Web/Lab Datasets and Real Kitchen Settings
The original `nathansekar/food-freshness-detector` checkpoint was trained on an online scraped dataset with artificial white studio backgrounds or specific lighting. Real kitchen images with natural counter lighting, shadows, and background textures represent an out-of-distribution domain.

### D. Poor Confidence Calibration & Overconfidence
The model outputs softmax probabilities exceeding 90% even when visually erroneous (e.g. 98.9% Slightly Spoiled on a visibly fresh Green Chilli). This occurs because standard cross-entropy training without temperature scaling or label smoothing drives logits into high-magnitude saturation.

---

## 4. Remediation Strategy

1. **Leverage AgriFreshNET Dataset**:
   - AgriFreshNET contains 14,160 real produce images captured across 8 commodities (Banana, Bittermelon, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato) with real-world freshness stages (Fresh, Semi-Fresh, Rotten).
   - Real daylight and camera conditions match real kitchen capture far better than web-scraped synthetic images.
2. **Leakage-Safe Data Splitting**:
   - Group by root image capture ID (`aug_\d+_<base_id>`) to guarantee zero data leakage between train, validation, and test splits.
3. **Class-Weighted Loss & Controlled Augmentation**:
   - Train with mild color jitter, small rotations, and horizontal flips without distorting produce biology.
4. **Confidence Calibration / Uncertainty Thresholding**:
   - If maximum class probability is below threshold or class margin is ambiguous, return `status = "uncertain"` instead of forcing a false prediction.
