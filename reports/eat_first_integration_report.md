# FoodFresh AI — Eat First Priority Engine Integration Report

**Date**: September 26, 2026  
**System Layer**: RULE ENGINE (Deterministic Consumption Prioritization)  
**Implementation**: [`backend/app/services/eat_first_service.py`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/backend/app/services/eat_first_service.py)

---

## 1. System Taxonomy & Boundary Declaration

| Component Category | Classification | Technology / Foundation | Key Responsibility |
| :--- | :--- | :--- | :--- |
| **Eat First Engine** | **RULE ENGINE** | Deterministic Decision Hierarchy | Translates shelf-life bounds and visible freshness condition into actionable kitchen urgency tiers. |

> **Architectural Clarity**: Eat First is strictly a **deterministic rule engine**, NOT a black-box machine learning model. It uses explainable thresholds grounded in food science principles rather than statistical probabilities.

---

## 2. Decision Inputs & Hierarchy

The engine evaluates 5 structured inputs:
1. `remaining.minDays` (Calculated remaining shelf-life lower bound)
2. `remaining.maxDays` (Calculated remaining shelf-life upper bound)
3. `freshness_label` (Estimated visible surface freshness: Fresh, Slightly Spoiled, Rotten, or Uncertain)
4. `days_stored` (User pantry elapsed duration)
5. `storage_type` (Countertop vs Crisper Chill)

### Priority Tiers and Trigger Conditions

| Priority Tier | Numeric Rank | Primary Trigger Conditions | Default Urgency Label | Transparent Reason Template |
| :--- | :--- | :--- | :--- | :--- |
| **`VERY_HIGH`** | `4` | $RemainingMax \le 0$ OR $Freshness = Rotten$ OR $RemainingMax \le 1$ | Consume immediately or discard | *"Very high priority because the estimated remaining quality is 0 days."* OR *"Very high priority because visible surface degradation indicates the quality window has expired."* |
| **`HIGH`** | `3` | $Freshness = Slightly Spoiled$ OR $RemainingMax \le 3$ | Consume within 1–3 days | *"High priority because the estimated remaining quality window is short ({min}–{max} days) and visible freshness is declining."* |
| **`MEDIUM`** | `2` | $RemainingMax \le 7$ days | Consume within a week | *"Estimated remaining quality is moderate ({min}–{max} days) under proper storage."* |
| **`LOW`** | `1` | $RemainingMax > 7$ days with Fresh appearance | Ample quality window remaining | *"Good visible freshness with ample estimated shelf-life ({min}–{max} days)."* |
| **`UNAVAILABLE`** | `0` | Shelf-Life status is unavailable | Guidance unavailable | *"Eat First requires an available shelf-life estimate."* |

---

## 3. Strict Safety Safeguards & Boundary Rules

1. **No Fake Scores**: The engine never assigns arbitrary numerical floating-point percentages to Eat First. It uses strict discrete tiers (`VERY_HIGH`, `HIGH`, `MEDIUM`, `LOW`, `UNAVAILABLE`).
2. **Missing Reference Guard**: If a food item cannot be matched to USDA FoodKeeper or if the storage mode is unsupported, Eat First returns `status = "unavailable"` with reason:
   > *"Eat First requires an available shelf-life estimate."*
   It **never fabricates** an artificial priority when underlying shelf-life data is missing.
3. **Multi-Food Sorting**: In compare mode, items are sorted deterministically descending by `score` (4 down to 1), with ties broken by ascending `remaining.maxDays` (items spoiling sooner appear higher).
