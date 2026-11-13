"""
FoodFresh AI - Food Recognition V2 Configuration
Defines hyperparameters, filesystem paths, and hardware setup for the expanded 24-class model.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional
import torch


@dataclass
class FoodRecognitionV2Config:
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
    num_classes: int = 24
    food_to_id: Dict[str, int] = field(default_factory=dict)
    id_to_food: Dict[str, str] = field(default_factory=dict)
    selected_foods: List[str] = field(default_factory=list)

    # Model Architecture
    model_name: str = "efficientnet_b0"
    image_size: int = 224
    pretrained: bool = True
    dropout_rate: float = 0.2

    # Two-Stage Training Hyperparameters
    batch_size: int = 128
    num_workers: int = 0  # Safe default on Windows
    random_seed: int = 42
    learning_rate: float = 1e-3           # Stage 1 classifier learning rate
    fine_tune_learning_rate: float = 1e-4    # Stage 2 backbone fine-tuning rate
    weight_decay: float = 1e-4
    stage_1_epochs: int = 3
    stage_2_epochs: int = 2
    early_stopping_patience: int = 3
    use_class_weights: bool = True
    use_amp: bool = True

    # Hardware Device
    device: str = field(init=False)

    def __post_init__(self):
        processed_dir = self.project_root / "data" / "processed" / "fruits360_v2"
        self.train_manifest_path = processed_dir / "fruits360_v2_train_manifest.csv"
        self.val_manifest_path = processed_dir / "fruits360_v2_val_manifest.csv"
        self.test_manifest_path = processed_dir / "fruits360_v2_test_manifest.csv"
        self.label_map_path = processed_dir / "label_map.json"
        self.config_json_path = processed_dir / "fruits360_v2_config.json"

        # V2 Checkpoint: strictly separated from V1 (food_classifier.pth)
        self.model_dir = self.project_root / "models" / "trained"
        self.checkpoint_path = self.model_dir / "food_classifier_v2.pth"

        if self.label_map_path.exists():
            try:
                with open(self.label_map_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.num_classes = data.get("num_classes", 24)
                self.food_to_id = data.get("food_to_id", {})
                self.id_to_food = data.get("id_to_food", {})
                self.selected_foods = [self.id_to_food[str(i)] for i in range(self.num_classes) if str(i) in self.id_to_food]
            except Exception as e:
                print(f"Warning: Could not parse V2 label map at {self.label_map_path}: {e}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
