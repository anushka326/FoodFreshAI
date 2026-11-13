"""Train an experimental image-to-shelf-life-interval classifier on AgriFreshNET.

Targets are the intervals explicitly encoded in the original folder labels. No
midpoints, storage conditions, or per-image elapsed-days values are fabricated.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ml.freshness.model import create_freshness_model
DATA = ROOT / "data" / "processed" / "agrifreshnet"
SOURCE_CHECKPOINT = ROOT / "models" / "candidates" / "freshness_v3_efficientnet_b0.pth"
OUT = ROOT / "models" / "candidates" / "shelf_life_interval_efficientnet_b0.pth"
REPORT = ROOT / "reports"
FOODS = ["Banana", "Bittermelon", "Cucumber", "Eggplant", "Orange", "Papaya", "Pineapple", "Tomato"]
STAGES = ["Fresh", "Semi-Fresh", "Rotten"]
RANGES = {
    "Banana": [(1, 4), (4, 7), (7, 13)], "Bittermelon": [(1, 3), (3, 5), (5, 8)],
    "Cucumber": [(1, 6), (6, 12), (12, 20)], "Eggplant": [(1, 4), (4, 8), (8, 15)],
    "Orange": [(1, 9), (9, 20), (20, 35)], "Papaya": [(1, 4), (4, 7), (7, 12)],
    "Pineapple": [(1, 15), (15, 25), (25, 35)], "Tomato": [(1, 10), (10, 24), (24, 35)],
}
NAMES = [f"{food} | {stage} | {RANGES[food][s][0]}-{RANGES[food][s][1]} days"
         for food in FOODS for s, stage in enumerate(STAGES)]


class IntervalDataset(Dataset):
    def __init__(self, manifest: Path, train: bool):
        self.rows = pd.read_csv(manifest)
        self.food_ids = {name: i for i, name in enumerate(FOODS)}
        self.stage_ids = {name: i for i, name in enumerate(STAGES)}
        aug = [transforms.RandomHorizontalFlip(), transforms.RandomRotation(12)] if train else []
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)), *aug, transforms.ToTensor(),
            transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
        ])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        row = self.rows.iloc[i]
        path = Path(row.image_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        image = Image.open(path).convert("RGB")
        target = self.food_ids[row.food_type] * len(STAGES) + self.stage_ids[row.freshness_label]
        return self.transform(image), target


def main():
    if not SOURCE_CHECKPOINT.is_file():
        raise FileNotFoundError(f"Freshness V3 source checkpoint missing: {SOURCE_CHECKPOINT}")
    random.seed(42); np.random.seed(42); torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = IntervalDataset(DATA / "freshness_train_manifest.csv", True)
    val_ds = IntervalDataset(DATA / "freshness_val_manifest.csv", False)
    test_ds = IntervalDataset(DATA / "freshness_test_manifest.csv", False)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0, pin_memory=device.type == "cuda")
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, num_workers=0)

    model = create_freshness_model(num_classes=3, pretrained=False)
    model.load_state_dict(torch.load(SOURCE_CHECKPOINT, map_location="cpu", weights_only=True))
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(NAMES))
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    best = -1.0; best_epoch = 0; stale = 0; history = []
    started = time.time()
    for epoch in range(1, 9):
        model.train(); losses = []
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(images), labels)
            loss.backward(); optimizer.step(); losses.append(float(loss.item()))
        model.eval(); pred = []; truth = []
        with torch.no_grad():
            for images, labels in val_loader:
                pred.extend(model(images.to(device)).argmax(1).cpu().tolist())
                truth.extend(labels.tolist())
        val_acc = accuracy_score(truth, pred)
        history.append({"epoch": epoch, "train_loss": float(np.mean(losses)), "val_accuracy": float(val_acc)})
        print(f"epoch {epoch}/8 train_loss={history[-1]['train_loss']:.4f} val_interval_accuracy={val_acc:.4f}", flush=True)
        if val_acc > best:
            best, best_epoch, stale = val_acc, epoch, 0
            torch.save({"state_dict": model.cpu().state_dict(), "classes": NAMES,
                        "source_checkpoint": str(SOURCE_CHECKPOINT.relative_to(ROOT)),
                        "target": "food x freshness interval class", "best_epoch": epoch}, OUT)
            model.to(device)
        else:
            stale += 1
            if stale >= 3: break

    saved = torch.load(OUT, map_location="cpu", weights_only=False)
    model.cpu().load_state_dict(saved["state_dict"]); model.to(device).eval()
    pred = []; truth = []
    with torch.no_grad():
        for images, labels in test_loader:
            pred.extend(model(images.to(device)).argmax(1).cpu().tolist())
            truth.extend(labels.tolist())
    metrics = classification_report(truth, pred, labels=list(range(len(NAMES))), target_names=NAMES,
                                   output_dict=True, zero_division=0)
    cm = confusion_matrix(truth, pred, labels=list(range(len(NAMES))))
    result = {
        "candidate": str(OUT.relative_to(ROOT)), "architecture": "EfficientNet-B0 initialized from Freshness V3",
        "target_representation": "24 categorical intervals, food x freshness stage; interval endpoints preserved",
        "inputs": "RGB image only; dataset split manifests", "storage_metadata": "not present",
        "train_samples": len(train_ds), "validation_samples": len(val_ds), "test_samples": len(test_ds),
        "best_epoch": best_epoch, "best_validation_accuracy": best,
        "test_interval_accuracy": accuracy_score(truth, pred),
        "test_macro_f1": metrics["macro avg"]["f1-score"], "per_class": metrics,
        "confusion_matrix": cm.tolist(), "device": str(device), "elapsed_seconds": time.time() - started,
        "ranges": {food: {stage: list(RANGES[food][i]) for i, stage in enumerate(STAGES)} for food in FOODS},
        "limitations": "Targets are taxonomy-level intervals, not observed remaining-life measurements; no storage or age covariates.",
    }
    REPORT.mkdir(exist_ok=True)
    (REPORT / "shelf_life_interval_training_metrics.json").write_text(json.dumps({"history": history, "result": result}, indent=2), encoding="utf-8")
    print(f"test_interval_accuracy={result['test_interval_accuracy']:.4f} macro_f1={result['test_macro_f1']:.4f}", flush=True)
    print("checkpoint=" + str(OUT), flush=True)


if __name__ == "__main__":
    main()
