# Freshness V3 held-out evaluation and production comparison

- Test rows: 2173 (same AgriFreshNET held-out split for both models)
- V3 checkpoint: `D:\VIT TY SEM5\ML Project\FOODFRESHAI\models\candidates\freshness_v3_efficientnet_b0.pth`
- Production checkpoint: `models/trained/freshness_model_v2.pth`

| Model | Accuracy | Macro F1 | Balanced accuracy | Macro precision | Macro recall | ECE raw | NLL raw | Temperature (validation) | ECE scaled | NLL scaled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V3 EfficientNet-B0 | 0.8260 | 0.8212 | 0.8250 | 0.8237 | 0.8250 | 0.0461 | 0.3695 | 1.4198 | 0.0400 | 0.3717 |
| Production V2 ResNet-18 | 0.9604 | 0.9605 | 0.9604 | 0.9608 | 0.9604 | 0.0231 | 0.1523 | 1.1118 | 0.0196 | 0.1426 |

## V3 per-class test metrics

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Fresh | 0.8234 | 0.8359 | 0.8296 | 725 |
| Semi-Fresh | 0.8023 | 0.6746 | 0.7329 | 716 |
| Rotten | 0.8455 | 0.9645 | 0.9011 | 732 |

## Confusion matrices (rows actual, columns predicted; Fresh, Semi-Fresh, Rotten)

V3:
```text
[[606, 98, 21], [125, 483, 108], [5, 21, 706]]
```

Production V2:
```text
[[708, 17, 0], [18, 685, 13], [0, 38, 694]]
```

Temperature was fitted on validation logits only; all displayed metrics use the untouched test split. Reliability diagram: `freshness_reliability_diagram.png`.
V3 is not promoted by this script.

## Reconciliation and promotion decision

The completion report emitted by the trainer (`freshness_v3_training_report.md`) claims V3 test accuracy 0.9365, balanced accuracy 0.9361, and macro F1 0.9357. That result could not be reproduced. I reran the test set using the trainer's own `create_model`, `AgriFreshDataset`, `EVAL_TRANSFORM`, and `evaluate_model` functions against the saved candidate checkpoint; the repeated result was accuracy 0.8260, balanced accuracy 0.8250, and macro F1 0.8212. The independent evaluator, with the same split and EXIF-correct image decoding, also returned 0.8260. The discrepancy remains unexplained; treat the independently reproduced checkpoint metrics as the verified result and the trainer report as inconsistent.

On the same untouched test split, production V2 reached 0.9604 accuracy, 0.9605 macro F1, and 0.9604 balanced accuracy. V3 is therefore **not promoted**. The raw V2 ECE was 0.0231 and test NLL 0.1523; temperature 1.1118 fitted on validation reduced ECE to 0.0196 and NLL to 0.1426 without changing labels. This temperature is now integrated for the active V2 production checkpoint. For V3, temperature 1.4198 reduced ECE 0.0461 to 0.0400 but increased NLL 0.3695 to 0.3717; V3 remains uncalibrated and inactive.
