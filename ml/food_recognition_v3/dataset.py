"""
FoodFresh AI - Food Recognition V3 Dataset & DataLoaders
PyTorch Dataset and DataLoader wrappers for V3 manifests with domain-balanced sampling support.
"""

import csv
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

from ml.food_recognition_v3.config import FoodRecognitionV3Config
from ml.food_recognition_v3.transforms import get_v3_transforms


class FoodRecognitionV3Dataset(Dataset):
    """
    PyTorch Dataset reading Food Recognition V3 manifests.
    Provides image tensors, integer class IDs (0 to 23), and domain metadata.
    """

    def __init__(
        self,
        manifest_path: Union[str, Path],
        transform: Optional[Callable] = None,
        return_metadata: bool = False
    ):
        self.manifest_path = Path(manifest_path)
        self.transform = transform
        self.return_metadata = return_metadata
        self.samples: List[Dict[str, Union[str, int]]] = []

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found at: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.samples.append({
                    "sample_id": row["sample_id"],
                    "image_path": row["image_path"],
                    "class_id": int(row["class_id"]),
                    "food_class": row["food_class"],
                    "domain": row["domain"],
                    "source": row["source"],
                    "freshness_label": row["freshness_label"]
                })

        if len(self.samples) == 0:
            raise ValueError(f"Manifest at {self.manifest_path} contains 0 records.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        record = self.samples[idx]
        img_path = record["image_path"]
        class_id = record["class_id"]

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                if self.transform is not None:
                    image_tensor = self.transform(img)
                else:
                    from torchvision.transforms.functional import to_tensor
                    image_tensor = to_tensor(img)
        except Exception as e:
            # Fallback for transient read issues
            image_tensor = torch.zeros(3, 224, 224)

        if self.return_metadata:
            return image_tensor, class_id, record
        return image_tensor, class_id


def create_v3_data_loaders(
    config: FoodRecognitionV3Config,
    train_transform: Optional[Callable] = None,
    eval_transform: Optional[Callable] = None
) -> Tuple[DataLoader, DataLoader]:
    """
    Create training and validation DataLoaders with domain-balanced sampling.
    """
    if train_transform is None or eval_transform is None:
        t_trans, e_trans = get_v3_transforms(image_size=config.image_size)
        train_transform = train_transform or t_trans
        eval_transform = eval_transform or e_trans

    train_dataset = FoodRecognitionV3Dataset(
        manifest_path=config.train_manifest_path,
        transform=train_transform,
        return_metadata=False
    )

    val_dataset = FoodRecognitionV3Dataset(
        manifest_path=config.val_manifest_path,
        transform=eval_transform,
        return_metadata=True
    )

    # Construct Domain-Balanced Sampler for Training
    if config.use_domain_balancing:
        # Calculate sample weights: boost real_world representation to target_real_world_ratio
        domains = [s["domain"] for s in train_dataset.samples]
        n_controlled = sum(1 for d in domains if d == "controlled")
        n_real_world = sum(1 for d in domains if d == "real_world")

        target_rw_ratio = config.target_real_world_ratio  # e.g. 0.35
        target_ctrl_ratio = 1.0 - target_rw_ratio

        weight_controlled = target_ctrl_ratio / max(n_controlled, 1)
        weight_real_world = target_rw_ratio / max(n_real_world, 1)

        sample_weights = np.array([
            weight_controlled if d == "controlled" else weight_real_world
            for d in domains
        ], dtype=np.float32)

        sampler = WeightedRandomSampler(
            weights=torch.from_numpy(sample_weights),
            num_samples=len(train_dataset),
            replacement=True
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            sampler=sampler,
            num_workers=config.num_workers,
            pin_memory=torch.cuda.is_available()
        )
    else:
        train_loader = DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_workers,
            pin_memory=torch.cuda.is_available()
        )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=torch.cuda.is_available()
    )

    return train_loader, val_loader
