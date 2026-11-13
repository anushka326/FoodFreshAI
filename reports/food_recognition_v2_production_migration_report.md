# FoodFresh AI — Food Recognition V2 Production Migration Report

**Date:** September 22, 2026  
**Status:** Successfully Migrated & Verified in Production  

---

## 1. Executive Summary
The FoodFresh AI Food Recognition production inference pipeline has been successfully migrated from **V1 (12 classes)** to **V2 (24 classes)**. This migration permanently resolves the root cause behind the previous Pomegranate misclassification diagnostic (Step 11).

In V1, Pomegranate was completely absent from the model vocabulary, forcing the softmax layer to map red spherical produce to Apple. Under V2, Pomegranate is an authoritative first-class category, recognized with **100.0% accuracy** on the official Fruits-360 test benchmark and **100.0% confidence** on live production inference.

---

## 2. Model Architecture & Configuration Comparison

| Attribute | Previous Production (V1) | Migrated Production (V2) |
| :--- | :--- | :--- |
| **Model Version** | `v1` | `v2` (Default) |
| **Architecture** | EfficientNet-B0 (`Linear(1280, 12)`) | EfficientNet-B0 (`Linear(1280, 24)`) |
| **Output Classes** | 12 classes | **24 classes** |
| **Pomegranate Support**| ❌ Completely Missing | **✅ Fully Supported (Class 19)** |
| **Checkpoint Path** | `models/trained/food_classifier.pth` | `models/trained/food_classifier_v2.pth` |
| **Checkpoint Size** | 16.3 MB | 48.9 MB |
| **Label Map Path** | `data/processed/fruits360/label_map.json` | `data/processed/fruits360_v2/label_map.json` |
| **Top-1 Test Accuracy** | 99.78% (12 classes) | **99.52%** (24 classes across 32,016 images) |
| **Pomegranate Test Acc**| 0% (Absent) | **100.0%** (164/164 test images correct) |
| **Input Preprocessing** | Resize(224) + ImageNet Norm | Resize(224) + ImageNet Norm (Evaluation) |

---

## 3. Configuration & Versioning Mechanism
The backend service (`backend/app/services/food_recognition_service.py`) dynamically resolves the model version via environment variable:
```bash
FOOD_RECOGNITION_MODEL_VERSION=v2
```
- **Default:** `v2`
- **Fallback / Legacy support:** `v1` configuration can be loaded on demand without altering codebase.
- **Label Map:** Dynamically parsed from `label_map.json` without any hardcoded class lists.
- **V1 Checkpoint Preservation:** `models/trained/food_classifier.pth` remains untouched and unmodified on disk.

---

## 4. API Endpoints Verification

### A. Health & Diagnostics (`GET /api/health`)
```json
{
  "status": "ok",
  "service": "FoodFresh AI backend",
  "foodRecognitionModel": {
    "version": "v2",
    "checkpoint": "food_classifier_v2.pth",
    "classes": 24,
    "loaded": true
  }
}
```

### B. Known Pomegranate Test Image Inference
- **Input:** `data/raw/fruits-360-100x100-main/Test/Pomegranate 1/321_100.jpg`
- **HTTP Request:** `POST /api/food-recognition/predict`
- **HTTP Response:**
```json
{
  "success": true,
  "detectedFood": "Pomegranate",
  "recognitionConfidence": 100.0,
  "topPredictions": [
    { "food": "Pomegranate", "confidence": 100.0 },
    { "food": "Apple", "confidence": 0.0 },
    { "food": "Onion", "confidence": 0.0 }
  ],
  "source": "ml",
  "model": "EfficientNet-B0",
  "modelVersion": "v2",
  "status": "success"
}
```

---

## 5. Known Test Dataset Validation Suite

The live production endpoint was evaluated across 6 staple produce items from the untouched Fruits-360 test split:

| Food Category | Sample Test Image | V2 Prediction | Live Confidence | Top 3 Predictions | Status |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Pomegranate** | `Pomegranate 1/321_100.jpg` | **Pomegranate** | **100.0%** | Pomegranate: 100.0%, Apple: 0.0%, Onion: 0.0% | **PASS** |
| **Apple** | `Apple 10/r0_103_100.jpg` | **Apple** | **99.7%** | Apple: 99.7%, Cherry: 0.3%, Grape: 0.0% | **PASS** |
| **Banana** | `Banana 1/100_100.jpg` | **Banana** | **100.0%** | Banana: 100.0%, Pear: 0.0%, Cucumber: 0.0% | **PASS** |
| **Orange** | `Orange 1/30_100.jpg` | **Orange** | **100.0%** | Orange: 100.0%, Apple: 0.0%, Lemon: 0.0% | **PASS** |
| **Tomato** | `Tomato 1/10_100.jpg` | **Tomato** | **99.9%** | Tomato: 99.9%, Pepper: 0.1%, Apple: 0.0% | **PASS** |
| **Pineapple** | `Pineapple 1/12_100.jpg` | **Pineapple** | **100.0%** | Pineapple: 100.0%, Strawberry: 0.0%, Mango: 0.0% | **PASS** |

---

## 6. Real-World Evaluation Dataset Status
1. **Folder Scaffold:** Created `data/real_world_eval/` with structured subfolders:
   - `Apple/`, `Banana/`, `Orange/`, `Pomegranate/`, `Tomato/`, `Mango/`
2. **Current Content:** **0 images** (no synthetic or web-crawled images fabricated; authentic images to be provided by users/testers).
3. **Documentation:** Created `data/real_world_eval/README.md` explaining exact placement, camera angle criteria, and labeling rules.
4. **Evaluation Script:** Implemented `scripts/evaluate_real_world_food.py`.
5. **Initial Execution:**
   - Predictions: `reports/food_recognition_v2_real_world_predictions.csv` (initialized with standard schema).
   - Report: `reports/food_recognition_v2_real_world_report.md` documenting:
     > *"No real-world evaluation images were available. Confidence threshold requires additional calibration data."*

---

## 7. Frontend & Browser Integration Verification
- **Upload Flow:**
  - File picker reads user images, submits multipart payload to `/api/food-recognition/predict`.
  - Displays dynamic result with model version subtitle: `Inference via FoodFresh AI EfficientNet-B0 (V2)`.
  - Header badge dynamically displays: `✓ Food Recognition V2`.
- **Camera Flow:**
  - Live video stream preview modal activates on `Take Photo`.
  - Single-frame canvas grab directly converges into common upload pipeline.
  - "Cancel" cleanly shuts down camera hardware stream tracks.
- **Pipeline Segregation:**
  - **Freshness Classification:** Untrained and disconnected (`Not analyzed yet`).
  - **Shelf-Life Estimation:** Untrained and disconnected (`Not analyzed yet`).
  - **Eat First Priority:** Neutral pending state (`Not analyzed yet`).

---

## 8. Remaining Limitations
1. **Studio vs. Real-World Domain Shift:**
   Fruits-360 images are photographed on white background rotary discs. Real-world consumer photos with complex kitchen countertops, occlusion, and varied lighting may exhibit lower confidence until real-world fine-tuning or background augmentations are expanded.
2. **Confidence Calibration:**
   Softmax output confidence on out-of-distribution real photos should not be treated as true Bayesian probability without Platt scaling or temperature scaling once real-world test sets are collected.
3. **Downstream Pipeline Independence:**
   AgriFreshNET Freshness classification and FoodKeeper Shelf-life regression remain in preparation and will be trained in subsequent steps.
