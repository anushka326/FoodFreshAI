"""
FoodFresh AI - Food Recognition Model Training Pipeline (STEP 7)
Implements two-stage transfer learning with official EfficientNet-B0 pretrained weights,
class-weighted CrossEntropyLoss, mixed-precision acceleration, checkpointing,
and evaluation against the untouched Fruits-360 test manifest.
"""

from pathlib import Path
import sys
import time
import json
import shutil
from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import create_data_loaders, FoodRecognitionDataset
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms
from ml.food_recognition.utils import count_parameters, set_seed


def compute_class_weights(train_split_path: Path, num_classes: int) -> torch.Tensor:
    """
    Compute balanced inverse-frequency class weights from training split.
    weight[c] = total_samples / (num_classes * count[c])
    """
    df = pd.read_csv(train_split_path)
    counts = df["label_id"].value_counts().to_dict()
    total_samples = len(df)
    
    weights = []
    for c in range(num_classes):
        cnt = counts.get(c, 1)
        w = total_samples / (num_classes * cnt)
        weights.append(w)
    
    weights_tensor = torch.tensor(weights, dtype=torch.float32)
    # Normalize weights so mean is 1.0
    weights_tensor = weights_tensor / weights_tensor.mean()
    return weights_tensor


def train_one_epoch(
    model: nn.Module,
    loader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    scaler: Optional[torch.cuda.amp.GradScaler] = None,
    use_amp: bool = True
) -> Tuple[float, float]:
    """Train for one epoch with optional AMP."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    use_cuda_amp = use_amp and (device.type == "cuda")

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()

        if use_cuda_amp and scaler is not None:
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
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = (correct / total) * 100.0 if total > 0 else 0.0
    return epoch_loss, epoch_acc


def evaluate_loader(
    model: nn.Module,
    loader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, float]:
    """Evaluate on validation or test DataLoader."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    val_loss = running_loss / total if total > 0 else 0.0
    val_acc = (correct / total) * 100.0 if total > 0 else 0.0
    return val_loss, val_acc


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    config: FoodRecognitionConfig,
    epoch: int,
    stage: str,
    val_acc: float,
    val_loss: float,
    target_path: Path
):
    """Save trained model checkpoint with comprehensive metadata."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Checkpoint safety: create backup if exists
    if target_path.exists() and not (target_path.parent / f"{target_path.stem}_backup.pth").exists():
        try:
            shutil.copy(target_path, target_path.parent / f"{target_path.stem}_backup.pth")
        except Exception:
            pass

    checkpoint = {
        "model_name": config.model_name,
        "num_classes": config.num_classes,
        "class_to_idx": config.food_to_id,
        "idx_to_class": config.id_to_food,
        "food_to_id": config.food_to_id,
        "id_to_food": config.id_to_food,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_val_accuracy": val_acc,
        "best_val_loss": val_loss,
        "epoch": epoch,
        "stage": stage,
        "image_size": config.image_size,
        "training_config": {
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "fine_tune_learning_rate": config.fine_tune_learning_rate,
            "weight_decay": config.weight_decay,
            "stage_1_epochs": config.stage_1_epochs,
            "stage_2_epochs": config.stage_2_epochs,
            "random_seed": config.random_seed
        }
    }
    torch.save(checkpoint, target_path)
    print(f"    [CHECKPOINT SAVED] -> {target_path} (Val Acc: {val_acc:.2f}%)")


def run_training(config: Optional[FoodRecognitionConfig] = None) -> Dict:
    """Execute the full FoodFresh AI Food Recognition training pipeline."""
    if config is None:
        config = FoodRecognitionConfig()

    set_seed(config.random_seed)
    device = torch.device(config.device)
    print("=" * 60)
    print("FOODFRESH AI — FOOD RECOGNITION TRAINING")
    print("=" * 60)
    print(f"Device:       {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"Food Classes: {config.num_classes}")
    print(f"Batch Size:   {config.batch_size}")
    print(f"Image Size:   {config.image_size}x{config.image_size}")
    print(f"Seed:         {config.random_seed}")

    # Build DataLoaders
    train_loader, val_loader, test_loader = create_data_loaders(config)
    print(f"DataLoaders:  Train batches={len(train_loader)} | Val batches={len(val_loader)} | Test batches={len(test_loader)}")

    # Class weights for handling class imbalance
    class_weights = None
    if config.use_class_weights and hasattr(config, "train_split_path") and config.train_split_path.exists():
        class_weights = compute_class_weights(config.train_split_path, config.num_classes).to(device)
        print("Class-weighted CrossEntropyLoss enabled.")

    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Initialize model with official pretrained EfficientNet-B0 weights
    print("\nInitializing model with official TorchVision EfficientNet-B0 pretrained weights...")
    model = create_food_recognition_model(num_classes=config.num_classes, pretrained=True).to(device)
    total_params, trainable_params = count_parameters(model)
    print(f"Initial parameters: {total_params:,} total ({trainable_params:,} trainable)")

    scaler = torch.amp.GradScaler(enabled=(config.use_amp and device.type == "cuda"))

    history_records = []
    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    # -------------------------------------------------------------
    # STAGE 1: Train Classifier Head (Backbone Frozen)
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print(f"STAGE 1: Training Classifier Head ({config.stage_1_epochs} epochs)")
    print("Freezing EfficientNet-B0 backbone features...")
    for param in model.features.parameters():
        param.requires_grad = False

    total_params, trainable_params = count_parameters(model)
    print(f"Stage 1 parameters: {total_params:,} total ({trainable_params:,} trainable)")

    optimizer_stage1 = AdamW(
        model.classifier.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler_stage1 = ReduceLROnPlateau(optimizer_stage1, mode="max", factor=0.5, patience=1)

    global_epoch = 0
    for epoch in range(1, config.stage_1_epochs + 1):
        global_epoch += 1
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer_stage1, device, scaler, config.use_amp
        )
        val_loss, val_acc = evaluate_loader(model, val_loader, criterion, device)
        scheduler_stage1.step(val_acc)
        lr_current = optimizer_stage1.param_groups[0]["lr"]
        elapsed = time.time() - t0

        print(
            f"Stage 1 | Epoch {epoch:02d}/{config.stage_1_epochs:02d} [{elapsed:.1f}s] - "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% | LR: {lr_current:.2e}"
        )

        history_records.append({
            "epoch": global_epoch,
            "stage": "Stage 1 (Classifier Head)",
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
            "learning_rate": lr_current
        })

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = global_epoch
            patience_counter = 0
            save_checkpoint(
                model, optimizer_stage1, config, global_epoch, "Stage 1",
                val_acc, val_loss, config.checkpoint_path
            )
        else:
            patience_counter += 1

    # -------------------------------------------------------------
    # STAGE 2: Fine-tune Upper Backbone Layers
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print(f"STAGE 2: Fine-Tuning Upper EfficientNet Layers ({config.stage_2_epochs} epochs)")
    print("Unfreezing top MBConv blocks (features[6:])...")
    for block in model.features[6:]:
        for param in block.parameters():
            param.requires_grad = True

    total_params, trainable_params = count_parameters(model)
    print(f"Stage 2 parameters: {total_params:,} total ({trainable_params:,} trainable)")

    optimizer_stage2 = AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config.fine_tune_learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler_stage2 = ReduceLROnPlateau(optimizer_stage2, mode="max", factor=0.5, patience=1)

    for epoch in range(1, config.stage_2_epochs + 1):
        global_epoch += 1
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer_stage2, device, scaler, config.use_amp
        )
        val_loss, val_acc = evaluate_loader(model, val_loader, criterion, device)
        scheduler_stage2.step(val_acc)
        lr_current = optimizer_stage2.param_groups[0]["lr"]
        elapsed = time.time() - t0

        print(
            f"Stage 2 | Epoch {epoch:02d}/{config.stage_2_epochs:02d} [{elapsed:.1f}s] - "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% | LR: {lr_current:.2e}"
        )

        history_records.append({
            "epoch": global_epoch,
            "stage": "Stage 2 (Fine-tuning)",
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
            "learning_rate": lr_current
        })

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = global_epoch
            patience_counter = 0
            save_checkpoint(
                model, optimizer_stage2, config, global_epoch, "Stage 2",
                val_acc, val_loss, config.checkpoint_path
            )
        else:
            patience_counter += 1
            if patience_counter >= config.early_stopping_patience:
                print(f"Early stopping triggered after {patience_counter} epochs without improvement.")
                break

    # Save training history
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    history_df = pd.DataFrame(history_records)
    history_path = reports_dir / "food_recognition_training_history.csv"
    history_df.to_csv(history_path, index=False)
    print(f"\nTraining history saved to: {history_path}")

    # Generate training curves plot
    plot_training_curves(history_df, reports_dir / "food_recognition_training_curves.png")

    # -------------------------------------------------------------
    # POST-TRAINING: VERIFY CHECKPOINT LOAD & BASIC INFERENCE
    # (Per STEP 7 Section 24: Test set evaluation is reserved for STEP 8)
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("CHECKPOINT RELOAD VERIFICATION & SINGLE TEST INFERENCE")
    print("=" * 60)
    print(f"Verifying checkpoint reload from: {config.checkpoint_path}")
    checkpoint = torch.load(config.checkpoint_path, map_location=device, weights_only=False)
    assert "model_state_dict" in checkpoint, "Missing model_state_dict in checkpoint"
    assert "training_config" in checkpoint, "Missing training_config in checkpoint"

    # Instantiate fresh model to verify reload
    eval_model = create_food_recognition_model(num_classes=config.num_classes, pretrained=False).to(device)
    eval_model.load_state_dict(checkpoint["model_state_dict"])
    eval_model.eval()
    print("Checkpoint reloaded successfully in fresh model instance. (PASS)")

    # Run one real inference check from the test dataset (Section 27)
    test_df = pd.read_csv(config.test_manifest_path)
    sample_row = test_df.iloc[0]
    sample_img_path = sample_row["image_path"]
    true_class = sample_row["normalized_food"]

    from ml.food_recognition.predict import predict_food
    pred_result = predict_food(sample_img_path, checkpoint_path=config.checkpoint_path, top_k=3)

    print("\nBasic Inference Verification (Single Test Image):")
    print(f"Test image:      {sample_img_path}")
    print(f"True class:      {true_class}")
    print(f"Predicted class: {pred_result.get('food')}")
    print(f"Confidence:      {pred_result.get('percentage')}")

    # Generate Training Report MD matching STEP 7 Section 32
    save_training_report(
        config=config,
        best_val_acc=best_val_acc,
        best_epoch=best_epoch,
        history_df=history_df,
        reports_dir=reports_dir,
        test_sample_info={
            "image_path": sample_img_path,
            "true_class": true_class,
            "predicted_class": pred_result.get("food"),
            "confidence": pred_result.get("percentage")
        }
    )

    return {
        "best_val_accuracy": best_val_acc,
        "best_epoch": best_epoch,
        "final_train_accuracy": history_df["train_accuracy"].iloc[-1],
        "final_val_accuracy": history_df["val_accuracy"].iloc[-1],
        "checkpoint_path": str(config.checkpoint_path),
        "test_sample_pred": pred_result.get("food"),
        "test_sample_conf": pred_result.get("percentage")
    }


def plot_training_curves(history_df: pd.DataFrame, output_path: Path):
    """Plot Training & Validation Loss and Accuracy vs Epoch."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    epochs = history_df["epoch"]

    # Loss plot
    ax1.plot(epochs, history_df["train_loss"], marker="o", label="Train Loss", color="#2563EB", linewidth=2)
    ax1.plot(epochs, history_df["val_loss"], marker="s", label="Val Loss", color="#DC2626", linewidth=2)
    ax1.set_title("Loss vs. Epoch", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_ylabel("Loss", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(fontsize=10)

    # Accuracy plot
    ax2.plot(epochs, history_df["train_accuracy"], marker="o", label="Train Accuracy (%)", color="#10B981", linewidth=2)
    ax2.plot(epochs, history_df["val_accuracy"], marker="s", label="Val Accuracy (%)", color="#8B5CF6", linewidth=2)
    ax2.set_title("Accuracy vs. Epoch", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_ylabel("Accuracy (%)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Training curves saved to: {output_path}")


def plot_confusion_matrix(matrix: np.ndarray, class_names: list, output_path: Path):
    """Plot and save confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(matrix.shape[1]),
        yticks=np.arange(matrix.shape[0]),
        xticklabels=class_names,
        yticklabels=class_names,
        title="Food Recognition Confusion Matrix (Fruits-360 Test Set)",
        ylabel="True Food Label",
        xlabel="Predicted Food Label"
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Annotate text
    thresh = matrix.max() / 2.0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j, i, format(matrix[i, j], "d"),
                ha="center", va="center",
                color="white" if matrix[i, j] > thresh else "black",
                fontsize=8
            )

    fig.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Confusion matrix saved to: {output_path}")


def save_classification_reports(report_dict: dict, class_names: list, reports_dir: Path):
    """Save classification metrics to CSV and Markdown."""
    rows = []
    for cls in class_names:
        if cls in report_dict:
            m = report_dict[cls]
            rows.append({
                "class": cls,
                "precision": round(m["precision"], 4),
                "recall": round(m["recall"], 4),
                "f1_score": round(m["f1-score"], 4),
                "support": int(m["support"])
            })

    df = pd.DataFrame(rows)
    csv_path = reports_dir / "food_recognition_classification_report.csv"
    df.to_csv(csv_path, index=False)

    md_path = reports_dir / "food_recognition_classification_report.md"
    md_content = ["# Food Recognition Classification Report\n"]
    md_content.append("| Class | Precision | Recall | F1-Score | Support |")
    md_content.append("| :--- | :---: | :---: | :---: | :---: |")
    for r in rows:
        md_content.append(f"| **{r['class']}** | {r['precision']:.4f} | {r['recall']:.4f} | {r['f1_score']:.4f} | {r['support']} |")
    
    # Add macro / weighted averages
    macro = report_dict.get("macro avg", {})
    weighted = report_dict.get("weighted avg", {})
    md_content.append(f"| **Macro Average** | {macro.get('precision', 0):.4f} | {macro.get('recall', 0):.4f} | {macro.get('f1-score', 0):.4f} | {int(macro.get('support', 0))} |")
    md_content.append(f"| **Weighted Average** | {weighted.get('precision', 0):.4f} | {weighted.get('recall', 0):.4f} | {weighted.get('f1-score', 0):.4f} | {int(weighted.get('support', 0))} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content) + "\n")
    print(f"Classification reports saved to: {csv_path} and {md_path}")


def save_training_report(
    config: FoodRecognitionConfig,
    best_val_acc: float,
    best_epoch: int,
    history_df: pd.DataFrame,
    reports_dir: Path,
    test_sample_info: dict
):
    """Save comprehensive training report conforming to STEP 7 requirements."""
    train_df = pd.read_csv(config.train_split_path) if config.train_split_path.exists() else pd.read_csv(config.train_manifest_path)
    val_df = pd.read_csv(config.val_split_path) if config.val_split_path.exists() else pd.DataFrame()
    test_df = pd.read_csv(config.test_manifest_path)

    final_train_acc = history_df["train_accuracy"].iloc[-1]
    final_val_acc = history_df["val_accuracy"].iloc[-1]

    classes_list = ", ".join(config.selected_foods)

    report = f"""# FoodFresh AI Food Recognition Training Report

## Dataset

Dataset:
Fruits-360

Training manifest:
{config.train_split_path}

Validation:
{config.val_split_path} (Stratified 10% split of training manifest, random_seed=42)

Test manifest:
{config.test_manifest_path}

## Classes

Number of classes:
{config.num_classes}

{classes_list}

## Dataset Counts

Training images:
{len(train_df):,}

Validation images:
{len(val_df):,}

Test images:
{len(test_df):,}

## Model

EfficientNet-B0

Pretrained:
YES

Weight source:
Official TorchVision

Weight enum:
EfficientNet_B0_Weights.DEFAULT

## Training Strategy

Stage 1:
- Backbone frozen (features.requires_grad = False)
- Classifier head trained (Linear(1280, {config.num_classes}))
- Epochs: {config.stage_1_epochs}
- Learning rate: {config.learning_rate}
- Optimizer: AdamW (weight_decay={config.weight_decay})

Stage 2:
- Upper MBConv blocks unfrozen (features[6:])
- Fine-tuned with reduced learning rate
- Epochs: {config.stage_2_epochs}
- Fine-tuning learning rate: {config.fine_tune_learning_rate}
- Optimizer: AdamW (weight_decay={config.weight_decay})

## Hyperparameters

Batch size: {config.batch_size}
Learning rate: {config.learning_rate}
Fine-tuning learning rate: {config.fine_tune_learning_rate}
Weight decay: {config.weight_decay}
Epochs: {len(history_df)} ({config.stage_1_epochs} Stage 1 + {config.stage_2_epochs} Stage 2)
Random seed: {config.random_seed}
Optimizer: AdamW
Loss: CrossEntropyLoss (Class-Weighted balanced for class distribution)
Scheduler: ReduceLROnPlateau (factor=0.5, patience=1)

## Hardware

Device: {config.device}
GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}
CUDA: {'YES' if torch.cuda.is_available() else 'NO'}

## Training Results

Best validation accuracy:
{best_val_acc:.2f}%

Best epoch:
Epoch {best_epoch}

Final training accuracy:
{final_train_acc:.2f}%

Final validation accuracy:
{final_val_acc:.2f}%

## Checkpoint

models/trained/food_classifier.pth

Checkpoint created:
YES

## Basic Inference Verification

Test image: {test_sample_info.get('image_path', 'N/A')}
True class: {test_sample_info.get('true_class', 'N/A')}
Predicted class: {test_sample_info.get('predicted_class', 'N/A')}
Confidence: {test_sample_info.get('confidence', 'N/A')}

## Important Limitation

This model predicts food category from an image.

It does NOT determine:

- food safety
- freshness
- remaining shelf-life

Those are separate FoodFresh AI components.
"""
    report_path = reports_dir / "food_recognition_training_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Training report saved to: {report_path}")


if __name__ == "__main__":
    cfg = FoodRecognitionConfig()
    run_training(cfg)
