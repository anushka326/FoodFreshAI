# EfficientNet-B0 Initialization Report

## Model
EfficientNet-B0

## Weight Source
Official TorchVision (`torchvision.models.efficientnet_b0`)

## Weight Enum
EfficientNet_B0_Weights.DEFAULT (resolves to `EfficientNet_B0_Weights.IMAGENET1K_V1`)

## Pretrained Weights
Loaded: YES  
- Source URL: `https://download.pytorch.org/models/efficientnet_b0_rwightman-7f5810bc.pth`  
- Cache Path: `C:\Users\DELL\.cache\torch\hub\checkpoints\efficientnet_b0_rwightman-7f5810bc.pth`  
- Cache File Size: 20.45 MB  

## Number of FoodFresh Classes
12  
- Classes: Apple, Banana, Cucumber, Eggplant, Grape, Orange, Papaya, Peach, Pear, Pepper, Pineapple, Tomato  
- Source: `data/processed/fruits360/label_map.json`  

## Original Classifier
```
Sequential(
  (0): Dropout(p=0.2, inplace=True)
  (1): Linear(in_features=1280, out_features=1000, bias=True)
)
```
- Input Features: 1280
- Output Features: 1000 (ImageNet-1k)

## FoodFresh Classifier
```
Sequential(
  (0): Dropout(p=0.2, inplace=True)
  (1): Linear(in_features=1280, out_features=12, bias=True)
)
```
- Input Features: 1280
- Output Features: 12 (FoodFresh AI Food Categories)

## Total Parameters
4,022,920

## Trainable Parameters
4,022,920

## Device
CUDA

## GPU
NVIDIA GeForce RTX 4050 Laptop GPU

## Forward Pass
PASS

## Output Shape
[1, 12]

## Preprocessing Transforms
Official TorchVision transforms associated with `EfficientNet_B0_Weights.DEFAULT`:
```
ImageClassification(
    crop_size=[224]
    resize_size=[256]
    mean=[0.485, 0.456, 0.406]
    std=[0.229, 0.224, 0.225]
    interpolation=InterpolationMode.BICUBIC
)
```

## Training
NOT PERFORMED

## FoodFresh Checkpoint
NOT CREATED (No `.pth` saved in `models/trained/`)
