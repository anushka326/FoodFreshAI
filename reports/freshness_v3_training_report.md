# Freshness Model V3 Training Report

**Model:** EfficientNet-B0
**Dataset:** AgriFreshNET (Fresh, Semi-Fresh, Rotten)
**Train/Val/Test Split:** 9856/2131/2173
**Training Date:** 2026-09-30T13:39:27.294544
**Device:** cuda
**Classes:** Fresh, Semi-Fresh, Rotten

## Final Metrics

### Test Set (Held-out)
- **Accuracy:** 0.9365
- **Balanced Accuracy:** 0.9361
- **Macro F1:** 0.9357
- **Weighted F1:** 0.9360
- **Loss:** 0.3953

### Per-Class Metrics (Test Set)
| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Fresh | 0.9223 | 0.9655 | 0.9434 | 725 |
| Semi-Fresh | 0.9313 | 0.8715 | 0.9004 | 716 |
| Rotten | 0.9556 | 0.9713 | 0.9634 | 732 |

### Confusion Matrix (Test Set)
Rows: True labels, Columns: Predicted labels

| Actual \ Predicted | Fresh | Semi-Fresh | Rotten |
|-------------------|---------------------------------------|
| Fresh | 700 | 25 | 0 |
| Semi-Fresh | 59 | 624 | 33 |
| Rotten | 0 | 21 | 711 |

## Dataset Information
- **Foods in Dataset:** Banana, Bittermelon, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato
- **Classes:** Fresh (33.3%), Semi-Fresh (33.3%), Rotten (33.3%)
- **Note:** Training data does NOT include green chilli or dried chilli
  - Green chilli failures on this model would be due to unseen domain
  - Dried chilli is a different form and needs form-aware handling

## Comparison with Production Model (to be performed)
- Current production: nathansekar/food-freshness-detector fallback
- This candidate: EfficientNet-B0 on AgriFreshNET
- Decision: Evaluate on protected regression cases before promotion
