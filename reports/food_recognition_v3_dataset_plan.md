# FoodFresh AI — Food Recognition V3 Domain Adaptation Dataset Plan

**Step 15 Technical Blueprint: Cross-Dataset Synthesis, Domain Balancing & Leakage-Free Architecture**

---

## 1. Executive Summary & Problem Diagnosis
Food Recognition V2 achieved a top-1 test accuracy of **99.52%** on the Fruits-360 benchmark, but real-world consumer testing revealed severe domain shift failures:
- **Real-world Pomegranate** $\rightarrow$ Pear (93.6% confidence)
- **Real-world Tomato** $\rightarrow$ Pineapple (63.7% confidence)
- **Real-world Apple** $\rightarrow$ Cucumber (62.3% confidence)

The technical root cause is **domain shift**: Fruits-360 is photographed exclusively on pure-white `#FFFFFF` rotary discs under sterile studio lighting. The convolutional filters in EfficientNet-B0 learn to heavily rely on high-contrast object-to-white silhouettes rather than true invariant textural and geometric semantics. When confronted with complex kitchen countertops, ambient shadows, plates, or hand-held cameras, the model's feature maps collapse into nearest-neighbor confusion.

This document establishes the dataset architecture, cross-dataset mapping, sampling strategy, and data collection protocol required to train **Food Recognition V3**.

---

## 2. Target Class Taxonomy (24 Classes)

| Class ID | Food Name | Fruits-360 Status | AgriFreshNET Status | Domain Coverage |
| :---: | :--- | :---: | :---: | :--- |
| 0 | **Apple** | Available (22,077) | None | Single-Domain (Studio Only) |
| 1 | **Avocado** | Available (4,077) | None | Single-Domain (Studio Only) |
| 2 | **Banana** | Available (2,562) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 3 | **Cherry** | Available (12,230) | None | Single-Domain (Studio Only) |
| 4 | **Corn** | Available (1,216) | None | Single-Domain (Studio Only) |
| 5 | **Cucumber** | Available (8,290) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 6 | **Eggplant** | Available (944) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 7 | **Grape** | Available (6,137) | None | Single-Domain (Studio Only) |
| 8 | **Guava** | Available (656) | None | Single-Domain (Studio Only) |
| 9 | **Lemon** | Available (1,312) | None | Single-Domain (Studio Only) |
| 10 | **Mango** | Available (1,626) | None | Single-Domain (Studio Only) |
| 11 | **Onion** | Available (4,173) | None | Single-Domain (Studio Only) |
| 12 | **Orange** | Available (4,427) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 13 | **Papaya** | Available (1,621) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 14 | **Peach** | Available (6,400) | None | Single-Domain (Studio Only) |
| 15 | **Pear** | Available (16,368) | None | Single-Domain (Studio Only) |
| 16 | **Pepper** | Available (8,316) | None | Single-Domain (Studio Only) |
| 17 | **Pineapple** | Available (1,312) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 18 | **Plum** | Available (4,196) | None | Single-Domain (Studio Only) |
| 19 | **Pomegranate** | Available (656) | None | Single-Domain (Studio Only) |
| 20 | **Potato** | Available (2,404) | None | Single-Domain (Studio Only) |
| 21 | **Strawberry** | Available (2,906) | None | Single-Domain (Studio Only) |
| 22 | **Tomato** | Available (13,672) | **Available (1,770)** | Multi-Domain (Studio + Real World) |
| 23 | **Watermelon** | Available (632) | None | Single-Domain (Studio Only) |

### Overlap Summary
- **Overlapping Classes:** **7 classes** (Banana, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato).
- **Missing / Single-Domain Classes:** **17 classes** (Apple, Avocado, Cherry, Corn, Grape, Guava, Lemon, Mango, Onion, Peach, Pear, Pepper, Plum, Pomegranate, Potato, Strawberry, Watermelon).
- **AgriFreshNET Non-Target Food:** Bittermelon (1,770 images excluded from Food Recognition vocabulary).

---

## 3. Training Strategy Comparison

### Strategy A: Fruits-360 Only (Current V2 Baseline)
- **Feasibility:** High.
- **Limitation:** Incurable laboratory-to-wild domain shift. Real-world kitchen background and ambient illumination cause severe misclassifications.
- **Verdict:** Unacceptable for production.

### Strategy B: Fruits-360 + AgriFreshNET Only
- **Feasibility:** High (both datasets already local on disk).
- **Advantage:** Introduces 12,390 natural smartphone images across 7 classes with domestic countertops and varying degradation states.
- **Critical Flaw:** Severe cross-class asymmetry. The 7 multi-domain classes would learn realistic invariant features, while the remaining 17 classes would remain strictly bound to white backgrounds. A real-world Apple would continue to be misclassified as Cucumber or Pear because only Cucumber/Pear/Pineapple would have diverse background representations.
- **Verdict:** Incomplete solution.

### Strategy C: Fruits-360 + AgriFreshNET + Targeted Real-World Collection (Recommended)
- **Feasibility:** High when executed via a staged collection protocol.
- **Advantage:** Bridges the domain gap across **all 24 classes**. AgriFreshNET provides heavy domain adaptation for 7 staple produce classes, while targeted manual collection supplies 20–100 authentic smartphone images for the 17 single-domain classes (especially Apple, Pomegranate, Onion, Mango, and Potato).
- **Verdict:** **RECOMMENDED STRATEGY FOR V3.**

---

## 4. Separation of Concerns (Orthogonal Pipelines)

### A. Freshness Labels $\neq$ Food Identity Labels
In AgriFreshNET, classes are named `Fresh Banana(1-4)`, `Semi fresh banana(4-7)`, and `Rotten banana(7-13)`.
- **Enforced Rule:** During Food Recognition V3 ingestion, all 3 stages are mapped strictly to `food_name = "Banana"`.
- Under no circumstances should "Fresh Banana" or "Rotten Tomato" become output classes of the food recognizer.
- Freshness classification remains a strictly independent downstream task.

### B. Shelf-Life Annotations $\neq$ Food Identity Labels
Parenthetical post-harvest intervals such as `(1-4)` or `(24-35)` belong exclusively to the Shelf-Life regression module and will be parsed as target variables for XGBoost or multi-task heads, never as classification categories.

---

## 5. Domain Balancing & Sampling Strategy
Simply concatenating Fruits-360 and AgriFreshNET would cause severe dataset imbalance:
- Fruits-360 has 128,210 images (biased towards Apple: 22,077 and Pear: 16,368).
- AgriFreshNET has 12,390 relevant images (exactly 1,770 per class).
- Real-world collection will initially yield 20–100 images per class.

Without intervention, standard mini-batch gradient descent would sample >90% studio disc images.

### Proposed Sampling Architecture
1. **Stratified Dual-Domain Batch Sampling (WeightedRandomSampler):**
   - Each mini-batch (batch size = 64) is constructed with fixed domain proportions:
     - 50% Fruits-360 studio images (preserving high morphological diversity).
     - 40% AgriFreshNET real-world images (teaching background and lighting invariance).
     - 10% Manual real-world consumer images (anchoring user environment distribution).
2. **Effective Class Weighting:**
   - Compute inverse class frequencies within each domain to prevent dominant classes (e.g. Apple, Tomato) from overwhelming rare classes (e.g. Watermelon, Guava, Pomegranate).

---

## 6. Leakage Prevention Protocol

### A. AgriFreshNET Burst Frame Containment
AgriFreshNET contains consecutive burst frames derived from physical photo sessions (e.g. `aug_0_IMG_20251104...` and `aug_100_IMG_20251104...`).
- **Standard:** Split strictly by **base physical photo stem** (strip `aug_\d+_`).
- All augmentations of a physical photo stay in either `train`, `val`, or `test`.

### B. Real-World Specimen Containment
- All photographs of the same physical specimen or session must belong to the exact same partition.
- Cross-split contamination of near-duplicate specimen angles is strictly prohibited.

---

## 7. Data Augmentation Strategy for V3
To narrow the domain shift during training:
1. **Background Blending / Mosaic Cutout:**
   - Synthetic background insertion behind segmented Fruits-360 objects to break white-background reliance.
2. **Photometric Augmentations:**
   - Random ColorJitter (brightness $\pm 0.25$, contrast $\pm 0.25$, saturation $\pm 0.25$, hue $\pm 0.05$).
   - Random Gaussian Blur ($\sigma \in [0.1, 2.0]$) to simulate smartphone focal blur.
3. **Geometric Augmentations:**
   - RandomResizedCrop(224, scale=(0.7, 1.0)) to simulate variable user framing distances.
   - RandomHorizontalFlip(p=0.5), RandomRotation(degrees=20).

---

## 8. Fine-Tuning Strategy for V3
- **Base Architecture:** Pretrained EfficientNet-B0 with 24-class classification head (`Linear(1280, 24)`).
- **Stage 1 (Head Alignment):**
  - Freeze backbone; train classification head with AdamW ($\text{LR} = 1\times 10^{-3}$, weight decay $1\times 10^{-4}$) for 3 epochs.
- **Stage 2 (Domain Adaptation Fine-Tuning):**
  - Unfreeze top convolutional blocks (layers 5–7); fine-tune end-to-end with low learning rate ($\text{LR} = 1\times 10^{-4}$ with cosine annealing) for 4 epochs using AMP.

---

## 9. Manual Real-World Collection Milestones

| Target Food | Overlap Status | Phase A Target | Phase B Target | Priority |
| :--- | :--- | :---: | :---: | :---: |
| **Pomegranate** | Fruits-360 Only | 30 images | 75 images | **CRITICAL (Known Failure)** |
| **Apple** | Fruits-360 Only | 30 images | 75 images | **CRITICAL (Known Failure)** |
| **Tomato** | Multi-Domain | 20 images | 50 images | **CRITICAL (Known Failure)** |
| **Mango** | Fruits-360 Only | 25 images | 60 images | HIGH |
| **Onion** | Fruits-360 Only | 25 images | 60 images | HIGH |
| **Potato** | Fruits-360 Only | 25 images | 60 images | HIGH |
| **Avocado** | Fruits-360 Only | 20 images | 50 images | MEDIUM |
| **Lemon** | Fruits-360 Only | 20 images | 50 images | MEDIUM |
| **Banana** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Orange** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Cucumber** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Eggplant** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Papaya** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Pineapple** | Multi-Domain | 15 images | 30 images | SUPPORTING |
| **Remaining 10 Foods**| Fruits-360 Only | 20 images/class | 50 images/class | STANDARD |

**Total Phase A Collection Target:** ~520 diverse real-world consumer photos across 24 classes.
