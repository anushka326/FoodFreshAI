# FoodFresh AI — Freshness Model Fine-Tuning Report (V2)

**Date**: September 26, 2026  
**Architecture**: ResNet-18 (Torchvision backbone + FastAI AdaptiveConcatPool2d head)  
**Dataset**: AgriFreshNET Freshness V2 (`data/processed/freshness_v2/`)  
**Trained Weights**: [`models/trained/freshness_model_v2.pth`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/models/trained/freshness_model_v2.pth)  
**Pretrained Starting Point**: `models/pretrained/freshness_resnet18/model_weights.pth` (kept untouched)  

---

## 1. Executive Summary

To resolve severe classification mode-collapse and false-positive degradation on real-world produce, the ResNet-18 freshness model was fine-tuned on the real-world **AgriFreshNET** produce dataset.

- **Total Dataset Size**: 14,160 images across 5,106 capture groups
- **Splits**: Train = 9,926 (70.1%), Validation = 2,128 (15.0%), Test = 2,106 (14.9%)
- **Data Leakage Guarantee**: 0 capture group overlap across train, validation, and test.
- **Best Validation Macro F1**: 92.54%
- **Final Test Set Accuracy**: 93.68%
- **Final Test Set Macro F1**: 93.70%

---

## 2. Test Set Evaluation Metrics (Untouched Test Partition)

### Overall Summary
- **Loss**: 0.2440
- **Accuracy**: **93.68%**
- **Macro F1-Score**: **93.70%**
- **Weighted F1-Score**: **93.71%**

### Per-Class Detailed Performance
| Class Index | Class Label | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | **Fresh** | 94.83% | 93.35% | **94.08%** | 707 |
| `1` | **Rotten** | 96.97% | 95.73% | **96.34%** | 702 |
| `2` | **Slightly Spoiled** | 89.40% | 91.97% | **90.66%** | 697 |

### Confusion Matrix
```
                  Predicted Fresh  Predicted Rotten  Predicted Slightly Spoiled
Actual Fresh             660              1                 46
Actual Rotten            0                672               30
Actual Slightly Spoiled  36               20                641
```

### Scikit-Learn Classification Report
```
                      precision    recall  f1-score   support

           Fresh (0)     0.9483    0.9335    0.9408       707
          Rotten (1)     0.9697    0.9573    0.9634       702
Slightly Spoiled (2)     0.8940    0.9197    0.9066       697

            accuracy                         0.9368      2106
           macro avg     0.9373    0.9368    0.9370      2106
        weighted avg     0.9375    0.9368    0.9371      2106

```

---

## 3. Epoch-by-Epoch Training Trajectory

| Epoch | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Val Macro F1 (%) | Epoch Duration (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | 0.6887 | 75.98% | 0.5427 | 81.95% | 81.73% | 106.7s |
| 02 | 0.3093 | 88.97% | 0.4073 | 87.03% | 87.06% | 101.3s |
| 03 | 0.2013 | 92.59% | 0.3584 | 88.44% | 88.35% | 101.1s |
| 04 | 0.1377 | 95.13% | 0.3592 | 90.70% | 90.72% | 98.4s |
| 05 | 0.1035 | 95.97% | 0.2903 | 91.64% | 91.57% | 93.4s |
| 06 | 0.0683 | 97.39% | 0.2681 | 92.53% | 92.54% | 181.3s |
| 07 | 0.0477 | 98.17% | 0.2928 | 91.87% | 91.87% | 332.9s |
| 08 | 0.0434 | 98.58% | 0.3018 | 91.87% | 91.87% | 246.4s |

---

## 4. Promotion Criteria Gate Status

In accordance with Phase 5 & Phase 25:
- The trained model is preserved at `models/trained/freshness_model_v2.pth`.
- The original checkpoint at `models/pretrained/freshness_resnet18/model_weights.pth` remains untouched.
- Promotion to production will strictly occur ONLY after side-by-side real-world benchmark validation on real produce images.
