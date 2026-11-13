"""
FoodFresh AI - Food Recognition Pipeline Smoke Test Script (STEP 5)
Executes an end-to-end architecture and DataLoader smoke test WITHOUT downloading weights or training.
"""

from pathlib import Path
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from torch.utils.data import DataLoader
from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import FoodRecognitionDataset
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms
from ml.food_recognition.utils import count_parameters, load_label_map, set_seed


def run_pipeline_smoke_test():
    set_seed(42)
    cfg = FoodRecognitionConfig()

    manifest_status = "FAIL"
    images_status = "FAIL"
    transforms_status = "FAIL"
    dataloader_status = "FAIL"
    model_status = "FAIL"
    forward_status = "FAIL"

    try:
        # 1. Manifest & Label Map Check
        food_to_id, id_to_food, num_classes = load_label_map(cfg.label_map_path)
        if cfg.train_manifest_path.exists() and num_classes == 12:
            manifest_status = "PASS"

        # 2. Dataset & Image Loading
        train_transforms, _ = get_transforms(image_size=cfg.image_size)
        dataset = FoodRecognitionDataset(cfg.train_manifest_path, transform=train_transforms)
        if len(dataset) > 0:
            manifest_status = "PASS"

        # Check first image load
        img_tensor, label_id = dataset[0]
        if isinstance(img_tensor, torch.Tensor) and isinstance(label_id, int):
            images_status = "PASS"

        # 3. Transform Check
        if img_tensor.shape == (3, cfg.image_size, cfg.image_size):
            transforms_status = "PASS"

        # 4. DataLoader Check (Batch size 4 for quick test)
        small_loader = DataLoader(dataset, batch_size=4, shuffle=False)
        batch_images, batch_labels = next(iter(small_loader))
        if batch_images.shape == (4, 3, cfg.image_size, cfg.image_size) and len(batch_labels) == 4:
            dataloader_status = "PASS"

        # 5. Model construction WITHOUT pretrained weights
        model = create_food_recognition_model(num_classes=num_classes, pretrained=False)
        total_p, _ = count_parameters(model)
        if total_p == 4022920 and model.classifier[1].out_features == 12:
            model_status = "PASS"

        # 6. Single Forward Pass (NO backward pass, NO training)
        model.eval()
        with torch.no_grad():
            outputs = model(batch_images)
        if outputs.shape == (4, 12):
            forward_status = "PASS"

    except Exception as e:
        print(f"Smoke test encountered error: {e}", file=sys.stderr)
        raise e

    print("Food Recognition Pipeline Smoke Test")
    print("-------------------------------------")
    print(f"Manifest: {manifest_status}")
    print(f"Images: {images_status}")
    print(f"Transforms: {transforms_status}")
    print(f"DataLoader: {dataloader_status}")
    print(f"Model construction without pretrained weights: {model_status}")
    print(f"Forward pass: {forward_status}")
    print("Training executed: NO")
    print("Pretrained weights downloaded: NO")

    all_passed = (
        manifest_status == "PASS" and
        images_status == "PASS" and
        transforms_status == "PASS" and
        dataloader_status == "PASS" and
        model_status == "PASS" and
        forward_status == "PASS"
    )
    return all_passed


if __name__ == "__main__":
    success = run_pipeline_smoke_test()
    sys.exit(0 if success else 1)
