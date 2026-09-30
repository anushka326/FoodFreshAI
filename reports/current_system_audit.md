# FoodFresh AI — Current System Audit Report

**Audit Date**: September 26, 2026  
**Auditor**: FoodFresh AI Engineering  
**Scope**: Complete System Audit (Backend, Frontend, ML Models, Datasets, Preprocessing, Shelf-Life, Eat First, FreshoBuddy)

---

## Executive Summary

The FoodFresh AI application integrates a Master Hybrid Vision Pipeline for food item detection, semantic classification, visible surface freshness estimation, USDA FoodKeeper shelf-life estimation, and deterministic Eat First consumption urgency. The system runs an end-to-end FastAPI backend (`backend/app/main.py`) and a React/Vite frontend (`frontend/src`).

While food recognition performs reliably across diverse produce, manual testing revealed that the current freshness estimation model (`nathansekar/food-freshness-detector` ResNet-18) exhibits erratic predictions and misclassifications on real produce (e.g. predicting fresh green chilli, moldy oranges, and rotten tomatoes all as "Slightly Spoiled" with high confidence). Furthermore, FreshoBuddy currently operates on client-side mock logic without Gemini API integration or persistent multi-session chat storage.

---

## 1. Current Model Inventory

| Pipeline Role | Model Architecture | Pretrained Checkpoint / Base | Source / Location | Parameter Count | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Object Detection** | Grounding DINO Base | `IDEA-Research/grounding-dino-base` | `models/pretrained/grounding_dino_base` | ~172M | Active |
| **Zero-Shot Semantic** | SigLIP 2 Base (Patch 16, 224) | `google/siglip2-base-patch16-224` | `models/pretrained/siglip2` | ~200M | Active |
| **Raw Food Specialist** | ResNet-50 | Custom trained on raw food produce | `models/pretrained/raw_food_resnet50` | ~25.5M | Active |
| **Visible Freshness** | ResNet-18 (fastai head) | `nathansekar/food-freshness-detector` | `models/pretrained/freshness_resnet18/model_weights.pth` | ~11.7M | Active (Audit Target) |
| **Shelf-Life** | USDA FoodKeeper Rule Index | USDA FoodKeeper JSON | `data/raw/foodkeeper/FoodKeeper.json` | 661 products | Active |
| **Eat First** | Deterministic Priority Engine | Rule Hierarchy (4 tiers) | `backend/app/services/eat_first_service.py` | N/A | Active |
| **FreshoBuddy** | AI Food Companion | Mock frontend heuristic engine | `frontend/src/services/freshoBuddyService.js` | N/A | Needs Gemini Backend |

---

## 2. Current Freshness Model Checkpoint & Architecture

- **Checkpoint File**: `models/pretrained/freshness_resnet18/model_weights.pth` (46.9 MB)
- **Configuration**: `models/pretrained/freshness_resnet18/config.json`
  ```json
  {
    "arch": "resnet18",
    "n_classes": 3,
    "img_size": 224
  }
  ```
- **Architecture**:
  - Backbone: Standard Torchvision `resnet18(weights=None)` stripped of its final pooling and classification layer (`nn.Sequential(*list(base.children())[:-2])`).
  - Pooling: `AdaptiveConcatPool2d` (concatenates AdaptiveAvgPool2d(1) + AdaptiveMaxPool2d(1) $\rightarrow$ 1024 channels).
  - Head:
    - `Flatten` $\rightarrow$ `BatchNorm1d(1024)` $\rightarrow$ `Dropout(0.25)`
    - `Linear(1024, 512, bias=False)` $\rightarrow$ `ReLU(inplace=True)`
    - `BatchNorm1d(512)` $\rightarrow$ `Dropout(0.5)`
    - `Linear(512, 3, bias=False)`
- **Softmax / Logits**: Raw linear output passed through `torch.softmax(logits, dim=1)`.

---

## 3. Current Preprocessing & Transforms

In `ml/hybrid_vision/preprocessing.py`:
- **Image Input Handling**: `load_image_rgb()` reads bytes, path, or PIL, applies `ImageOps.exif_transpose`, and ensures RGB mode.
- **Bounding Box Crop**: `crop_bounding_box()` crops detected food object with an 8% margin clamp (`CROP_MARGIN_RATIO = 0.08`).
- **ResNet Normalization**:
  - Transform:
    ```python
    T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    ```
  - **Identified Preprocessing Nuance**:
    - Direct squishing to `(224, 224)` alters the natural aspect ratio of elongated foods (e.g. green chilli, cucumber, banana).
    - Standard fastai / torchvision models typically expect aspect-ratio-preserving resize (`Resize(256)`) followed by center crop (`CenterCrop(224)`), or squishing depending on original training transforms.

---

## 4. Current Freshness Classes & Mapping

- **Vocabulary**: `models/pretrained/freshness_resnet18/vocab.json`
  - Index 0: `"fresh"`
  - Index 1: `"rotten"`
  - Index 2: `"slightly_spoiled"`
- **Display Label Mapping**:
  - `"fresh"` $\rightarrow$ `"Fresh"`
  - `"slightly_spoiled"` $\rightarrow$ `"Slightly Spoiled"`
  - `"rotten"` $\rightarrow$ `"Rotten"`
- **Calibration Status**: None currently implemented. The system directly takes `torch.argmax(probs)` and reports the raw softmax probability as confidence without uncertainty gating or temperature scaling.

---

## 5. Current FoodKeeper Integration

- **Dataset**: `data/raw/foodkeeper/FoodKeeper.json` (631.8 KB)
- **Product Entries**: 661 items across 25 categories (Parsed into memory upon initialization in `backend/app/services/shelf_life_service.py`).
- **Normalization & Search**:
  - Query cleaning via regex (`_normalize_query`).
  - Three-tier matching:
    1. Exact normalized name match.
    2. Curated alias map (`FOODKEEPER_ALIASES` with ~40 produce mappings).
    3. Keyword / token fallback match.
- **Identified Normalization Gaps**:
  - Specific produce like "Green Chilli", "Chili Pepper", and "Bell Pepper" require rigorous canonical separation rather than loose token grouping.
  - Ambiguous matches should safely return `status = unavailable` with reason `ambiguous FoodKeeper match` rather than guessing.

---

## 6. Current Shelf-Life Logic

- **Implementation**: `backend/app/services/shelf_life_service.py`
- **Supported Storage Contexts**:
  - `countertop`, `pantry`, `ambient` $\rightarrow$ Maps to `Pantry` FoodKeeper attributes.
  - `fridge`, `crisper`, `refrigerate` $\rightarrow$ Maps to `Refrigerate` FoodKeeper attributes.
- **Reference Shelf-Life Extraction**:
  - Evaluates `DOP_Pantry_Min`, `DOP_Pantry_Max`, `Pantry_Min`, etc., and metric conversions (`days`, `weeks`, `months`).
  - Supports special "When Ripe" handling.
- **Remaining Quality Formula**:
  - `rem_min = max(0, ref_min - days_stored)`
  - `rem_max = max(0, ref_max - days_stored)`
  - Heuristic visible freshness adjustment applied (Rotten $\rightarrow$ 0 days; Slightly Spoiled $\rightarrow$ 50% reduction).
- **Zero / Negative-Day Handling**:
  - Clamped to `0.0`, but needs explicit explanatory text ("Estimated remaining quality: 0 days" + reason) according to Phase 11.

---

## 7. Current Eat First Logic

- **Implementation**: `backend/app/services/eat_first_service.py`
- **Engine Type**: Deterministic rule hierarchy (NOT a machine learning model).
- **Inputs**: `shelf_life_data` (`remaining.minDays`, `remaining.maxDays`), `freshness_label`.
- **Tiers**:
  1. `VERY_HIGH` (Rotten, or $\le 1$ day remaining).
  2. `HIGH` (Slightly Spoiled, or $\le 3$ days remaining).
  3. `MEDIUM` ($\le 7$ days remaining).
  4. `LOW` ($> 7$ days remaining).
- **Safeguard**: If shelf life is unavailable, returns `status = "unavailable"` with reason `"Eat First requires an available shelf-life estimate."`

---

## 8. Current FreshoBuddy Implementation

- **Location**: `frontend/src/pages/FreshoBuddyPage/FreshoBuddyPage.jsx` and `frontend/src/services/freshoBuddyService.js`.
- **Status**: Currently a client-side mock rule-engine simulating responses with artificial `setTimeout` delays.
- **Missing Elements**:
  - No FastAPI backend route for chat (`/api/fresho-buddy/chat`).
  - No Google Gemini API integration.
  - No environment variable loading of `GEMINI_API_KEY`.
  - No system prompt infusing FoodFresh AI domain knowledge, storage guidelines, or safety disclaimers.

---

## 9. Current Chat Storage & User State

- **Current State**: `sessionStorage.getItem('foodfresh_active_food_context')` and ephemeral React state in `FreshoBuddyPage.jsx`.
- **Identified Deficiencies**:
  - Chat messages are lost when the page refreshes or when "New Conversation" is clicked.
  - No persistent database tables for `conversations` or `messages`.
  - No multi-conversation sidebar grouped by date (Today, Yesterday, Older).
  - No user isolation based on authenticated user IDs.

---

## 10. Current Known Issues & Root Causes

1. **Freshness False Positives & Mode Collapse**:
   - The ResNet-18 model predicts "Slightly Spoiled" for widely diverse inputs, including fresh green chillies and severely rotten tomatoes/oranges.
   - Root causes: Domain shift (the pretrained web dataset has distinct background/lighting distributions compared to real kitchen counter environments), potential aspect-ratio distortion during resizing, and lack of confidence calibration.
2. **Missing Real Gemini Backend**:
   - FreshoBuddy requires a real backend endpoint using Google GenAI SDK, reading `GEMINI_API_KEY` securely from the backend environment.
3. **Missing Persistent Conversation History**:
   - FreshoBuddy lacks a database-backed chat history with sidebar navigation and user isolation.
4. **Food Safety Language**:
   - Must strictly ensure all surfaces use "Estimated visible freshness" and "Estimated remaining quality", avoiding definitive safety claims ("Safe to eat", "Definitely rotten").
