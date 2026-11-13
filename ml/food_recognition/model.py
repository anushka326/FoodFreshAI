"""
FoodFresh AI - Food Recognition Model Factory
Constructs EfficientNet-B0 architecture for multi-class food classification.
"""

from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights


def create_food_recognition_model(
    num_classes: int = 12,
    pretrained: bool = True,
    dropout_rate: float = 0.2
) -> nn.Module:
    """
    Construct the EfficientNet-B0 food recognition architecture.

    Args:
        num_classes: Number of food classification output classes (dynamically loaded from label map).
        pretrained: If True (default), loads official TorchVision ImageNet pretrained weights (EfficientNet_B0_Weights.DEFAULT).
                    If False, initializes architecture with random weights without downloading.
        dropout_rate: Dropout probability in the classification head.

    Returns:
        Configured PyTorch nn.Module with customized classifier head for FoodFresh AI.
    """
    if pretrained:
        # Load official TorchVision EfficientNet-B0 ImageNet weights
        weights = EfficientNet_B0_Weights.DEFAULT
        model = efficientnet_b0(weights=weights)
    else:
        # Construct architecture purely in-memory with random weights (NO DOWNLOAD)
        model = efficientnet_b0(weights=None)

    # Replace classifier head for the specific FoodFresh AI class count
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout_rate, inplace=True),
        nn.Linear(in_features=in_features, out_features=num_classes)
    )

    return model


def get_official_transforms():
    """
    Retrieve the official TorchVision preprocessing transform pipeline
    associated with EfficientNet_B0_Weights.DEFAULT.
    """
    weights = EfficientNet_B0_Weights.DEFAULT
    return weights.transforms()

