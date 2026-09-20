# FoodFresh AI Food Recognition Evaluation Report

## 1. Model

Model:
EfficientNet-B0

Checkpoint:
`models/trained/food_classifier.pth`

Pretrained initialization:
Official TorchVision EfficientNet-B0 (`EfficientNet_B0_Weights.DEFAULT`)

## 2. Test Dataset

Manifest:
`D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_test_manifest.csv` (Untouched test split, strictly unseen during training)

Number of classes:
12

Number of test images:
22,996

## 3. Hardware

Device:
cuda

GPU:
NVIDIA GeForce RTX 4050 Laptop GPU

## 4. Overall Metrics

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

## 5. Top-K Accuracy

Top-1:
99.5391%

Top-3:
100.0000%

Top-5:
100.0000%

## 6. Per-Class Metrics

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


Detailed metrics table saved in:
`reports/food_recognition_per_class_metrics.csv` and `reports/food_recognition_per_class_metrics.md`

## 7. Confusion Analysis

Most frequent observed class confusions:
- **Tomato → Pepper**: 40 test images
- **Cucumber → Peach**: 23 test images
- **Pear → Apple**: 23 test images
- **Eggplant → Cucumber**: 20 test images


Full confusion matrices saved in:
`reports/food_recognition_confusion_matrix.png` (Counts)
`reports/food_recognition_confusion_matrix_normalized.png` (Proportions)

## 8. Confidence Analysis

Correct prediction confidence:
- Mean: 0.9980
- Median: 1.0000
- Min: 0.5014
- Max: 1.0000

Incorrect prediction confidence:
- Mean: 0.8249
- Median: 0.8864
- Min: 0.4601
- Max: 0.9996

Median confidence (overall):
1.0000

Visualization saved in:
`reports/food_recognition_confidence_distribution.png`

> **Notice:** Model confidence reflects softmax output probability across food categories and does NOT represent food safety, quality, or shelf-life certainty.

## 9. Model Size

Parameters:
4,022,920 total parameters (4,022,920 trainable parameters)

Checkpoint size:
39.89 MB

## 10. Error Analysis

Number of incorrect predictions:
106 (0.46%)

Number of correct predictions:
22,890 (99.54%)

Observable patterns in misclassifications:
- Most misclassifications occur among visually similar botanical varieties sharing analogous skin textures, colors, or spherical profiles (such as Eggplant varieties with lighter coloration, or specific pepper and peach angles).
- For incorrect classifications, the average model confidence (82.49%) is noticeably lower than for correct classifications (99.80%), indicating appropriate uncertainty calibration.

Visual examples saved in:
`reports/food_recognition_misclassified_examples.png`
Complete log of all misclassifications saved in:
`reports/food_recognition_misclassifications.csv`

## 11. Important Limitation

This evaluation measures image classification performance on the Fruits-360 test set.

It does NOT prove:

- food safety
- freshness detection
- shelf-life prediction
- performance on arbitrary real-world kitchen images

Real-world performance must be tested separately.

---

## 12. Out-of-Dataset Qualitative Inference

The following qualitative test was conducted on external food images outside Fruits-360 (from AgriFreshNET) to observe behavior under non-studio environmental conditions:


Image: `aug_0_IMG-20251127-WA0019.jpg`
Expected category: Apple
Prediction: Cucumber
Confidence: 92.38%
Top 3 predictions: Cucumber (92.4%), Banana (4.2%), Eggplant (2.2%)

Image: `aug_0_IMG_20251104_131910090_HDR_AE~2.jpg`
Expected category: Banana
Prediction: Banana
Confidence: 96.16%
Top 3 predictions: Banana (96.2%), Cucumber (3.8%), Pepper (0.1%)

Image: `aug_0_IMG_20251025_121754.jpg`
Expected category: Cucumber
Prediction: Cucumber
Confidence: 100.00%
Top 3 predictions: Cucumber (100.0%), Papaya (0.0%), Pear (0.0%)

Image: `IMG_20251102_075331551_HDR_AE.jpg`
Expected category: Tomato
Prediction: Cucumber
Confidence: 84.31%
Top 3 predictions: Cucumber (84.3%), Tomato (12.3%), Apple (2.4%)


> **Notice:** These qualitative results illustrate domain-shift effects when moving from studio-isolated white backgrounds to real-world environments. They are NOT incorporated into the formal test metrics above.
