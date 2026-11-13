"""
FoodFresh AI - Freshness Classification Configuration
Defines hyperparameters, filesystem paths, and device setup for freshness classification.
"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import torch


@dataclass
class FreshnessConfig:
    # Project Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    train_manifest_path: Path = field(init=False)
    val_manifest_path: Path = field(init=False)
    test_manifest_path: Path = field(init=False)
    label_map_path: Path = field(init=False)
    config_json_path: Path = field(init=False)
    model_dir: Path = field(init=False)
    checkpoint_path: Path = field(init=False)

    # Class & Label Metadata
    num_classes: int = 3
    freshness_to_id: Dict[str, int] = field(default_factory=dict)
    id_to_freshness: Dict[str, str] = field(default_factory=dict)
    classes: List[str] = field(default_factory=lambda: ["Fresh", "Semi-Fresh", "Rotten"])

    # Model Architecture
    model_name: str = "efficientnet_b0"
    image_size: int = 224
    pretrained: bool = True
    dropout_rate: float = 0.2

    # Training Hyperparameters (For future training step)
    batch_size: int = 64
    num_workers: int = 0  # Safe default on Windows
    random_seed: int = 42
    learning_rate: float = 1e-3         # Head learning rate
    fine_tune_learning_rate: float = 1e-4  # Backbone fine-tune learning rate
    weight_decay: float = 1e-4
    stage_1_epochs: int = 3
    stage_2_epochs: int = 2
    early_stopping_patience: int = 3
    use_amp: bool = True

    # Hardware Device
    device: str = field(init=False)

    def __post_init__(self):
        # Set paths relative to project root
        processed_dir = self.project_root / "data" / "processed" / "agrifreshnet"
        self.train_manifest_path = processed_dir / "freshness_train_manifest.csv"
        self.val_manifest_path = processed_dir / "freshness_val_manifest.csv"
        self.test_manifest_path = processed_dir / "freshness_test_manifest.csv"
        self.label_map_path = processed_dir / "freshness_label_map.json"
        self.config_json_path = processed_dir / "freshness_config.json"

        self.model_dir = self.project_root / "models" / "trained"
        self.checkpoint_path = self.model_dir / "freshness_classifier.pth"

        # Load class mappings dynamically if available
        if self.label_map_path.exists():
            try:
                with open(self.label_map_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.num_classes = data.get("num_classes", 3)
                self.freshness_to_id = data.get("freshness_to_id", {})
                self.id_to_freshness = data.get("id_to_freshness", {})
                self.classes = [self.id_to_freshness[str(i)] for i in range(self.num_classes) if str(i) in self.id_to_freshness]
            except Exception as e:
                print(f"Warning: Could not parse label map at {self.label_map_path}: {e}")

        # Device selection logic
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
