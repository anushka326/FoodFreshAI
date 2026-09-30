"""
FoodFresh AI - Freshness Classification Transforms
Constructs training and evaluation image transformation pipelines for EfficientNet-B0.
Designed to preserve critical biological freshness visual cues (subtle rot spots, discoloration, texture).
"""

from typing import Tuple
from torchvision import transforms

# Standard ImageNet normalization parameters expected by official EfficientNet-B0
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_freshness_transforms(image_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Construct separate image transforms for training and evaluation.

    Args:
        image_size: Target image height and width (default 224 for EfficientNet-B0).

    Returns:
        (train_transforms, eval_transforms)
    """
    # Training transforms with conservative augmentations that preserve freshness signals
    train_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        # Subtle jitter: avoids radical color shifts that corrupt freshness/rot cues
        transforms.ColorJitter(brightness=0.05, contrast=0.05, saturation=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    # Deterministic evaluation transforms
    eval_transforms = transforms.Compose([
        # Freshness V3 trains on Resize(256) followed by a 224 crop. Keep
        # checkpoint evaluation/inference spatial preprocessing identical.
        transforms.Resize((256, 256)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    return train_transforms, eval_transforms
