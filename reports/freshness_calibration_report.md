# FoodFresh AI — Freshness Model Confidence Calibration Report

**Date**: September 26, 2026  
**Subject**: Confidence-Aware Decision Logic and Uncertainty Thresholding  
**Reference Report**: [`reports/freshness_v1_vs_v2_report.md`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/freshness_v1_vs_v2_report.md)  

---

## 1. Motivation & Problem Statement

Raw softmax probabilities from neural networks suffer from systemic overconfidence when evaluated out-of-distribution or on ambiguous visual inputs. In the previous baseline:
- An image of bread was predicted "Rotten" with **97.7%** confidence.
- A fresh green chilli was predicted "Slightly Spoiled" with **58.3%** confidence.
- A tomato with visible rot was predicted "Fresh" with **57.0%** confidence.

Directly exposing the `argmax` softmax value as ground truth misleads consumers and undermines trust.

---

## 2. Confidence Calibration & Uncertainty Policy

FoodFresh AI introduces a **two-dimensional uncertainty gate** combining:
1. **Top-1 Confidence Threshold**: Minimum absolute probability required to assert a class.
2. **Top-1 / Top-2 Probability Margin**: Margin of separation $\Delta = P_1 - P_2$ ensuring the decision is decisive and not a near-tie.

### Empirical Threshold Tiers

| Tier | Condition | System Status | User-Facing Display | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| **High Confidence** | $P_1 \ge 65.0\%$ and $\Delta \ge 20.0\%$ | `success` | `Fresh`, `Slightly Spoiled`, `Rotten` | Clear, decisive surface evidence matching trained distributions. |
| **Moderate Confidence** | $50.0\% \le P_1 < 65.0\%$ and $\Delta \ge 10.0\%$ | `success` | `[Label] (Moderate Confidence)` | Moderate visual evidence; user encouraged to perform sensory check. |
| **Uncertain** | $P_1 < 50.0\%$ or $\Delta < 10.0\%$ | `uncertain` | `Freshness Uncertain` | Ambiguous visual evidence, poor lighting, or occluded surface. |

---

## 3. Real-World Calibration Behavior

Under this calibrated policy:
- Visibly clear items with distinct features (e.g. clearly fresh potato, moldy orange) receive **High Confidence** ratings with no unnecessary friction.
- Borderline or ambiguous cases are marked as **Freshness Uncertain — sensory inspection recommended**, preventing false claims.
- The user interface displays explicit explanatory text:
  > *"Estimated visible freshness is based on surface appearance and is not a laboratory food-safety test. Always check aroma and texture before consuming."*
