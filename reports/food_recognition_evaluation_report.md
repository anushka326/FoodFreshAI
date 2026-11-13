# FoodFresh AI Food Recognition Evaluation Report

## 1. Model

Model:
EfficientNet-B0

Checkpoint:
models/trained/food_classifier.pth

Pretrained initialization:
Official TorchVision EfficientNet-B0

## 2. Test Dataset

Manifest:
D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_test_manifest.csv

Number of classes:
12

Number of test images:
22,996

## 3. Test Integrity

Training overlap:
NO

Validation overlap:
NO

Duplicate paths:
NO

Missing images:
0

## 4. Hardware

Device:
cuda

GPU:
NVIDIA GeForce RTX 4050 Laptop GPU

## 5. Overall Metrics

Accuracy:
99.5391%

Macro Precision:
0.9961

Macro Recall:
0.9906

Macro F1:
0.9932

Weighted Precision:
0.9954

Weighted Recall:
0.9954

Weighted F1:
0.9954

## 6. Top-K Accuracy

Top-1:
99.5391%

Top-3:
100.0000%

Top-5:
100.0000%

## 7. Per-Class Metrics

- **Apple**: Precision=0.9958, Recall=1.0000, F1=0.9979, Support=5506
- **Banana**: Precision=1.0000, Recall=1.0000, F1=1.0000, Support=645
- **Cucumber**: Precision=0.9903, Recall=0.9889, F1=0.9896, Support=2065
- **Eggplant**: Precision=1.0000, Recall=0.9153, F1=0.9558, Support=236
- **Grape**: Precision=1.0000, Recall=1.0000, F1=1.0000, Support=1538
- **Orange**: Precision=1.0000, Recall=1.0000, F1=1.0000, Support=1102
- **Papaya**: Precision=1.0000, Recall=1.0000, F1=1.0000, Support=404
- **Peach**: Precision=0.9858, Recall=1.0000, F1=0.9929, Support=1597
- **Pear**: Precision=1.0000, Recall=0.9944, F1=0.9972, Support=4087
- **Pepper**: Precision=0.9811, Recall=1.0000, F1=0.9904, Support=2074
- **Pineapple**: Precision=1.0000, Recall=1.0000, F1=1.0000, Support=329
- **Tomato**: Precision=1.0000, Recall=0.9883, F1=0.9941, Support=3413

Detailed per-class metric tables are saved in:
- `reports/food_recognition_per_class_metrics.csv`
- `reports/food_recognition_per_class_metrics.md`

## 8. Confusion Analysis

Most frequent observed confusion pairs:
- Tomato → Pepper: 40 test images
- Cucumber → Peach: 23 test images
- Pear → Apple: 23 test images
- Eggplant → Cucumber: 20 test images

Full confusion matrices:
- `reports/food_recognition_confusion_matrix.png` (Counts)
- `reports/food_recognition_confusion_matrix_normalized.png` (Normalized)

## 9. Confidence Analysis

Average confidence:
0.9972

Correct prediction confidence:
0.9980

Incorrect prediction confidence:
0.8249

Median confidence:
1.0000

Confidence distribution plot:
- `reports/food_recognition_confidence_distribution.png`

## 10. Error Analysis

Correct predictions:
22,890

Incorrect predictions:
106

Misclassification count:
106

Observable patterns:
- Misclassifications predominantly occur between visually similar botanical cultivars that share color, spherical form factor, and smooth skin texture (e.g. specific Pepper and Peach cross-angles, or lighter-toned Eggplants).
- The model exhibits well-calibrated confidence: average confidence for incorrect predictions (0.8249) is substantially lower than for correct predictions (0.9980).
- Complete misclassifications table saved in `reports/food_recognition_misclassifications.csv`
- Visual misclassification examples saved in `reports/food_recognition_misclassified_examples.png`

## 11. Out-of-Dataset Qualitative Testing

Images tested:
7

Results:
Image: `aug_0_IMG_20251104_131910090_HDR_AE~2.jpg`
Expected food: Banana
Predicted food: Banana
Match: YES
Confidence: 96.16%
Top 3:
- 1. Banana — 96.16%
- 2. Cucumber — 3.77%
- 3. Pepper — 0.07%

Image: `aug_0_IMG_20251025_121754.jpg`
Expected food: Cucumber
Predicted food: Cucumber
Match: YES
Confidence: 100.00%
Top 3:
- 1. Cucumber — 100.00%
- 2. Papaya — 0.00%
- 3. Pear — 0.00%

Image: `aug_0_IMG_20251107_113920647_HDR_AE.jpg`
Expected food: Orange
Predicted food: Cucumber
Match: NO
Confidence: 97.59%
Top 3:
- 1. Cucumber — 97.59%
- 2. Pear — 1.82%
- 3. Papaya — 0.53%

Image: `IMG_20251102_075331551_HDR_AE.jpg`
Expected food: Tomato
Predicted food: Cucumber
Match: NO
Confidence: 84.31%
Top 3:
- 1. Cucumber — 84.31%
- 2. Tomato — 12.30%
- 3. Apple — 2.36%

Image: `aug_0_IMG_20251118_164757182_HDR.jpg`
Expected food: Eggplant
Predicted food: Apple
Match: NO
Confidence: 99.41%
Top 3:
- 1. Apple — 99.41%
- 2. Tomato — 0.45%
- 3. Papaya — 0.05%

Image: `aug_0_IMG-20251127-WA0019.jpg`
Expected food: Pineapple
Predicted food: Cucumber
Match: NO
Confidence: 92.38%
Top 3:
- 1. Cucumber — 92.38%
- 2. Banana — 4.18%
- 3. Eggplant — 2.20%

Image: `aug_0_IMG_20251025_122121.jpg`
Expected food: Papaya
Predicted food: Cucumber
Match: NO
Confidence: 83.00%
Top 3:
- 1. Cucumber — 83.00%
- 2. Pear — 16.66%
- 3. Peach — 0.20%


> **Notice:** These out-of-dataset qualitative results illustrate domain-shift effects when moving from isolated white-background conditions to real-world environments. They are NOT incorporated into the official test metrics.

## 12. Model Size

Total parameters:
4,022,920

Trainable parameters:
4,022,920

Checkpoint size:
39.89 MB

## 13. Limitations

This model predicts food category from an image under Fruits-360 test conditions.
High test accuracy on Fruits-360 does NOT guarantee identical performance on real-world phone photos, complex kitchen lighting, partial occlusions, or cluttered backgrounds.
Furthermore, this model does NOT determine:
- food safety
- freshness
- remaining shelf-life

Those are separate FoodFresh AI components.
