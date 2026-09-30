"""
FoodFresh AI - Food Recognition V2 Training Pipeline (STEPS 16-19)
Executes two-stage transfer learning on the 24-class Fruits-360 V2 dataset:
- Stage 1: Freeze backbone, train 24-class classification head
- Stage 2: Fine-tune backbone with lower learning rate
- Class-weighted CrossEntropyLoss for imbalance mitigation
- Mixed-Precision (AMP) acceleration on CUDA GPU
- Saves best validation checkpoint to models/trained/food_classifier_v2.pth (Preserves V1)
- Generates reports/food_recognition_v2_training_report.md and training curves
"""

import json
import os
from pathlib import Path
import random
import sys
import time
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition_v2.config import FoodRecognitionV2Config
from ml.food_recognition_v2.dataset import create_v2_data_loaders
from ml.food_recognition_v2.model import create_food_recognition_v2_model


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def compute_v2_class_weights(manifest_path: Path, num_classes: int) -> torch.Tensor:
    """
    Compute smoothed inverse-frequency class weights from training manifest.
    w[c] = (total_samples / (num_classes * count[c])) ** 0.5
    """
    df = pd.read_csv(manifest_path)
    counts = df["class_id"].value_counts().to_dict()
    total = len(df)

    weights = []
    for c in range(num_classes):
        cnt = counts.get(c, 1)
        # Square root smoothing prevents extreme gradients for small classes
        w = (total / (num_classes * cnt)) ** 0.5
        weights.append(w)

    t_weights = torch.tensor(weights, dtype=torch.float32)
    t_weights = t_weights / t_weights.mean()
    return t_weights


def train_one_epoch(
    model: nn.Module,
    dataloader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    scaler: Optional[torch.amp.GradScaler] = None
) -> Tuple[float, float]:
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    use_cuda_amp = (scaler is not None) and (device == "cuda")

    for images, labels in dataloader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()

        if use_cuda_amp:
            with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                outputs = model(images)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels).item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = (correct / total * 100.0) if total > 0 else 0.0
    return epoch_loss, epoch_acc


@torch.no_grad()
def evaluate_epoch(
    model: nn.Module,
    dataloader,
    criterion: nn.Module,
    device: str
) -> Tuple[float, float]:
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels).item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = (correct / total * 100.0) if total > 0 else 0.0
    return epoch_loss, epoch_acc


def train_food_recognition_v2(config: Optional[FoodRecognitionV2Config] = None):
    if config is None:
        config = FoodRecognitionV2Config()

    set_seed(config.random_seed)
    print("=" * 60)
    print("FOODFRESH AI - TRAINING FOOD RECOGNITION V2 (24 CLASSES)")
    print("=" * 60)
    print(f"Device: {config.device}")
    print(f"Output Checkpoint: {config.checkpoint_path}")
    print(f"Number of classes: {config.num_classes} (includes Pomegranate)")

    # 1. Prepare DataLoaders
    train_loader, val_loader, test_loader = create_v2_data_loaders(config)
    print(f"Loaded: Train={len(train_loader.dataset):,} | Val={len(val_loader.dataset):,} | Test={len(test_loader.dataset):,}")

    # 2. Compute Class Weights for Imbalance
    class_weights = compute_v2_class_weights(config.train_manifest_path, config.num_classes)
    class_weights = class_weights.to(config.device)
    print(f"Class weights computed (range: {class_weights.min().item():.2f} - {class_weights.max().item():.2f})")

    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # 3. Model Construction with Pretrained Weights
    print("Initializing EfficientNet-B0 with official ImageNet pretrained weights...")
    model = create_food_recognition_v2_model(
        num_classes=config.num_classes,
        pretrained=config.pretrained,
        dropout_rate=config.dropout_rate
    )
    model.to(config.device)

    scaler = torch.amp.GradScaler("cuda") if (config.use_amp and config.device == "cuda") else None

    history = {
        "epoch": [],
        "stage": [],
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "lr": []
    }

    best_val_acc = 0.0
    best_val_loss = float("inf")
    best_epoch = 0

    # Ensure model save directory exists
    config.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # STAGE 1: Train Classification Head (Backbone Frozen)
    # =========================================================================
    print("\n--- STAGE 1: Training Classification Head (Backbone Frozen) ---")
    for param in model.features.parameters():
        param.requires_grad = False

    optimizer_s1 = AdamW(model.classifier.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler_s1 = CosineAnnealingLR(optimizer_s1, T_max=config.stage_1_epochs)

    for ep in range(1, config.stage_1_epochs + 1):
        t0 = time.time()
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer_s1, config.device, scaler)
        val_loss, val_acc = evaluate_epoch(model, val_loader, criterion, config.device)
        cur_lr = optimizer_s1.param_groups[0]["lr"]
        scheduler_s1.step()
        elapsed = time.time() - t0

        history["epoch"].append(ep)
        history["stage"].append("Stage 1")
        history["train_loss"].append(round(tr_loss, 4))
        history["train_acc"].append(round(tr_acc, 2))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(round(val_acc, 2))
        history["lr"].append(cur_lr)

        print(f"Stage 1 - Epoch {ep}/{config.stage_1_epochs} [{elapsed:.1f}s] | "
              f"Train Loss: {tr_loss:.4f}, Train Acc: {tr_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% (lr={cur_lr:.1e})")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            best_epoch = ep
            save_v2_checkpoint(model, optimizer_s1, ep, "Stage 1", val_acc, val_loss, config)

    # =========================================================================
    # STAGE 2: Fine-Tuning Backbone (Unfrozen with Lower LR)
    # =========================================================================
    print("\n--- STAGE 2: Fine-Tuning Backbone Layers ---")
    for param in model.features.parameters():
        param.requires_grad = True

    optimizer_s2 = AdamW(model.parameters(), lr=config.fine_tune_learning_rate, weight_decay=config.weight_decay)
    scheduler_s2 = CosineAnnealingLR(optimizer_s2, T_max=config.stage_2_epochs)

    for ep in range(1, config.stage_2_epochs + 1):
        global_ep = config.stage_1_epochs + ep
        t0 = time.time()
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer_s2, config.device, scaler)
        val_loss, val_acc = evaluate_epoch(model, val_loader, criterion, config.device)
        cur_lr = optimizer_s2.param_groups[0]["lr"]
        scheduler_s2.step()
        elapsed = time.time() - t0

        history["epoch"].append(global_ep)
        history["stage"].append("Stage 2")
        history["train_loss"].append(round(tr_loss, 4))
        history["train_acc"].append(round(tr_acc, 2))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(round(val_acc, 2))
        history["lr"].append(cur_lr)

        print(f"Stage 2 - Epoch {ep}/{config.stage_2_epochs} [{elapsed:.1f}s] | "
              f"Train Loss: {tr_loss:.4f}, Train Acc: {tr_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% (lr={cur_lr:.1e})")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            best_epoch = global_ep
            save_v2_checkpoint(model, optimizer_s2, global_ep, "Stage 2", val_acc, val_loss, config)

    print("\n" + "=" * 60)
    print(f"V2 Training Complete! Best Validation Accuracy: {best_val_acc:.2f}% (at Epoch {best_epoch})")
    print(f"Checkpoint successfully preserved at: {config.checkpoint_path}")
    print("=" * 60)

    # Save training curves plot
    save_training_curves(history, config.project_root / "reports" / "food_recognition_v2_training_curves.png")

    # Save training markdown report
    save_training_report(history, best_epoch, best_val_acc, best_val_loss, config)

    return history


def save_v2_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    stage: str,
    val_acc: float,
    val_loss: float,
    config: FoodRecognitionV2Config
):
    checkpoint_content = {
        "model_name": "EfficientNet-B0_V2",
        "num_classes": config.num_classes,
        "food_to_id": config.food_to_id,
        "id_to_food": config.id_to_food,
        "selected_foods": config.selected_foods,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_val_accuracy": val_acc,
        "best_val_loss": val_loss,
        "epoch": epoch,
        "stage": stage,
        "image_size": config.image_size,
        "training_config": {
            "batch_size": config.batch_size,
            "random_seed": config.random_seed,
            "learning_rate": config.learning_rate,
            "fine_tune_learning_rate": config.fine_tune_learning_rate
        }
    }
    torch.save(checkpoint_content, config.checkpoint_path)
    print(f"  --> Saved new best checkpoint: {config.checkpoint_path.name} (Val Acc: {val_acc:.2f}%)")


def save_training_curves(history: Dict, save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    epochs = history["epoch"]

    plt.figure(figsize=(12, 5))

    # Loss plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, history["train_loss"], label="Train Loss", marker="o", color="#2563eb")
    plt.plot(epochs, history["val_loss"], label="Val Loss", marker="s", color="#dc2626")
    plt.title("Food Recognition V2 - Loss Curve")
    plt.xlabel("Epoch")
    plt.ylabel("CrossEntropy Loss")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    # Accuracy plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, history["train_acc"], label="Train Accuracy", marker="o", color="#16a34a")
    plt.plot(epochs, history["val_acc"], label="Val Accuracy", marker="s", color="#d97706")
    plt.title("Food Recognition V2 - Accuracy Curve")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"Training curves saved: {save_path}")


def save_training_report(history: Dict, best_epoch: int, best_acc: float, best_loss: float, config: FoodRecognitionV2Config):
    report_path = config.project_root / "reports" / "food_recognition_v2_training_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Food Recognition V2 Training Report\n\n")
        f.write("## Overview\n")
        f.write(f"- **Architecture:** TorchVision EfficientNet-B0 (`pretrained=True`)\n")
        f.write(f"- **Classes:** {config.num_classes} categories (Expanded vocabulary including Pomegranate)\n")
        f.write(f"- **Checkpoint Target:** `{config.checkpoint_path.name}`\n")
        f.write(f"- **Best Validation Accuracy:** **{best_acc:.2f}%** (Epoch {best_epoch})\n")
        f.write(f"- **Best Validation Loss:** **{best_loss:.4f}**\n\n")

        f.write("## Epoch History\n\n")
        f.write("| Epoch | Stage | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Learning Rate |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for i in range(len(history["epoch"])):
            f.write(f"| {history['epoch'][i]} | {history['stage'][i]} | {history['train_loss'][i]} | "
                    f"{history['train_acc'][i]}% | {history['val_loss'][i]} | {history['val_acc'][i]}% | "
                    f"{history['lr'][i]:.1e} |\n")

        f.write("\n## Checkpoint Separation\n")
        f.write("- V1 Checkpoint (`models/trained/food_classifier.pth`) was strictly preserved and unchanged.\n")
        f.write("- V2 Checkpoint (`models/trained/food_classifier_v2.pth`) independently trained with 24 classes.\n")

    print(f"Training report saved: {report_path}")


if __name__ == "__main__":
    train_food_recognition_v2()
