"""
FoodFresh AI - Food Recognition V2 Model Factory
Constructs EfficientNet-B0 architecture for 24-class food classification.
"""

from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights


def create_food_recognition_v2_model(
    num_classes: int = 24,
    pretrained: bool = True,
    dropout_rate: float = 0.2
) -> nn.Module:
    """
    Construct the EfficientNet-B0 food recognition V2 architecture.

    Args:
        num_classes: Number of output classes (24 for V2).
        pretrained: If True (default), loads official TorchVision ImageNet pretrained weights.
        dropout_rate: Dropout probability in the classification head.

    Returns:
        Configured PyTorch nn.Module with customized 24-class head.
    """
    if pretrained:
        weights = EfficientNet_B0_Weights.DEFAULT
        model = efficientnet_b0(weights=weights)
    else:
        model = efficientnet_b0(weights=None)

    # Replace classifier head for the specific FoodFresh AI V2 class count (24 classes)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout_rate, inplace=True),
        nn.Linear(in_features=in_features, out_features=num_classes)
    )

    return model
