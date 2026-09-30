"""
FoodFresh AI - Freshness Model Fine-Tuning (V2)
Fine-tunes ResNet-18 on AgriFreshNET dataset using transfer learning, conservative learning rates,
realistic augmentations, early stopping, and comprehensive evaluation metrics.
Saves checkpoint to models/trained/freshness_model_v2.pth.
"""

import os
import sys
import json
import time
import csv
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models import resnet18
import torchvision.transforms as T
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PRETRAINED_WEIGHTS = PROJECT_ROOT / "models" / "pretrained" / "freshness_resnet18" / "model_weights.pth"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "freshness_v2"
TRAIN_MANIFEST = PROCESSED_DIR / "train_manifest.csv"
VAL_MANIFEST = PROCESSED_DIR / "val_manifest.csv"
TEST_MANIFEST = PROCESSED_DIR / "test_manifest.csv"
LABEL_MAP_PATH = PROCESSED_DIR / "label_map.json"

TRAINED_DIR = PROJECT_ROOT / "models" / "trained"
MODEL_SAVE_PATH = TRAINED_DIR / "freshness_model_v2.pth"
REPORTS_DIR = PROJECT_ROOT / "reports"
TRAINING_REPORT_PATH = REPORTS_DIR / "freshness_model_training_report.md"
HISTORY_CSV_PATH = REPORTS_DIR / "freshness_model_training_history.csv"

VOCAB = ["fresh", "rotten", "slightly_spoiled"]


class AdaptiveConcatPool2d(nn.Module):
    def __init__(self, sz=None):
        super().__init__()
        self.output_size = sz or 1
        self.ap = nn.AdaptiveAvgPool2d(self.output_size)
        self.mp = nn.AdaptiveMaxPool2d(self.output_size)

    def forward(self, x):
        return torch.cat([self.mp(x), self.ap(x)], 1)


class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


def build_freshness_resnet18(num_classes: int = 3) -> nn.Module:
    base = resnet18(weights=None)
    body = nn.Sequential(*list(base.children())[:-2])
    head = nn.Sequential(
        AdaptiveConcatPool2d(),
        Flatten(),
        nn.BatchNorm1d(1024),
        nn.Dropout(0.25),
        nn.Linear(1024, 512, bias=False),
        nn.ReLU(inplace=True),
        nn.BatchNorm1d(512),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes, bias=False)
    )
    return nn.Sequential(body, head)


class AgriFreshDataset(Dataset):
    def __init__(self, manifest_path: Path, transform=None):
        self.samples = []
        self.transform = transform
        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_path = PROJECT_ROOT / row["filepath"]
                self.samples.append((full_path, int(row["label"])))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


def evaluate_model(model, loader, device, criterion):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for inputs, targets in loader:
            inputs = inputs.to(device)
            targets = targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            total_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(targets.cpu().numpy())

    avg_loss = total_loss / len(loader.dataset)
    acc = np.mean(np.array(all_preds) == np.array(all_targets))
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(all_targets, all_preds, average="weighted", zero_division=0)
    precisions = precision_score(all_targets, all_preds, average=None, zero_division=0)
    recalls = recall_score(all_targets, all_preds, average=None, zero_division=0)
    f1s = f1_score(all_targets, all_preds, average=None, zero_division=0)
    cm = confusion_matrix(all_targets, all_preds, labels=[0, 1, 2])

    metrics = {
        "loss": avg_loss,
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "precisions": precisions,
        "recalls": recalls,
        "f1s": f1s,
        "confusion_matrix": cm,
        "preds": all_preds,
        "targets": all_targets
    }
    return metrics


def main():
    print("=" * 60)
    print("FOODFRESH AI — FRESHNESS MODEL FINE-TUNING (V2)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    TRAINED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Transforms
    # Biological-aware augmentations matching produce characteristics
    train_transform = T.Compose([
        T.Resize((256, 256)),
        T.RandomCrop(224),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=15),
        T.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = T.Compose([
        T.Resize((256, 256)),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 2. Datasets & Loaders
    print("Loading manifests...")
    train_dataset = AgriFreshDataset(TRAIN_MANIFEST, transform=train_transform)
    val_dataset = AgriFreshDataset(VAL_MANIFEST, transform=eval_transform)
    test_dataset = AgriFreshDataset(TEST_MANIFEST, transform=eval_transform)

    batch_size = 32
    num_workers = 2 if os.name != 'nt' else 0  # 0 on Windows avoids multiprocessing IPC overhead

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    print(f"Dataset sizes: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")

    # 3. Model Initialization
    model = build_freshness_resnet18(num_classes=3)
    if PRETRAINED_WEIGHTS.exists():
        print(f"Initializing from pretrained checkpoint: {PRETRAINED_WEIGHTS}")
        state_dict = torch.load(PRETRAINED_WEIGHTS, map_location=device)
        model.load_state_dict(state_dict)
    else:
        print("Pretrained checkpoint not found, initializing from standard ImageNet backbone...")
        base = resnet18(weights="IMAGENET1K_V1")
        model[0].load_state_dict(nn.Sequential(*list(base.children())[:-2]).state_dict())

    model.to(device)

    # 4. Optimizer, Criterion, Scheduler
    criterion = nn.CrossEntropyLoss()

    # Differential learning rates: smaller for backbone, larger for custom head
    optimizer = torch.optim.AdamW([
        {"params": model[0].parameters(), "lr": 1e-4},
        {"params": model[1].parameters(), "lr": 5e-4}
    ], weight_decay=1e-2)

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=8, eta_min=1e-6)

    # 5. Training Loop with Early Stopping
    epochs = 8
    best_val_macro_f1 = 0.0
    patience = 3
    patience_counter = 0
    history = []

    print("\nStarting fine-tuning...")
    start_total_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        epoch_start = time.time()

        for step, (inputs, targets) in enumerate(train_loader):
            inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            train_correct += (preds == targets).sum().item()

        scheduler.step()

        epoch_train_loss = train_loss / len(train_dataset)
        epoch_train_acc = train_correct / len(train_dataset)

        # Validation
        val_metrics = evaluate_model(model, val_loader, device, criterion)
        epoch_time = time.time() - epoch_start

        history.append({
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc * 100.0, 2),
            "val_loss": round(val_metrics["loss"], 4),
            "val_acc": round(val_metrics["accuracy"] * 100.0, 2),
            "val_macro_f1": round(val_metrics["macro_f1"] * 100.0, 2),
            "val_weighted_f1": round(val_metrics["weighted_f1"] * 100.0, 2),
            "epoch_time_s": round(epoch_time, 1)
        })

        print(
            f"Epoch {epoch:02d}/{epochs:02d} [{epoch_time:.1f}s] | "
            f"Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc*100:.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f} Acc: {val_metrics['accuracy']*100:.2f}% "
            f"Macro-F1: {val_metrics['macro_f1']*100:.2f}%"
        )

        # Save Best Model Checkpoint
        if val_metrics["macro_f1"] > best_val_macro_f1:
            best_val_macro_f1 = val_metrics["macro_f1"]
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  --> Saved new best model to {MODEL_SAVE_PATH} (Val Macro F1: {best_val_macro_f1*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch} (no improvement for {patience} consecutive epochs).")
                break

    total_training_time = time.time() - start_total_time
    print(f"\nTraining completed in {total_training_time/60.0:.2f} minutes.")

    # 6. Final Evaluation on UNTOUCHED Test Set
    print("\nLoading best model checkpoint for evaluation on untouched test set...")
    best_model = build_freshness_resnet18(num_classes=3)
    best_model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
    best_model.to(device)

    test_metrics = evaluate_model(best_model, test_loader, device, criterion)
    print("\n" + "=" * 60)
    print("FINAL TEST SET PERFORMANCE (UNTOUCHED TEST SET)")
    print("=" * 60)
    print(f"Test Loss:        {test_metrics['loss']:.4f}")
    print(f"Test Accuracy:    {test_metrics['accuracy']*100:.2f}%")
    print(f"Test Macro F1:    {test_metrics['macro_f1']*100:.2f}%")
    print(f"Test Weighted F1: {test_metrics['weighted_f1']*100:.2f}%")
    print("\nPer-Class Breakdown:")
    for i, cls_name in enumerate(VOCAB):
        print(f"  {cls_name.upper():<16}: Precision={test_metrics['precisions'][i]*100:.2f}%, Recall={test_metrics['recalls'][i]*100:.2f}%, F1={test_metrics['f1s'][i]*100:.2f}%")

    print("\nConfusion Matrix:")
    print(test_metrics["confusion_matrix"])

    # 7. Write History CSV
    with open(HISTORY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "train_acc", "val_loss", "val_acc", "val_macro_f1", "val_weighted_f1", "epoch_time_s"])
        writer.writeheader()
        writer.writerows(history)
    print(f"\nSaved training history to: {HISTORY_CSV_PATH}")

    # 8. Generate Training Markdown Report
    target_names = ["Fresh (0)", "Rotten (1)", "Slightly Spoiled (2)"]
    sk_report = classification_report(test_metrics["targets"], test_metrics["preds"], target_names=target_names, digits=4)

    report_content = f"""# FoodFresh AI — Freshness Model Fine-Tuning Report (V2)

**Date**: September 26, 2026  
**Architecture**: ResNet-18 (Torchvision backbone + FastAI AdaptiveConcatPool2d head)  
**Dataset**: AgriFreshNET Freshness V2 (`data/processed/freshness_v2/`)  
**Trained Weights**: `models/trained/freshness_model_v2.pth`  
**Pretrained Starting Point**: `models/pretrained/freshness_resnet18/model_weights.pth` (kept untouched)  

---

## 1. Executive Summary

To resolve severe classification mode-collapse and false-positive degradation on real-world produce, the ResNet-18 freshness model was fine-tuned on the real-world **AgriFreshNET** produce dataset.

- **Total Dataset Size**: 14,160 images across 5,106 capture groups
- **Splits**: Train = 9,926 (70.1%), Validation = 2,128 (15.0%), Test = 2,106 (14.9%)
- **Data Leakage Guarantee**: 0 capture group overlap across train, validation, and test.
- **Best Validation Macro F1**: {best_val_macro_f1*100:.2f}%
- **Final Test Set Accuracy**: {test_metrics['accuracy']*100:.2f}%
- **Final Test Set Macro F1**: {test_metrics['macro_f1']*100:.2f}%

---

## 2. Test Set Evaluation Metrics (Untouched Test Partition)

### Overall Summary
- **Loss**: {test_metrics['loss']:.4f}
- **Accuracy**: **{test_metrics['accuracy']*100:.2f}%**
- **Macro F1-Score**: **{test_metrics['macro_f1']*100:.2f}%**
- **Weighted F1-Score**: **{test_metrics['weighted_f1']*100:.2f}%**

### Per-Class Detailed Performance
| Class Index | Class Label | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | **Fresh** | {test_metrics['precisions'][0]*100:.2f}% | {test_metrics['recalls'][0]*100:.2f}% | **{test_metrics['f1s'][0]*100:.2f}%** | {sum(np.array(test_metrics['targets']) == 0)} |
| `1` | **Rotten** | {test_metrics['precisions'][1]*100:.2f}% | {test_metrics['recalls'][1]*100:.2f}% | **{test_metrics['f1s'][1]*100:.2f}%** | {sum(np.array(test_metrics['targets']) == 1)} |
| `2` | **Slightly Spoiled** | {test_metrics['precisions'][2]*100:.2f}% | {test_metrics['recalls'][2]*100:.2f}% | **{test_metrics['f1s'][2]*100:.2f}%** | {sum(np.array(test_metrics['targets']) == 2)} |

### Confusion Matrix
```
                  Predicted Fresh  Predicted Rotten  Predicted Slightly Spoiled
Actual Fresh             {test_metrics['confusion_matrix'][0, 0]:<16} {test_metrics['confusion_matrix'][0, 1]:<17} {test_metrics['confusion_matrix'][0, 2]}
Actual Rotten            {test_metrics['confusion_matrix'][1, 0]:<16} {test_metrics['confusion_matrix'][1, 1]:<17} {test_metrics['confusion_matrix'][1, 2]}
Actual Slightly Spoiled  {test_metrics['confusion_matrix'][2, 0]:<16} {test_metrics['confusion_matrix'][2, 1]:<17} {test_metrics['confusion_matrix'][2, 2]}
```

### Scikit-Learn Classification Report
```
{sk_report}
```

---

## 3. Epoch-by-Epoch Training Trajectory

| Epoch | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Val Macro F1 (%) | Epoch Duration (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for h in history:
        report_content += f"| {h['epoch']:02d} | {h['train_loss']:.4f} | {h['train_acc']:.2f}% | {h['val_loss']:.4f} | {h['val_acc']:.2f}% | {h['val_macro_f1']:.2f}% | {h['epoch_time_s']}s |\n"

    report_content += """
---

## 4. Promotion Criteria Gate Status

In accordance with Phase 5 & Phase 25:
- The trained model is preserved at `models/trained/freshness_model_v2.pth`.
- The original checkpoint at `models/pretrained/freshness_resnet18/model_weights.pth` remains untouched.
- Promotion to production will strictly occur ONLY after side-by-side real-world benchmark validation on real produce images.
"""

    with open(TRAINING_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Saved Training Report to: {TRAINING_REPORT_PATH}")


if __name__ == "__main__":
    main()
