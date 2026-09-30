# Real-World Food Recognition Dataset (V3 Domain Adaptation)

## Purpose
This directory structure is dedicated to collecting and organizing authentic real-world consumer photographs for **Food Recognition V3 domain adaptation**.

Fruits-360 was captured in laboratory rotary conditions against pure white `#FFFFFF` backdrops. While effective for initial feature learning, standard consumer photos (countertops, kitchen ambient light, refrigerator shelves, wooden boards, grocery bags) suffer from domain shift. This directory hosts real consumer images to bridge that domain gap.

---

## Directory Structure
Place images into their respective category folders:

```text
data/real_world_food/
├── Apple/
├── Avocado/
├── Banana/
├── Cherry/
├── Corn/
├── Cucumber/
├── Eggplant/
├── Grape/
├── Guava/
├── Lemon/
├── Mango/
├── Onion/
├── Orange/
├── Papaya/
├── Peach/
├── Pear/
├── Pepper/
├── Pineapple/
├── Plum/
├── Pomegranate/
├── Potato/
├── Strawberry/
├── Tomato/
└── Watermelon/
```

---

## Data Collection Guidelines
1. **Authentic Smartphone Cameras:**
   - Capture images directly using mobile phone cameras (rear camera, standard focal length, no beauty/manipulation filters).
2. **Environmental & Background Diversity:**
   - Varied kitchen surfaces: granite countertops, wooden cutting boards, stainless steel sinks, refrigerator crisper drawers, dining tables, plates/bowls, and grocery bags.
   - Varied lighting: morning daylight, warm evening indoor lights, direct fluorescent kitchen lights, ambient shadow casting.
   - Avoid collecting only centered studio-style images, pure white backgrounds, or sterile disc shots.
3. **Viewpoint, Distance & Scale Variety:**
   - Top-down (flat-lay), 45-degree user perspective, eye-level side views.
   - Vary the distance: macro texture, medium produce shot, produce sitting on counter or table.
   - Vary the scale: multiple sizes, different orientations, and partially occluded produce (e.g. half inside a bowl or grocery bag).
4. **Produce Diversity:**
   - Different varieties, sizes, shapes, and ripeness colors (e.g. green vs red apples, ripe yellow vs speckled bananas).
   - Single-food dominance: Ensure the target food is the prominent subject in the frame.
5. **Quality over Quantity (Do NOT Burst-Spam):**
   - **Do NOT** take 50 near-identical burst shots of the exact same fruit from the same angle. High correlation provides zero semantic diversity and leads to over-optimistic evaluation metrics.
   - Capture 2–4 distinct angles per physical fruit specimen under differing lighting or surfaces.

---

## ⚠️ Critical Leakage Prevention Rule (Group-Based Splitting)
When partitioning real-world images into Train, Validation, and Test sets:

> **All images of the SAME physical object specimen or photography session MUST remain strictly within the SAME split.**

- **Violation Example:** Specimen A photographed 5 times; 4 photos placed in `train` and 1 in `test`.
  - *Result:* Severe evaluation data leakage. The model merely memorizes the specific bruise/marking/lighting of Specimen A rather than learning generalizable food semantics.
- **Enforced Standard:** All photos from `Specimen_Apple_01` go exclusively to `train` OR `val` OR `test`.

---

## Target Collection Priorities (Based on Step 16 Inventory)

| Priority Tier | Food Classes | Current Real-World Coverage | Target Collection Range | Rationale |
| :--- | :--- | :---: | :---: | :--- |
| **Tier 1 (Critical)** | **Pomegranate, Apple, Tomato** | 0 real-world images | **50–100 images** (15–25 specimens) | Exposed severe misclassification in V2 production testing. High priority to establish real-world invariant filters. |
| **Tier 2 (High)** | **Mango, Onion, Potato, Avocado, Lemon** | 0 real-world images | **40–80 images** (10–20 specimens) | Common household produce with zero AgriFreshNET coverage. Prone to white-backdrop collapse. |
| **Tier 3 (Standard Single-Domain)** | **Cherry, Corn, Grape, Guava, Peach, Pear, Pepper, Plum, Strawberry, Watermelon** | 0 real-world images | **30–60 images** (8–15 specimens) | Lacks real-world domestic backgrounds. Needs varied countertops and ambient light. |
| **Tier 4 (Supporting Multi-Domain)** | **Banana, Cucumber, Eggplant, Orange, Papaya, Pineapple** | 1,770 images in AgriFreshNET | **15–30 images** (5–10 specimens) | Already strongly anchored by AgriFreshNET smartphone captures; consumer photos provide supplemental validation. |

