# FoodFresh AI — USDA FoodKeeper Shelf-Life Integration Report

**Date**: September 26, 2026  
**System Layer**: REFERENCE DATA & CANONICAL MAPPING ENGINE  
**Source Dataset**: USDA FoodKeeper (`data/raw/foodkeeper/FoodKeeper.json`, 661 products, 25 categories)  
**Implementation**: [`backend/app/services/shelf_life_service.py`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/backend/app/services/shelf_life_service.py)

---

## 1. System Taxonomy & Boundary Declaration

| Component Category | Classification | Technology / Foundation | Key Responsibility |
| :--- | :--- | :--- | :--- |
| **FoodKeeper Database** | **REFERENCE DATA** | USDA Food Safety and Inspection Service JSON | Authoritative empirical storage lifetimes across Pantry, Refrigerate, and Freezer. |
| **Canonical Mapper** | **RULE ENGINE** | Deterministic Alias & Disambiguation Dictionary | Maps detected produce terms to exact FoodKeeper product IDs; prevents false conflations. |
| **Shelf-Life Engine** | **RULE ENGINE** | Elapsed-Time Subtraction & Freshness Heuristic | Computes remaining quality windows; formats zero-day and negative-day explanations. |

---

## 2. Canonical Normalization & Disambiguation

Food items frequently have ambiguous common names (e.g. "Chili Pepper", "Green Chilli", "Bell Pepper", "Pepper"). The canonical layer applies strict product ID resolution:

| User / Detected Food Query | Resolved Canonical Food | FoodKeeper Product ID | Category | Match Type |
| :--- | :--- | :--- | :--- | :--- |
| `green chilli`, `chilli`, `hot pepper` | **Hot peppers** | `548.0` | Vegetables | `canonical_match` |
| `bell pepper`, `sweet pepper`, `capsicum` | **Peppers** | `296.0` | Vegetables | `canonical_match` |
| `tomato`, `vine tomato` | **Tomatoes** | `306.0` | Vegetables | `canonical_match` |
| `cherry tomato` | **Cherry tomatoes** | `600.0` | Vegetables | `canonical_match` |
| `potato`, `white potato` | **Potatoes** | `297.0` | Vegetables | `canonical_match` |
| `sweet potato`, `yam` | **Yams/sweet potatoes** | `422.0` | Vegetables | `canonical_match` |
| `apple` | **Apples** | `248.0` | Fruit | `canonical_match` |
| `banana` | **Bananas** | `251.0` | Fruit | `canonical_match` |
| `orange`, `lemon`, `lime` | **Citrus fruit** | `256.0` | Fruit | `canonical_match` |
| `pomegranate` | **Pomegranate** | `269.0` | Fruit | `canonical_match` |
| `cucumber` | **Cucumbers** | `283.0` | Vegetables | `canonical_match` |
| `eggplant`, `brinjal` | **Eggplant** | `284.0` | Vegetables | `canonical_match` |
| `bread`, `loaf` | **Commercial bread products** | `195.0` | Bakery | `canonical_match` |

### Ambiguity Safeguard
If a food query matches multiple conflicting FoodKeeper products without a justified canonical alias:
- The system returns `status = "unavailable"` with reason `"ambiguous FoodKeeper match"`.
- It **never fabricates or guesses** shelf-life numbers.

---

## 3. Storage Environment Mapping

The application UI supports two primary kitchen storage environments:
1. **Countertop** (Ambient room temperature, ~21°C) $\rightarrow$ Maps to FoodKeeper `Pantry` attributes (`Pantry_Min`, `Pantry_Max`, `Pantry_Metric`, `DOP_Pantry_*`).
2. **Crisper Chill** (Refrigerated produce drawer, ~4°C) $\rightarrow$ Maps to FoodKeeper `Refrigerate` attributes (`Refrigerate_Min`, `Refrigerate_Max`, `Refrigerate_Metric`, `DOP_Refrigerate_*`).

### Unsupported Storage Mode Handling
If a commodity does not support the selected storage environment according to USDA FoodKeeper:
- Example: Storing **Bell Peppers** on the Countertop returns:
  > *"USDA FoodKeeper does not specify a Countertop quality window for Peppers. Recommended storage is Crisper Chill (Refrigerated) (Fresh whole peppers will last longer if kept dry and refrigerated)."*
- Example: Storing whole **Tomatoes** in the Refrigerator returns:
  > *"FoodKeeper recommends countertop/pantry storage for whole tomatoes to preserve flavor and cellular texture."*

---

## 4. Shelf-Life Calculation & Freshness Signal Integration

### Mathematical Formulation
$$\text{Remaining Min Days} = \max\left(0, \text{Reference Min Days} - \text{Days Stored}\right)$$
$$\text{Remaining Max Days} = \max\left(0, \text{Reference Max Days} - \text{Days Stored}\right)$$

### Visible Freshness Heuristic Adjustment
1. **`Rotten`**: Remaining min/max clamped immediately to `0 days`.
2. **`Slightly Spoiled`**: Remaining min/max discounted by 50% to reflect accelerated decay.
3. **`Fresh`**: Full standard FoodKeeper reference window preserved.

---

## 5. Zero-Day and Negative-Day Explanations

When calculated remaining days reach `0` or become negative ($Days Stored \ge Reference Max$):
- Output: `"Estimated remaining quality: 0 days"`.
- Transparent explanation:
  - If rotten: *"Visible deterioration indicates that this item is past its consumable quality window."*
  - If expired by time: *"Stored for {days} days, exceeding the USDA FoodKeeper reference window of {min}–{max} days under {storage} storage."*
- Wording compliance: Uses **"Estimated remaining quality"**; never claims definitive food safety.
