# FoodFresh AI — Freshness Classification Pipeline

## Overview
This module implements the **Freshness Classification Pipeline** for FoodFresh AI, powered by the AgriFreshNET dataset and TorchVision EfficientNet-B0.

The model classifies produce images into 3 canonical freshness stages:
- **`0: Fresh`**
- **`1: Semi-Fresh`**
- **`2: Rotten`**

---

## Directory Structure
```
ml/freshness/
├── __init__.py       # Package exports
├── config.py         # FreshnessConfig dataclass
├── dataset.py        # FreshnessDataset & create_freshness_data_loaders
├── transforms.py     # Freshness-preserving EfficientNet-B0 transforms
├── model.py          # EfficientNet-B0 3-class model factory
├── train.py          # Two-stage transfer learning training script
├── evaluate.py       # Test set evaluation and metric generation
├── predict.py        # Single image inference predictor
├── utils.py          # Helper utilities and checkpoint management
└── README.md         # Documentation
```

---

## Dataset & Manifests
- **Raw Dataset:** AgriFreshNET (14,160 total images across 8 food types)
- **Processed Directory:** `data/processed/agrifreshnet/`
  - `freshness_label_map.json`: Canonical 3-class label mapping.
  - `freshness_config.json`: Metadata, split counts, and food types.
  - `freshness_train_manifest.csv`: 9,856 images (~69.60%).
  - `freshness_val_manifest.csv`: 2,131 images (~15.05%).
  - `freshness_test_manifest.csv`: 2,173 images (~15.35%).
- **Leak-Free Partitioning:** All augmentations of a physical photo (`base_stem`) reside strictly within one split. 0 base stem overlap.

---

## Model Architecture
- **Backbone:** TorchVision Official `efficientnet_b0` (`weights=EfficientNet_B0_Weights.DEFAULT`)
- **Classifier Head:** `Dropout(p=0.2)` -> `Linear(in_features=1280, out_features=3)`
- **Input Size:** `(3, 224, 224)`
- **Normalization:** ImageNet mean (`[0.485, 0.456, 0.406]`) and standard deviation (`[0.229, 0.224, 0.225]`).

---

## Pipeline Usage

### 1. DataLoaders
```python
from ml.freshness import FreshnessConfig, create_freshness_data_loaders

config = FreshnessConfig()
train_loader, val_loader, test_loader = create_freshness_data_loaders(config)
```

### 2. Model Factory
```python
from ml.freshness import create_freshness_model

model = create_freshness_model(num_classes=3, pretrained=True)
```

### 3. Training (Future Step)
```powershell
python -m ml.freshness.train --run
```
