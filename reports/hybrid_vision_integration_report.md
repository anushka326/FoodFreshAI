# FoodFresh AI — Master Hybrid Vision Integration Report

**Date:** September 26, 2026  
**Environment:** Windows (AMD64) • Python 3.12.4 • PyTorch 2.6.0+cu124 • CUDA Enabled  
**Architecture:** Open-Vocabulary Detection + Zero-Shot Semantic Classification + Domain Specialist + Visible Freshness Classifier

---

## 1. Overview & Architecture Summary

FoodFresh AI has transitioned from the previous closed-set classification pipeline to a **Master Hybrid Vision Model Stack**. Rather than forcing a single network to perform all visual and biological tasks, the new architecture decouples localization, zero-shot open-vocabulary semantic matching, raw agricultural classification, and visible freshness estimation:

```
                     USER IMAGE
                         │
                         ▼
             [1] Grounding DINO Base
             (Open-Vocabulary Detector)
                         │
                         ▼
                 Detected Objects
                         │
                         ▼
               Food Region Selection & Crop
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
    [2] Raw Food ResNet-50      [3] SigLIP 2 Base
    (90-Class Specialist)       (Zero-Shot Open Vocab)
             │                       │
             └───────────┬───────────┘
                         ▼
             Deterministic Fusion & Gate
                         │
                         ▼
                 Food Identity
                         │
                         ▼
          [4] Food Freshness Detector
          (ResNet-18 Visible Quality)
                         │
                         ▼
             Estimated Visible Freshness
                         │
                         ▼
           [5] Shelf-Life Component
          (FoodKeeper XGBoost — Pending)
                         │
                         ▼
                FoodFresh AI Result
```

---

## 2. Models Installed, Sources & Sizes

| Role | Model Identifier | Hugging Face Source | Local Storage Path | Parameters | Model Size on Disk |
|------|------------------|---------------------|--------------------|------------|--------------------|
| **Object Detection** | `IDEA-Research/grounding-dino-base` | [HuggingFace Repo](https://huggingface.co/IDEA-Research/grounding-dino-base) | `models/pretrained/grounding_dino/` | 232,315,264 (~232M) | 938 MB (`model.safetensors`) |
| **Open-Vocab Food Identification** | `google/siglip2-base-patch16-224` | [HuggingFace Repo](https://huggingface.co/google/siglip2-base-patch16-224) | `models/pretrained/siglip2/` | 375,187,970 (~375M) | 1,431 MB (`model.safetensors`) |
| **Raw Food Specialist** | `ibrahimdaud/raw-food-recognition-models` | [HuggingFace Repo](https://huggingface.co/ibrahimdaud/raw-food-recognition-models) | `models/pretrained/raw_food_resnet50/` | 23,692,442 (~23.7M) | 271 MB (`resnet50_pytorch_model.bin`) |
| **Visible Freshness** | `nathansekar/food-freshness-detector` | [HuggingFace Repo](https://huggingface.co/nathansekar/food-freshness-detector) | `models/pretrained/freshness_resnet18/` | 11,690,496 (~11.7M) | 44.7 MB (`model_weights.pth`) |
| **Shelf-Life Estimation** | Project XGBoost / FoodKeeper | In-tree project dataset | `ml/shelf_life/` (pending) | Pending integration | N/A |

---

## 3. Individual Model Test Results

All four models were independently tested across canonical project images (`reports/hybrid_model_individual_tests.csv`):

| Test Image | Model | Prediction | Confidence / Score | Top 3 Predictions | Latency (CUDA) |
|---|---|---|---|---|---|
| **Pomegranate** | Grounding DINO | `pomegranate` | 65.87% | pomegranate (65.87%) | 2514 ms (first-call) |
| | SigLIP 2 | `pomegranate` | 98.35% | pomegranate (98.35%), apple (0.68%), passion fruit (0.13%) | 389 ms |
| | Raw Food ResNet-50 | `Pomegranate` | 98.60% | Pomegranate (98.60%), Beetroot (0.58%), Apple (0.30%) | 143 ms |
| | Freshness ResNet-18 | `Fresh` | 50.98% | Fresh: 50.98%, Rotten: 48.98%, Slightly Spoiled: 0.04% | 88 ms |
| **Tomato** | Grounding DINO | `tomato pepper` | 58.57% | tomato pepper (58.57%), tomato (44.15%) | 523 ms |
| | SigLIP 2 | `tomato` | 96.68% | tomato (96.68%), bell pepper (1.20%), chili pepper (0.85%) | 296 ms |
| | Raw Food ResNet-50 | `Bell Pepper` | 72.71% | Bell Pepper (72.71%), Tomato (18.42%), Orange (0.81%) | 35 ms |
| | Freshness ResNet-18 | `Slightly Spoiled` | 77.41% | Slightly Spoiled: 77.41%, Rotten: 22.42%, Fresh: 0.17% | 14 ms |
| **Apple** | Grounding DINO | `apple` | 65.41% | apple (65.41%) | 513 ms |
| | SigLIP 2 | `peach` | 56.92% | peach (56.92%), apple (21.77%), plum (8.55%) | 277 ms |
| | Raw Food ResNet-50 | `Apple` | 96.44% | Apple (96.44%), Mango (1.51%), Radish (0.65%) | 27 ms |
| | Freshness ResNet-18 | `Fresh` | 56.35% | Fresh: 56.35%, Rotten: 43.60%, Slightly Spoiled: 0.05% | 14 ms |
| **Banana** | Grounding DINO | `banana` | 82.18% | banana (82.18%) | 529 ms |
| | SigLIP 2 | `banana` | 99.50% | banana (99.50%), lemon (0.12%), mango (0.07%) | 278 ms |
| | Raw Food ResNet-50 | `Sweet Potato` | 62.10% | Sweet Potato (62.10%), Pumpkin (6.68%), Banana (6.41%) | 35 ms |
| | Freshness ResNet-18 | `Slightly Spoiled` | 93.23% | Slightly Spoiled: 93.23%, Rotten: 6.74%, Fresh: 0.03% | 17 ms |
| **Orange** | Grounding DINO | `pear` | 27.40% | pear (27.40%), mango (25.97%) | 529 ms |
| | SigLIP 2 | `orange` | 76.71% | orange (76.71%), lime (19.12%), lemon (14.22%) | 279 ms |
| | Raw Food ResNet-50 | `Pear` | 44.94% | Pear (44.94%), Mango (20.47%), Orange (2.55%) | 23 ms |
| | Freshness ResNet-18 | `Slightly Spoiled` | 53.44% | Slightly Spoiled: 53.44%, Rotten: 46.40%, Fresh: 0.16% | 16 ms |

---

## 4. End-to-End Hybrid Results & Real-World Evaluation

Recorded in `reports/hybrid_real_world_evaluation.csv`:

| Test Target | Hybrid Prediction | Hybrid Confidence | Fusion Status | Freshness State | Latency | Decision Rationale |
|---|---|---|---|---|---|---|
| **Pomegranate** | **Pomegranate** | **98.47%** | `success` | Fresh (51.0%) | 3228 ms | Full consensus: Both Raw Food ResNet-50 (98.6%) and SigLIP 2 (98.35%) agree on Pomegranate. |
| **Tomato** | **Tomato** | **65.42%** | `success` | Slightly Spoiled (98.3%) | 904 ms | SigLIP 2 semantic prediction (`tomato`, 95.96%) supported by Raw Food specialist (`Tomato` in top candidates). |
| **Apple** | **Apple** | **66.57%** | `success` | Fresh (56.4%) | 851 ms | Specialist Raw Food prediction (`Apple`, 96.44%) supported by SigLIP 2 in top candidates. |
| **Banana** | **Banana** | **62.25%** | `success` | Slightly Spoiled (83.4%) | 856 ms | SigLIP 2 semantic prediction (`banana`, 99.47%) supported by Raw Food specialist. |
| **Orange** | **Orange** | **32.66%** | `success` | Slightly Spoiled (93.2%) | 895 ms | SigLIP 2 semantic prediction (`orange`, 52.73%) supported by Raw Food specialist. |
| **Multi-Food** | **Banana** | **92.49%** | `success` | Slightly Spoiled (57.0%) | 1011 ms | Detector localized separate candidate regions; detector and SigLIP 2 agree on Banana crop. |

---

## 5. Multi-Object Detection Verification

- **Input:** Composite multi-item image containing Apple, Banana, and Tomato side-by-side (`data/real_world_eval/multi_apple_banana_tomato.jpg`).
- **Grounding DINO Behavior:** Successfully extracted distinct candidate bounding boxes across the frame:
  1. `banana` (76.45% confidence)
  2. `pepper / tomato` (69.73% confidence)
  3. `apple` (49.35% confidence)
- **Pipeline Processing:** Primary region was isolated without crashing, and classification was dispatched to the individual crop.

---

## 6. Unknown & Uncertain Case Handling

The hybrid engine enforces transparent uncertainty gating rather than hallucinating or forcing an arbitrary top label:
- **Synthetic Ambiguous Noise / Out-of-Distribution Test:**
  - `analysisStatus`: `"uncertain"`
  - `detectedFood`: `None`
  - `topCandidates`: Mango (88.72%), Peas (14.17%), Cereal (6.80%)
  - `decisionMessage`: *"Conflicting model evidence: Raw Food predicts Mango (88.72%), while SigLIP 2 predicts peas (14.17%). Marking as uncertain."*
- **Safety Benefit:** Protects the user from incorrect categorization when lighting is defective or an item is outside standard food classes.

---

## 7. Visible Freshness Classification

- **Model:** `nathansekar/food-freshness-detector` (ResNet-18 fastai backbone with AdaptiveConcatPool2d).
- **Official Vocabulary:** `['fresh', 'rotten', 'slightly_spoiled']`.
- **Display Terminology:** Expressed strictly as **"Estimated Visible Freshness"** (e.g. *Fresh*, *Slightly Spoiled*, *Rotten*).
- **Audit Note:** The application does **not** claim microbiological safety or laboratory purity. Visible freshness reflects visual surface indicators only.

---

## 8. Shelf-Life Status

- **Status:** `not_available`
- **Display:** Displayed as `"Not available yet — Awaiting FoodKeeper data integration"`.
- **Eat First Priority:** Displayed as `"Not available until shelf-life is integrated"`.
- **Integrity Rule:** Zero fabricated numbers (no fake "3 days", "5 days", etc.).

---

## 9. Backend & Frontend Verification

- **Backend:** FastAPI listening on `http://127.0.0.1:8000`. Endpoint `POST /api/food-recognition/predict` returns:
  ```json
  {
    "success": true,
    "analysisStatus": "success",
    "detectedFood": "Pomegranate",
    "recognitionConfidence": 98.47,
    "topPredictions": [...],
    "detectedObjects": [...],
    "foodRecognition": { "groundingDino": {...}, "rawFoodResNet": {...}, "siglip2": {...} },
    "freshness": { "status": "success", "label": "Fresh", "score": 50.98, ... },
    "shelfLife": { "status": "not_available" },
    "modelVersions": {
      "detector": "IDEA-Research/grounding-dino-base",
      "foodSemantic": "google/siglip2-base-patch16-224",
      "foodSpecialist": "ibrahimdaud/raw-food-recognition-models",
      "freshness": "nathansekar/food-freshness-detector"
    }
  }
  ```
- **Frontend:** Vite React application on `http://localhost:3000`.
  - Landing, Login, Dashboard, and Analyze Food pages verified.
  - Data binding directly displays the new backend payload.
  - Model stack attribution badge displayed.

---

## 10. Performance Benchmarks

- **Device:** Windows 11 x86_64, NVIDIA CUDA GPU enabled
- **Model Load Time (all 4 models):** ~12.4 seconds (cached weights)
- **Per-Image Inference Latency:**
  - Grounding DINO: 450 – 550 ms
  - SigLIP 2: 260 – 350 ms
  - Raw Food ResNet-50: 15 – 35 ms
  - Freshness ResNet-18: 8 – 20 ms
  - Total Pipeline Latency: ~850 – 1050 ms per image (after GPU warmup)

---

## 11. Safety & Accuracy Disclaimers

1. **Food Recognition:** Grounding DINO and SigLIP 2 provide open-vocabulary zero-shot capabilities. Recognition is probabilistic and dependent on illumination, occlusion, and packaging.
2. **Freshness Estimation:** Visible freshness is based entirely on optical surface characteristics. It cannot detect internal spoilage, foodborne pathogens, toxins, or anaerobic bacterial growth.
3. **Food Safety:** The system never claims food is guaranteed "safe to eat".
4. **Shelf-Life:** Shelf-life estimation is explicitly disconnected until FoodKeeper and project XGBoost models are verified.
