"""
FoodFresh AI - Food Recognition V3 Model Factory
Initializes EfficientNet-B0 architecture directly from the trained V2 checkpoint
(models/trained/food_classifier_v2.pth), enabling domain-adaptive transfer learning.
"""

from pathlib import Path
from typing import Optional, Tuple
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0

from ml.food_recognition_v3.config import FoodRecognitionV3Config


def create_v3_architecture(num_classes: int = 24, dropout_rate: float = 0.2) -> nn.Module:
    """
    Construct the baseline EfficientNet-B0 architecture matching Food Recognition V2/V3.
    """
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout_rate, inplace=True),
        nn.Linear(in_features=in_features, out_features=num_classes)
    )
    return model


def load_v3_model_from_v2(
    config: FoodRecognitionV3Config,
    device: Optional[torch.device] = None
) -> Tuple[nn.Module, dict]:
    """
    Load the trained V2 Food Recognition checkpoint into the V3 model.

    Args:
        config: V3 training configuration.
        device: Target PyTorch compute device.

    Returns:
        (model, checkpoint_metadata)
    """
    target_device = device or torch.device(config.device)
    v2_path = config.v2_checkpoint_path

    if not v2_path.exists():
        raise FileNotFoundError(f"V2 initialization checkpoint not found at: {v2_path}")

    print(f"Loading V2 initialization checkpoint from: {v2_path} on {target_device}")
    checkpoint = torch.load(v2_path, map_location=target_device, weights_only=False)

    ckpt_classes = checkpoint.get("num_classes", 24)
    if ckpt_classes != config.num_classes:
        raise ValueError(
            f"V2 checkpoint class count ({ckpt_classes}) does not match V3 config ({config.num_classes})!"
        )

    # Reconstruct architecture and load weights
    model = create_v3_architecture(num_classes=config.num_classes, dropout_rate=config.dropout_rate)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(target_device)

    metadata = {
        "v2_best_val_accuracy": checkpoint.get("best_val_accuracy"),
        "v2_best_val_loss": checkpoint.get("best_val_loss"),
        "v2_epoch": checkpoint.get("epoch"),
        "v2_stage": checkpoint.get("stage"),
        "num_classes": ckpt_classes
    }

    print(f"Successfully loaded V2 model state (best val acc: {metadata['v2_best_val_accuracy']}%, {ckpt_classes} classes).")
    return model, metadata
