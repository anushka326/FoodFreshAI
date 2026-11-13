"""
FoodFresh AI - Freshness Classification Model Factory
Constructs EfficientNet-B0 architecture for 3-class freshness classification.
"""

from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights


def create_freshness_model(
    num_classes: int = 3,
    pretrained: bool = True,
    dropout_rate: float = 0.2
) -> nn.Module:
    """
    Construct the EfficientNet-B0 freshness classification architecture.

    Args:
        num_classes: Number of freshness output classes (default 3: Fresh, Semi-Fresh, Rotten).
        pretrained: If True (default), loads official TorchVision ImageNet pretrained weights.
                    If False, initializes architecture without loading pretrained weights.
        dropout_rate: Dropout probability in the classification head.

    Returns:
        Configured PyTorch nn.Module with customized 3-class classifier head.
    """
    if pretrained:
        weights = EfficientNet_B0_Weights.DEFAULT
        model = efficientnet_b0(weights=weights)
    else:
        model = efficientnet_b0(weights=None)

    # Replace classifier head for the specific FoodFresh AI freshness class count (3 classes)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout_rate, inplace=True),
        nn.Linear(in_features=in_features, out_features=num_classes)
    )

    return model


def get_official_freshness_transforms():
    """
    Retrieve the official TorchVision preprocessing transform pipeline
    associated with EfficientNet_B0_Weights.DEFAULT.
    """
    weights = EfficientNet_B0_Weights.DEFAULT
    return weights.transforms()
