"""
FoodFresh AI - Freshness Classification Training Script
Two-stage transfer learning for EfficientNet-B0 on AgriFreshNET manifests.
NOTE: Prepared for future training step. DO NOT EXECUTE TRAINING IN STEP 10.
"""

import argparse
import json
import os
from pathlib import Path
import time
from typing import Dict, List, Optional
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from ml.freshness.config import FreshnessConfig
from ml.freshness.dataset import create_freshness_data_loaders
from ml.freshness.model import create_freshness_model
from ml.freshness.utils import set_seed, save_checkpoint


def train_one_epoch(
    model: nn.Module,
    dataloader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    scaler: Optional[torch.amp.GradScaler] = None
) -> Dict[str, float]:
    """Execute one training epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()

        if scaler and device == "cuda":
            with torch.amp.autocast(device_type="cuda"):
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
        correct += torch.sum(preds == labels.data).item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = (correct / total * 100.0) if total > 0 else 0.0
    return {"loss": epoch_loss, "accuracy": epoch_acc}


@torch.no_grad()
def evaluate_epoch(
    model: nn.Module,
    dataloader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]:
    """Execute one validation epoch."""
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
        correct += torch.sum(preds == labels.data).item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = (correct / total * 100.0) if total > 0 else 0.0
    return {"loss": epoch_loss, "accuracy": epoch_acc}


def run_training(config: Optional[FreshnessConfig] = None):
    """
    Orchestrate full freshness classification training pipeline.
    Will be called in the training step.
    """
    if config is None:
        config = FreshnessConfig()

    set_seed(config.random_seed)
    print(f"Initializing Freshness Training on device: {config.device}")

    # 1. Prepare DataLoaders
    train_loader, val_loader, _ = create_freshness_data_loaders(config)
    print(f"DataLoaders created - Train: {len(train_loader.dataset)} samples, Val: {len(val_loader.dataset)} samples")

    # 2. Build Model
    model = create_freshness_model(
        num_classes=config.num_classes,
        pretrained=config.pretrained,
        dropout_rate=config.dropout_rate
    )
    model.to(config.device)

    criterion = nn.CrossEntropyLoss()
    scaler = torch.amp.GradScaler("cuda") if (config.use_amp and config.device == "cuda") else None

    # Stage 1: Train classifier head only
    print("\n--- STAGE 1: Classifier Head Training ---")
    for param in model.features.parameters():
        param.requires_grad = False

    optimizer = AdamW(model.classifier.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=config.stage_1_epochs)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0

    for epoch in range(1, config.stage_1_epochs + 1):
        t0 = time.time()
        train_res = train_one_epoch(model, train_loader, criterion, optimizer, config.device, scaler)
        val_res = evaluate_epoch(model, val_loader, criterion, config.device)
        scheduler.step()
        elapsed = time.time() - t0

        history["train_loss"].append(train_res["loss"])
        history["train_acc"].append(train_res["accuracy"])
        history["val_loss"].append(val_res["loss"])
        history["val_acc"].append(val_res["accuracy"])

        print(f"Epoch {epoch}/{config.stage_1_epochs} [{elapsed:.1f}s] - "
              f"Train Loss: {train_res['loss']:.4f}, Train Acc: {train_res['accuracy']:.2f}% | "
              f"Val Loss: {val_res['loss']:.4f}, Val Acc: {val_res['accuracy']:.2f}%")

        if val_res["accuracy"] > best_val_acc:
            best_val_acc = val_res["accuracy"]
            save_checkpoint(
                model=model,
                epoch=epoch,
                val_loss=val_res["loss"],
                val_acc=val_res["accuracy"],
                checkpoint_path=config.checkpoint_path,
                optimizer=optimizer,
                history=history
            )

    # Stage 2: Fine-tune backbone with lower learning rate
    print("\n--- STAGE 2: Backbone Fine-Tuning ---")
    for param in model.features.parameters():
        param.requires_grad = True

    optimizer_ft = AdamW(model.parameters(), lr=config.fine_tune_learning_rate, weight_decay=config.weight_decay)
    scheduler_ft = CosineAnnealingLR(optimizer_ft, T_max=config.stage_2_epochs)

    for epoch in range(1, config.stage_2_epochs + 1):
        t0 = time.time()
        train_res = train_one_epoch(model, train_loader, criterion, optimizer_ft, config.device, scaler)
        val_res = evaluate_epoch(model, val_loader, criterion, config.device)
        scheduler_ft.step()
        elapsed = time.time() - t0

        curr_total_epoch = config.stage_1_epochs + epoch
        history["train_loss"].append(train_res["loss"])
        history["train_acc"].append(train_res["accuracy"])
        history["val_loss"].append(val_res["loss"])
        history["val_acc"].append(val_res["accuracy"])

        print(f"FT Epoch {epoch}/{config.stage_2_epochs} [{elapsed:.1f}s] - "
              f"Train Loss: {train_res['loss']:.4f}, Train Acc: {train_res['accuracy']:.2f}% | "
              f"Val Loss: {val_res['loss']:.4f}, Val Acc: {val_res['accuracy']:.2f}%")

        if val_res["accuracy"] > best_val_acc:
            best_val_acc = val_res["accuracy"]
            save_checkpoint(
                model=model,
                epoch=curr_total_epoch,
                val_loss=val_res["loss"],
                val_acc=val_res["accuracy"],
                checkpoint_path=config.checkpoint_path,
                optimizer=optimizer_ft,
                history=history
            )

    print(f"\nTraining completed. Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Checkpoint saved to: {config.checkpoint_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FoodFresh AI - Freshness Classifier Training")
    parser.add_argument("--run", action="store_true", help="Execute training (ONLY for future training step)")
    args = parser.parse_args()

    if args.run:
        run_training()
    else:
        print("Freshness training script prepared.")
        print("Pass '--run' to execute training when authorized in future steps.")
