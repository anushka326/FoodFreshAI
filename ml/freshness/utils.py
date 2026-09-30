"""
FoodFresh AI - Freshness Classification Utilities
Helper functions for reproducibility, checkpointing, and metric logging.
"""

import json
import os
from pathlib import Path
import random
from typing import Any, Dict, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn


def set_seed(seed: int = 42) -> None:
    """Set random seed across Python, NumPy, and PyTorch for deterministic results."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def load_label_map(label_map_path: Path) -> Tuple[Dict[str, int], Dict[str, str]]:
    """Load canonical freshness label mapping from JSON."""
    if not label_map_path.exists():
        raise FileNotFoundError(f"Label map not found at {label_map_path}")

    with open(label_map_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    freshness_to_id = data.get("freshness_to_id", {})
    id_to_freshness = data.get("id_to_freshness", {})
    return freshness_to_id, id_to_freshness


def save_checkpoint(
    model: nn.Module,
    epoch: int,
    val_loss: float,
    val_acc: float,
    checkpoint_path: Path,
    optimizer: Optional[torch.optim.Optimizer] = None,
    history: Optional[Dict[str, Any]] = None,
    label_map: Optional[Dict[str, Any]] = None
) -> None:
    """Save model checkpoint and training metadata."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer else None,
        "val_loss": val_loss,
        "val_acc": val_acc,
        "history": history or {},
        "label_map": label_map or {},
        "architecture": "EfficientNet-B0",
        "num_classes": 3
    }
    torch.save(state, checkpoint_path)


def load_checkpoint(
    checkpoint_path: Path,
    model: nn.Module,
    device: str = "cpu"
) -> Dict[str, Any]:
    """Load model weights from checkpoint."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")

    checkpoint = torch.load(checkpoint_path, map_location=device)
    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()
    return checkpoint
