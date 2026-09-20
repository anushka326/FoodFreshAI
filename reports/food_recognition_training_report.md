# FoodFresh AI Food Recognition Training Report

## Dataset

Dataset:
Fruits-360

Training manifest:
`D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_train_split.csv`

Validation:
`D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_val_split.csv` (Stratified 10% split of training manifest, random_seed=42)

Test manifest:
`D:\VIT TY SEM5\ML Project\FOODFRESHAI\data\processed\fruits360\fruits360_test_manifest.csv` (Untouched test set)

## Classes

Number of classes:
12

Classes:
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
Official TorchVision (`torchvision.models.efficientnet_b0`)

Weight enum:
EfficientNet_B0_Weights.DEFAULT

## Training Strategy

Stage 1:
- Backbone frozen (`features.requires_grad = False`)
- Classifier head trained (`classifier[1] = Linear(1280, 12)`)
- Epochs: 3
- Learning rate: 0.001
- Optimizer: AdamW (weight_decay=0.0001)

Stage 2:
- Upper MBConv blocks unfrozen (`features[6:]`)
- Fine-tuned with reduced learning rate
- Epochs: 2
- Fine-tuning learning rate: 0.0001
- Optimizer: AdamW (weight_decay=0.0001)

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
CPU: Available
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

## Test Results

Test accuracy:
99.54%

Macro precision:
0.9961

Macro recall:
0.9906

Macro F1:
0.9932

Weighted F1:
0.9954

## Checkpoint

`models/trained/food_classifier.pth`

Checkpoint created:
YES

## Important Limitation

This model predicts the food category from an image.

It does NOT determine:

- food safety
- freshness
- remaining shelf-life

Those are separate FoodFresh AI components.
