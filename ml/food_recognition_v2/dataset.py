"""
FoodFresh AI - Food Recognition V2 Dataset & DataLoaders
PyTorch Dataset and DataLoader wrappers for Fruits-360 V2 manifests.
"""

import csv
from pathlib import Path
from typing import Callable, Optional, Tuple, Union
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
from ml.food_recognition_v2.config import FoodRecognitionV2Config
from ml.food_recognition_v2.transforms import get_v2_transforms


class FoodRecognitionV2Dataset(Dataset):
    """
    PyTorch Dataset reading Fruits-360 V2 manifests.
    Maps image file paths to integer class IDs (0 to 23).
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
        self.samples = []

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found at: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_path = row["image_path"]
                food_type = row["food_type"]
                class_id = int(row["class_id"])
                original_class = row["original_class"]
                self.samples.append((img_path, class_id, food_type, original_class))

        if len(self.samples) == 0:
            raise ValueError(f"Manifest at {self.manifest_path} contains 0 records.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        img_path, class_id, food_type, orig_class = self.samples[idx]

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                if self.transform is not None:
                    image_tensor = self.transform(img)
                else:
                    from torchvision.transforms.functional import to_tensor
                    image_tensor = to_tensor(img)
        except Exception as e:
            raise IOError(f"Failed to load image at '{img_path}': {e}") from e

        if self.return_metadata:
            return image_tensor, class_id, food_type, img_path

        return image_tensor, class_id


def create_v2_data_loaders(
    config: FoodRecognitionV2Config,
    train_transform: Optional[Callable] = None,
    eval_transform: Optional[Callable] = None
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Construct Train, Validation, and Test DataLoaders for V2.
    """
    default_train, default_eval = get_v2_transforms(image_size=config.image_size)
    train_transform = train_transform or default_train
    eval_transform = eval_transform or default_eval

    train_dataset = FoodRecognitionV2Dataset(
        manifest_path=config.train_manifest_path,
        transform=train_transform
    )

    val_dataset = FoodRecognitionV2Dataset(
        manifest_path=config.val_manifest_path,
        transform=eval_transform
    )

    test_dataset = FoodRecognitionV2Dataset(
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
