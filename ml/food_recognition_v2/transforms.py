"""
FoodFresh AI - Food Recognition V2 Transforms
Constructs training and evaluation image transformation pipelines for EfficientNet-B0.
Implements realistic augmentations to narrow the domain shift between studio rotary images and real-world cameras.
"""

from typing import Tuple
from torchvision import transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_v2_transforms(image_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Construct training and evaluation transforms for V2.

    Args:
        image_size: Target resolution (default 224 for EfficientNet-B0).

    Returns:
        (train_transforms, eval_transforms)
    """
    train_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        # Moderate color jitter to simulate household and kitchen lighting conditions
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    eval_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    return train_transforms, eval_transforms
