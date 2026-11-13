"""
FoodFresh AI - Food Recognition Transforms
Constructs training and evaluation image transformation pipelines for EfficientNet-B0.
"""

from typing import Tuple
from torchvision import transforms

# Standard ImageNet normalization parameters expected by EfficientNet
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms(image_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Construct separate image transforms for training and evaluation.

    Args:
        image_size: Target image height and width (default 224 for EfficientNet-B0).

    Returns:
        (train_transforms, eval_transforms)
    """
    train_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    eval_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    return train_transforms, eval_transforms
