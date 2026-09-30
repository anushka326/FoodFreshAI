# FoodFresh AI Food Recognition Training Report

## Dataset

Dataset:
Fruits-360

Training manifest:
D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_train_split.csv

Validation:
D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_val_split.csv (Stratified 10% split of training manifest, random_seed=42)

Test manifest:
D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_test_manifest.csv

## Classes

Number of classes:
12

Apple, Banana, Cucumber, Eggplant, Grape, Orange, Papaya, Peach, Pear, Pepper, Pineapple, Tomato

## Dataset Counts

Training images:
62,217

Validation images:
6,913

Test images:
22,996

## Model

EfficientNet-B0

Pretrained:
YES

Weight source:
Official TorchVision

Weight enum:
EfficientNet_B0_Weights.DEFAULT

## Training Strategy

Stage 1:
- Backbone feature extractor frozen (features.requires_grad = False)
- FoodFresh classification head trained (Linear(in_features=1280, out_features=12))
- Optimizer: AdamW (learning_rate=0.001, weight_decay=0.0001)
- Epochs: 3

Stage 2:
- Upper MBConv blocks unfrozen (features[6:])
- Fine-tuned with reduced learning rate
- Optimizer: AdamW (fine_tune_learning_rate=0.0001, weight_decay=0.0001)
- Epochs: 2

## Hyperparameters

Batch size: 128
Learning rate: 0.001
Fine-tuning learning rate: 0.0001
Weight decay: 0.0001
Epochs: 5 (3 Stage 1 + 2 Stage 2)
Random seed: 42
Optimizer: AdamW
Loss: CrossEntropyLoss (Class-Weighted balanced for class distribution)
Scheduler: ReduceLROnPlateau (factor=0.5, patience=1)

## Hardware

Device: cuda
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
CUDA: YES

## Training Results

Best validation accuracy:
99.99%

Best epoch:
Epoch 5

Final training accuracy:
99.75%

Final validation accuracy:
99.99%

## Checkpoint

models/trained/food_classifier.pth

Checkpoint created:
YES

## Basic Inference Verification

Test image: D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\raw\fruits-360-100x100-main\Test\Apple 10\r0_103_100.jpg
True class: Apple
Predicted class: Apple
Confidence: 100.00%

## Important Limitation

This model predicts food category from an image.

It does NOT determine:

- food safety
- freshness
- remaining shelf-life

Those are separate FoodFresh AI components.
