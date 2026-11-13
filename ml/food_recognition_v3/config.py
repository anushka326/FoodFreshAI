"""
FoodFresh AI - Food Recognition V3 Configuration
Defines hyperparameters, filesystem paths, hardware setup, and domain-balancing parameters.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional
import torch


@dataclass
class FoodRecognitionV3Config:
    # Project & Dataset Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    v3_dir: Path = field(init=False)
    train_manifest_path: Path = field(init=False)
    val_manifest_path: Path = field(init=False)
    benchmark_test_manifest_path: Path = field(init=False)
    real_world_test_manifest_path: Path = field(init=False)
    label_map_path: Path = field(init=False)
    config_json_path: Path = field(init=False)

    # Checkpoint Paths
    model_dir: Path = field(init=False)
    v2_checkpoint_path: Path = field(init=False)
    checkpoint_path: Path = field(init=False)
    best_checkpoint_path: Path = field(init=False)

    # Class & Label Metadata
    num_classes: int = 24
    food_to_id: Dict[str, int] = field(default_factory=dict)
    id_to_food: Dict[str, str] = field(default_factory=dict)
    selected_foods: List[str] = field(default_factory=list)

    # Model Architecture
    model_name: str = "efficientnet_b0_v3"
    image_size: int = 224
    dropout_rate: float = 0.2

    # Two-Stage Fine-Tuning Hyperparameters
    batch_size: int = 64
    num_workers: int = 0  # Safe default on Windows
    random_seed: int = 42

    # Stage A: Classifier Head Adaptation
    stage_a_epochs: int = 1
    stage_a_lr: float = 1e-3

    # Stage B: Controlled Full Fine-Tuning
    stage_b_epochs: int = 2
    backbone_lr: float = 2e-5
    head_lr: float = 2e-4
    weight_decay: float = 1e-4
    early_stopping_patience: int = 2

    # Balancing & Optimization
    use_domain_balancing: bool = True
    target_real_world_ratio: float = 0.35  # Target 35% real-world samples per epoch batching
    use_class_weights: bool = True
    use_amp: bool = True

    # Hardware Device
    device: str = field(init=False)

    def __post_init__(self):
        self.v3_dir = self.project_root / "data" / "processed" / "food_recognition_v3"
        manifests_dir = self.v3_dir / "manifests"

        self.train_manifest_path = manifests_dir / "v3_train_manifest.csv"
        self.val_manifest_path = manifests_dir / "v3_val_manifest.csv"
        self.benchmark_test_manifest_path = manifests_dir / "v3_benchmark_test_manifest.csv"
        self.real_world_test_manifest_path = manifests_dir / "v3_real_world_test_manifest.csv"
        self.label_map_path = self.v3_dir / "label_map.json"
        self.config_json_path = self.v3_dir / "dataset_config.json"

        self.model_dir = self.project_root / "models" / "trained"
        self.v2_checkpoint_path = self.model_dir / "food_classifier_v2.pth"
        self.checkpoint_path = self.model_dir / "food_classifier_v3.pth"
        self.best_checkpoint_path = self.model_dir / "food_classifier_v3_best.pth"

        # Load authoritative label map
        if self.label_map_path.exists():
            try:
                with open(self.label_map_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.num_classes = data.get("num_classes", 24)
                self.food_to_id = data.get("food_to_id", {})
                self.id_to_food = data.get("id_to_food", {})
                self.selected_foods = [self.id_to_food[str(i)] for i in range(self.num_classes) if str(i) in self.id_to_food]
            except Exception as e:
                print(f"Warning: Could not parse V3 label map at {self.label_map_path}: {e}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
