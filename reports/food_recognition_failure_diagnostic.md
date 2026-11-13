# FoodFresh AI — Food Recognition Failure Diagnostic & Root-Cause Analysis
**Step 11: Pomegranate Misclassification Investigation & Correction Strategy**

---

## Executive Summary
When a real-world image of a **Pomegranate** was uploaded through the FoodFresh AI Analyze Food page, the model predicted:
1. **Apple** — 76.7%
2. **Cucumber** — 15.5%
3. **Banana** — 4.8%

A rigorous technical investigation across the Fruits-360 raw dataset, dataset preparation scripts, training manifests, label mappings, trained model weights, and inference pipelines reveals:

> **Primary Root Cause:**
> **Pomegranate is completely outside the current model's supported class vocabulary.**
> The current trained model (`models/trained/food_classifier.pth`) has exactly **12 output classes**. Pomegranate was **NEVER** an output class, was **NEVER** included in `label_map.json`, and was **NEVER** included in the training manifest.
> 
> Because softmax forces the output probabilities across the 12 candidate classes to sum to 100%, the model maps the visual features of Pomegranate (red coloration, spherical contour, smooth skin) to the visually closest class in its vocabulary: **Apple**.
>
> When tested against known, official Fruits-360 Pomegranate images from `data/raw/fruits-360-100x100-main/Test/Pomegranate 1/`, the model also consistently predicts **Apple** with 86.5% – 97.6% confidence.

---

## 1. Current Model Classes (12 Classes)
The current trained model vocabulary is defined by `data/processed/fruits360/label_map.json`:

| Class ID | Food Category | In Vocabulary? |
| :---: | :--- | :---: |
| 0 | Apple | Yes |
| 1 | Banana | Yes |
| 2 | Cucumber | Yes |
| 3 | Eggplant | Yes |
| 4 | Grape | Yes |
| 5 | Orange | Yes |
| 6 | Papaya | Yes |
| 7 | Peach | Yes |
| 8 | Pear | Yes |
| 9 | Pepper | Yes |
| 10 | Pineapple | Yes |
| 11 | Tomato | Yes |
| **—** | **Pomegranate** | **NO (MISSING)** |

---

## 2. Pomegranate Availability in Raw Datasets

### A. Raw Fruits-360 Dataset (`data/raw/fruits-360-100x100-main/`)
- **Training directory:** `Training/Pomegranate 1/` contains **492 images**.
- **Test directory:** `Test/Pomegranate 1/` contains **164 images**.
- **Total raw images:** **656 images**.
- **Normalization rule:** In `scripts/prepare_fruits360.py`, `Pomegranate 1` was mapped to `normalized_food = "Pomegranate"`. However, because `INITIAL_FOOD_SET` was hardcoded to only 12 items, Pomegranate was marked `selected = False` and excluded from manifests.

### B. AgriFreshNET Dataset
- AgriFreshNET does **not** contain Pomegranate (AgriFreshNET contains 8 foods: Banana, Bittermelon, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato).

---

## 3. Training & Test Manifest Inspection
Inspection of `data/processed/fruits360/fruits360_train_manifest.csv` and `fruits360_test_manifest.csv`:

| Food Category | Training Images | Test Images | Total Images | Status |
| :--- | :---: | :---: | :---: | :---: |
| Apple | 16,571 | 5,506 | 22,077 | In Manifest |
| Pear | 12,281 | 4,087 | 16,368 | In Manifest |
| Tomato | 10,259 | 3,413 | 13,672 | In Manifest |
| Pepper | 6,242 | 2,074 | 8,316 | In Manifest |
| Cucumber | 6,225 | 2,065 | 8,290 | In Manifest |
| Peach | 4,803 | 1,597 | 6,400 | In Manifest |
| Grape | 4,599 | 1,538 | 6,137 | In Manifest |
| Orange | 3,325 | 1,102 | 4,427 | In Manifest |
| Banana | 1,917 | 645 | 2,562 | In Manifest |
| Papaya | 1,217 | 404 | 1,621 | In Manifest |
| Pineapple | 983 | 329 | 1,312 | In Manifest |
| Eggplant | 708 | 236 | 944 | In Manifest |
| **Pomegranate** | **0** | **0** | **0** | **EXCLUDED** |
| **Total** | **69,130** | **22,996** | **92,126** | **12 Classes** |

---

## 4. Model Architecture & Checkpoint Verification
Inspection of `models/trained/food_classifier.pth`:
- **Architecture:** TorchVision EfficientNet-B0 with custom Linear head.
- **Weights shape in classifier head:** `classifier.1.weight` has shape `torch.Size([12, 1280])`.
- **Output dimension:** Exactly **12**.
- **Metadata inside checkpoint:**
  - `num_classes`: `12`
  - `food_to_id`: Matches `label_map.json` identically.
- **Verification:** The model is structurally capable of predicting only 12 specific classes. It is mathematically impossible for `models/trained/food_classifier.pth` to emit "Pomegranate" as a prediction.

---

## 5. Label Order & Mapping Verification
- `training manifest` numerical ID &rarr; `label_map.json` &rarr; `checkpoint metadata` &rarr; `inference service`.
- Checked:
  - `0`: Apple
  - `1`: Banana
  - `2`: Cucumber
  - `5`: Orange
  - `11`: Tomato
- **Finding:** The label order is 100% consistent across all components. There is **no label swap or index corruption**.

---

## 6. Preprocessing Verification
Compared:
- Training preprocessing (`ml/food_recognition/transforms.py`)
- Inference preprocessing (`backend/app/services/food_recognition_service.py`)

Both pipelines:
1. Convert PIL image to 3-channel RGB.
2. Resize to `224 × 224`.
3. Convert to tensor (`[0, 1]` range).
4. Apply standard ImageNet normalization:
   - Mean: `[0.485, 0.456, 0.406]`
   - Std: `[0.229, 0.224, 0.225]`
- **Finding:** Preprocessing is fully aligned and mathematically identical.

---

## 7. Known Dataset Image Tests (In-Domain vs Out-of-Vocabulary)
Inference execution was run using the live backend service and `TestClient` on both known in-domain test images and raw Fruits-360 Pomegranate test images:

| Image Path | Actual Food | In Vocabulary? | Predicted Food | Confidence | Correct? |
| :--- | :--- | :---: | :--- | :---: | :---: |
| `Test/Apple 10/r0_103_100.jpg` | **Apple** | Yes | Apple | 100.0% | **YES** |
| `Test/Banana 1/100_100.jpg` | **Banana** | Yes | Banana | 100.0% | **YES** |
| `Test/Orange 1/30_100.jpg` | **Orange** | Yes | Orange | 100.0% | **YES** |
| `Test/Tomato 1/10_100.jpg` | **Tomato** | Yes | Tomato | 100.0% | **YES** |
| `Test/Pineapple 1/12_100.jpg` | **Pineapple** | Yes | Pineapple | 100.0% | **YES** |
| `Test/Pomegranate 1/321_100.jpg` | **Pomegranate** | **NO** | Apple | 97.6% | **NO** |
| `Test/Pomegranate 1/322_100.jpg` | **Pomegranate** | **NO** | Apple | 97.6% | **NO** |
| `Test/Pomegranate 1/323_100.jpg` | **Pomegranate** | **NO** | Apple | 86.5% | **NO** |
| `Test/Pomegranate 1/324_100.jpg` | **Pomegranate** | **NO** | Apple | 96.8% | **NO** |
| `Test/Pomegranate 1/325_100.jpg` | **Pomegranate** | **NO** | Apple | 97.3% | **NO** |
| *User Real-World Camera Photo* | **Pomegranate** | **NO** | Apple | 76.7% | **NO** |

---

## 8. Backend API vs Direct ML Inference
- Direct `FoodRecognitionService.predict_image()` on `321_100.jpg`:
  `Apple (97.6%)`, `Grape (1.1%)`, `Pear (1.0%)`.
- FastAPI `POST /api/food-recognition/predict` on `321_100.jpg`:
  `Apple (97.6%)`, `Grape (1.1%)`, `Pear (1.0%)`.
- **Finding:** The backend endpoint accurately executes the model without alteration.

---

## 9. Confidence Behavior & Open-Set Classification
- Standard softmax normalization maps raw unbounded logits $z_i$ into probabilities:
  $$P(y = i \mid x) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}$$
- When an object outside the $K=12$ classes is presented, the model has no "None of the above" output neuron.
- High softmax confidence (76.7% – 97.6%) is an inherent characteristic of closed-set neural classifiers on out-of-distribution / out-of-vocabulary images.
- Red color, spherical geometry, and fruit texture activate the features strongly associated with the red Apple class weights.

---

## 10. Real-World Domain Shift Analysis
Beyond the vocabulary omission, real-world camera images exhibit domain shift compared to Fruits-360:
1. **Background:** Fruits-360 images possess an artificial pure-white background created by an automated rotary rig; real kitchen images possess countertops, hands, cutting boards, plates, and shadows.
2. **Lighting:** Fruits-360 images feature specular white studio illumination; real-world photos contain ambient household lighting, colored reflections, and cast shadows.
3. **Scale & Context:** Fruits-360 crops are tightly centered on single fruit units (100x100 px); real-world captures contain variable perspective, scale, and background objects.

---

## 11. Root Cause Summary
1. **Primary Root Cause (100% Determinative):**
   **Pomegranate is NOT an output class.** The model was trained on only 12 classes, excluding Pomegranate.
2. **Secondary Contributing Factor (Overconfidence):**
   Closed-set softmax forced the out-of-vocabulary Pomegranate into the nearest visual neighbor (**Apple**).
3. **Tertiary Factor (Domain Shift):**
   Pure white background training makes the model more sensitive to background context when real photos are analyzed.

---

## 12. Recommended Correction Strategy & Retraining Plan

### A. Expand Food Recognition Vocabulary
Expand `INITIAL_FOOD_SET` in dataset preparation to include high-frequency produce items available in Fruits-360, specifically:
- **Pomegranate** (492 train, 164 test images)
- Plus other staple kitchen produce available in Fruits-360 (e.g., Strawberry, Lemon, Mango, Watermelon, Guava, etc.).

### B. Add "Other / Unknown" or Calibrated Low-Confidence Threshold
- Implement temperature scaling or an entropy/margin-based threshold to reliably trigger `"status": "low_confidence"` when out-of-vocabulary produce is analyzed.

### C. Realistic Background Augmentation
- During fine-tuning, introduce random background replacement, random crops, and mild lighting variations to improve real-world generalization from white-background images.

### D. Safe Versioning Protocol
- **DO NOT overwrite** `models/trained/food_classifier.pth`.
- Train and validate the updated model under a dedicated new checkpoint:
  **`models/trained/food_classifier_v2.pth`**
- Update manifests under versioned names or unified multi-class manifests.

---

## 13. Explicit Pomegranate Verification Checklist

1. **Is Pomegranate present in the original dataset?**
   **YES.** Raw Fruits-360 contains `Training/Pomegranate 1` (492 images) and `Test/Pomegranate 1` (164 images).
2. **Is Pomegranate present in the training manifest?**
   **NO.** `fruits360_train_manifest.csv` contains 0 Pomegranate images.
3. **Is Pomegranate present in `label_map.json`?**
   **NO.** Only 12 classes exist, none of which are Pomegranate.
4. **Is Pomegranate an output class of the trained checkpoint?**
   **NO.** Output head is `Linear(1280, 12)`.
5. **Does the model correctly classify a known Fruits-360 Pomegranate test image?**
   **NO.** It predicts **Apple** with 86.5% – 97.6% confidence.
6. **Does the backend return the same prediction as direct inference?**
   **YES.** Exactly identical.
7. **Is the real-world Pomegranate failure caused primarily by missing class, label mapping, preprocessing, model weakness, or domain shift?**
   **Primarily missing class.** Pomegranate was never in the training set or classifier output head. Closed-set softmax forced the misclassification to Apple.
