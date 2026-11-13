"""
FoodFresh AI - Freshness Classification Dataset & DataLoaders
PyTorch Dataset and DataLoader implementations for AgriFreshNET manifests.
"""

import csv
from pathlib import Path
from typing import Callable, Optional, Tuple, Union, Any, Dict
from PIL import Image, ImageOps
import torch
from torch.utils.data import DataLoader, Dataset
from ml.freshness.config import FreshnessConfig
from ml.freshness.transforms import get_freshness_transforms


class FreshnessDataset(Dataset):
    """
    PyTorch Dataset reading AgriFreshNET freshness manifests.
    Maps image file paths to integer freshness classes (0: Fresh, 1: Semi-Fresh, 2: Rotten).
    """

    def __init__(
        self,
        manifest_path: Union[str, Path],
        transform: Optional[Callable] = None,
        return_metadata: bool = False
    ):
        """
        Args:
            manifest_path: Path to CSV manifest.
            transform: Optional torchvision transform.
            return_metadata: If True, returns (image, label, food_type, image_path).
        """
        self.manifest_path = Path(manifest_path)
        self.transform = transform
        self.return_metadata = return_metadata
        self.samples = []

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_path = row["image_path"]
                food_type = row["food_type"]
                freshness_label = row["freshness_label"]
                freshness_id = int(row["freshness_id"])
                original_class = row["original_class"]
                self.samples.append({
                    "image_path": img_path,
                    "food_type": food_type,
                    "freshness_label": freshness_label,
                    "freshness_id": freshness_id,
                    "original_class": original_class
                })

        if len(self.samples) == 0:
            raise ValueError(f"Manifest at {self.manifest_path} contains 0 records.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Union[Tuple[torch.Tensor, int], Tuple[torch.Tensor, int, str, str]]:
        item = self.samples[idx]
        img_path = item["image_path"]
        label_id = item["freshness_id"]
        food_type = item["food_type"]

        try:
            with Image.open(img_path) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGB")
                if self.transform is not None:
                    image_tensor = self.transform(img)
                else:
                    from torchvision.transforms.functional import to_tensor
                    image_tensor = to_tensor(img)
        except Exception as e:
            raise IOError(f"Failed to load or process image at '{img_path}': {e}") from e

        if self.return_metadata:
            return image_tensor, label_id, food_type, img_path

        return image_tensor, label_id


def create_freshness_data_loaders(
    config: FreshnessConfig,
    train_transform: Optional[Callable] = None,
    eval_transform: Optional[Callable] = None
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Construct Train, Validation, and Test DataLoaders from FreshnessConfig.

    Args:
        config: FreshnessConfig instance.
        train_transform: Optional training transform.
        eval_transform: Optional evaluation transform.

    Returns:
        (train_loader, val_loader, test_loader)
    """
    default_train, default_eval = get_freshness_transforms(image_size=config.image_size)
    train_transform = train_transform or default_train
    eval_transform = eval_transform or default_eval

    train_dataset = FreshnessDataset(
        manifest_path=config.train_manifest_path,
        transform=train_transform
    )

    val_dataset = FreshnessDataset(
        manifest_path=config.val_manifest_path,
        transform=eval_transform
    )

    test_dataset = FreshnessDataset(
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

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
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
