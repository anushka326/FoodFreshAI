"""
FoodFresh AI - Food Recognition Utilities
Provides deterministic seeding, device detection, and label mapping helpers.
"""

import json
import os
from pathlib import Path
import random
from typing import Dict, Tuple
import numpy as np
import torch
import torch.nn as nn


def set_seed(seed: int = 42) -> None:
    """Set random seeds for Python, NumPy, and PyTorch to promote determinism."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_device() -> torch.device:
    """Return available torch device (cuda if GPU available, else cpu)."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_label_map(label_map_path: Path) -> Tuple[Dict[str, int], Dict[str, str], int]:
    """
    Load food_to_id and id_to_food mappings from JSON.
    Returns (food_to_id, id_to_food, num_classes).
    """
    if not label_map_path.exists():
        raise FileNotFoundError(f"Label map not found at {label_map_path}")
    with open(label_map_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    food_to_id = data.get("food_to_id", {})
    id_to_food = data.get("id_to_food", {})
    num_classes = data.get("num_classes", len(food_to_id))
    return food_to_id, id_to_food, num_classes


def count_parameters(model: nn.Module) -> Tuple[int, int]:
    """Return (total_parameters, trainable_parameters) for a PyTorch model."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable
