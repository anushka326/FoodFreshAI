"""
FoodFresh AI - Food Recognition Dataset & DataLoaders
PyTorch Dataset and DataLoader wrappers for Fruits-360 manifests.
"""

import csv
import os
from pathlib import Path
from typing import Callable, Optional, Tuple
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.transforms import get_transforms


class FoodRecognitionDataset(Dataset):
    """
    PyTorch Dataset reading Fruits-360 manifests.
    Maps image file paths to normalized integer class labels.
    """

    def __init__(self, manifest_path: Path, transform: Optional[Callable] = None):
        """
        Args:
            manifest_path: Path to train or test CSV manifest.
            transform: Optional torchvision transform.
        """
        self.manifest_path = Path(manifest_path)
        self.transform = transform
        self.samples = []

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        # Load samples from CSV
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_p = row["image_path"]
                lbl_id = int(row["label_id"])
                norm_food = row["normalized_food"]
                self.samples.append((img_p, lbl_id, norm_food))

        if len(self.samples) == 0:
            raise ValueError(f"Manifest at {self.manifest_path} contains 0 sample records.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label_id, _ = self.samples[idx]

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                if self.transform is not None:
                    image_tensor = self.transform(img)
                else:
                    # Fallback to simple ToTensor if no transform provided
                    from torchvision.transforms.functional import to_tensor
                    image_tensor = to_tensor(img)
        except Exception as e:
            raise IOError(f"Failed to load or process image at '{img_path}': {e}") from e

        return image_tensor, label_id


def create_data_loaders(
    config: FoodRecognitionConfig,
    train_transform: Optional[Callable] = None,
    eval_transform: Optional[Callable] = None,
    include_val: bool = True
) -> Tuple[DataLoader, Optional[DataLoader], DataLoader]:
    """
    Construct Train, Validation, and Test DataLoaders from configuration.

    Args:
        config: FoodRecognitionConfig instance.
        train_transform: Optional training transform. If None, uses default.
        eval_transform: Optional evaluation transform. If None, uses default.
        include_val: Whether to create and return a validation loader.

    Returns:
        (train_loader, val_loader, test_loader)
    """
    default_train, default_eval = get_transforms(image_size=config.image_size)
    train_transform = train_transform or default_train
    eval_transform = eval_transform or default_eval

    # Use train split if available, otherwise fallback to train manifest
    train_path = config.train_split_path if (hasattr(config, "train_split_path") and config.train_split_path.exists()) else config.train_manifest_path
    train_dataset = FoodRecognitionDataset(
        manifest_path=train_path,
        transform=train_transform
    )

    val_loader = None
    if include_val and hasattr(config, "val_split_path") and config.val_split_path.exists():
        val_dataset = FoodRecognitionDataset(
            manifest_path=config.val_split_path,
            transform=eval_transform
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=(config.device == "cuda")
        )

    test_dataset = FoodRecognitionDataset(
        manifest_path=config.test_manifest_path,
        transform=eval_transform
    )

    pin_memory = (config.device == "cuda")

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=pin_memory
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=pin_memory
    )

    return train_loader, val_loader, test_loader
