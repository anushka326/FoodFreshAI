"""
FoodFresh AI - Food Recognition V3 Transforms
Constructs domain-adaptive training transforms and deterministic evaluation transforms.
Augments synthetic disc data and smartphone captures with domestic photometric and geometric variations.
"""

from typing import Tuple
from torchvision import transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_v3_transforms(image_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Construct training and evaluation transforms for V3 domain adaptation.

    Args:
        image_size: Target resolution (default 224 for EfficientNet-B0).

    Returns:
        (train_transforms, eval_transforms)
    """
    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0), ratio=(0.9, 1.1)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomApply([
            transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 1.5))
        ], p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    eval_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    return train_transforms, eval_transforms
