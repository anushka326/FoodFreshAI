# FoodFresh AI — Food Recognition Pipeline

## Overview
The Food Recognition module provides multi-class produce categorization using an EfficientNet-B0 backbone adapted for kitchen and supermarket produce recognition.

## Data Source
- **Primary Source:** Fruits-360 (100x100 resolution) dataset.
- **Manifests:** Generated in STEP 4 under `data/processed/fruits360/`:
  - `fruits360_train_manifest.csv` (69,130 training images)
  - `fruits360_test_manifest.csv` (22,996 test images)
  - `label_map.json` (12-class bidirectional lookup)
  - `original_to_food.json` (263 original variety classes mapped to broad foods)

## Normalized Food Classes (12 Classes)
1. `Apple` (ID: 0)
2. `Banana` (ID: 1) — *AgriFreshNET Overlap*
3. `Cucumber` (ID: 2) — *AgriFreshNET Overlap*
4. `Eggplant` (ID: 3) — *AgriFreshNET Overlap*
5. `Grape` (ID: 4)
6. `Orange` (ID: 5) — *AgriFreshNET Overlap*
7. `Papaya` (ID: 6) — *AgriFreshNET Overlap*
8. `Peach` (ID: 7)
9. `Pear` (ID: 8)
10. `Pepper` (ID: 9)
11. `Pineapple` (ID: 10) — *AgriFreshNET Overlap*
12. `Tomato` (ID: 11) — *AgriFreshNET Overlap*

## Important Model Notice
> [!IMPORTANT]
> Pretrained weights are intentionally not downloaded in STEP 5.
> The architecture factory constructs EfficientNet-B0 with `pretrained=False` (weights=None) during this preparation phase. Pretrained weights download and training execution will occur in authorized subsequent steps.

## Module Structure
- `config.py`: Centralized configuration, hyperparameter specifications, and path resolution.
- `dataset.py`: PyTorch `FoodRecognitionDataset` and DataLoader factory reading manifest CSVs.
- `transforms.py`: Data augmentation (RandomHorizontalFlip, ColorJitter, RandomRotation) and standard 224x224 ImageNet normalization.
- `model.py`: EfficientNet-B0 architecture factory with customized linear classifier head.
- `train.py`: Guarded training loop with AdamW optimizer and CosineAnnealingLR scheduler.
- `evaluate.py`: Evaluation suite computing accuracy, macro precision, recall, F1, and confusion matrix.
- `predict.py`: Inference utility for single-image classification prepared for FastAPI backend integration.
- `utils.py`: Seed management, hardware device detection, and parameter counting.

## Future Execution Commands

### 1. Training (Authorized Future Step)
```powershell
python -m ml.food_recognition.train --execute-training
```

### 2. Evaluation
```powershell
python -m ml.food_recognition.evaluate
```

### 3. Inference
```powershell
python -m ml.food_recognition.predict --image <path_to_image>
```
