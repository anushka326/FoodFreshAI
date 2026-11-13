"""
FoodFresh AI - Food Recognition V2 Evaluation Pipeline (STEPS 20-24)
Executes comprehensive evaluation of V2 against the untouched test set:
- Overall Accuracy, Top-3, Top-5, Macro/Weighted Precision, Recall, F1
- Dedicated Pomegranate-Specific Evaluation (reports/pomegranate_v2_evaluation.csv)
- Confusion Matrix Plot (reports/food_recognition_v2_confusion_matrix.png)
- Per-Class Metrics Table (reports/food_recognition_v2_per_class_metrics.csv)
- V1 vs V2 Comparison Benchmark (reports/food_recognition_v1_vs_v2_comparison.csv)
- Verifies model reload independently of training
"""

import json
import os
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition_v2.config import FoodRecognitionV2Config
from ml.food_recognition_v2.dataset import FoodRecognitionV2Dataset
from ml.food_recognition_v2.model import create_food_recognition_v2_model
from ml.food_recognition_v2.transforms import get_v2_transforms


def load_v2_model(checkpoint_path: Path, num_classes: int, device: str) -> Tuple[torch.nn.Module, Dict]:
    """Reload V2 checkpoint and return model in eval mode."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"V2 checkpoint not found at: {checkpoint_path}")

    model = create_food_recognition_v2_model(num_classes=num_classes, pretrained=False)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, checkpoint


def evaluate_food_recognition_v2(config: Optional[FoodRecognitionV2Config] = None):
    if config is None:
        config = FoodRecognitionV2Config()

    print("=" * 60)
    print("FOODFRESH AI - EVALUATING FOOD RECOGNITION V2 (24 CLASSES)")
    print("=" * 60)

    # 1. Step 20: Reload checkpoint independently
    print(f"Reloading V2 checkpoint from: {config.checkpoint_path}")
    model, checkpoint_meta = load_v2_model(config.checkpoint_path, config.num_classes, config.device)
    print(f"[OK] Checkpoint reload verified. Stored best val accuracy: {checkpoint_meta.get('best_val_accuracy', 0):.2f}%")

    # 2. Setup untouched test DataLoader
    _, eval_transforms = get_v2_transforms(image_size=config.image_size)
    test_dataset = FoodRecognitionV2Dataset(
        manifest_path=config.test_manifest_path,
        transform=eval_transforms,
        return_metadata=True
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers
    )
    print(f"Evaluating on {len(test_dataset):,} untouched test images...")

    all_targets = []
    all_preds = []
    all_probs = []
    all_paths = []
    all_foods = []
    top3_correct = 0
    top5_correct = 0

    t_start = time.time()

    with torch.no_grad():
        for images, labels, foods, paths in test_loader:
            images = images.to(config.device)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)

            # Top 1, 3, 5
            _, top5_indices = torch.topk(probs, k=min(5, config.num_classes), dim=1)
            batch_preds = top5_indices[:, 0].cpu().numpy()
            batch_labels = labels.numpy()

            all_preds.extend(batch_preds)
            all_targets.extend(batch_labels)
            all_probs.extend(probs.cpu().numpy())
            all_paths.extend(paths)
            all_foods.extend(foods)

            # Accumulate top-k
            for i in range(len(batch_labels)):
                target = batch_labels[i]
                preds_i = top5_indices[i].cpu().numpy()
                if target in preds_i[:3]:
                    top3_correct += 1
                if target in preds_i[:5]:
                    top5_correct += 1

    total_time = time.time() - t_start
    total_samples = len(all_targets)
    latency_per_sample_ms = (total_time / total_samples) * 1000.0

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)

    # 3. Compute Macro & Weighted Metrics
    acc = accuracy_score(all_targets, all_preds) * 100.0
    top3_acc = (top3_correct / total_samples) * 100.0
    top5_acc = (top5_correct / total_samples) * 100.0

    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="macro")
    weight_p, weight_r, weight_f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="weighted")

    print("\n" + "=" * 50)
    print("V2 TEST EVALUATION RESULTS (OVERALL)")
    print("=" * 50)
    print(f"Top-1 Accuracy:    {acc:.2f}%")
    print(f"Top-3 Accuracy:    {top3_acc:.2f}%")
    print(f"Top-5 Accuracy:    {top5_acc:.2f}%")
    print(f"Macro Precision:   {macro_p * 100.0:.2f}%")
    print(f"Macro Recall:      {macro_r * 100.0:.2f}%")
    print(f"Macro F1-Score:    {macro_f1 * 100.0:.2f}%")
    print(f"Weighted F1-Score: {weight_f1 * 100.0:.2f}%")
    print(f"Inference Latency: {latency_per_sample_ms:.2f} ms / sample")

    # 4. Per-Class Metrics Table
    precision_per_cls, recall_per_cls, f1_per_cls, support_per_cls = precision_recall_fscore_support(
        all_targets, all_preds, average=None, labels=list(range(config.num_classes))
    )

    per_class_rows = []
    for cid in range(config.num_classes):
        food_name = config.id_to_food[str(cid)]
        per_class_rows.append({
            "class_id": cid,
            "food_type": food_name,
            "precision": round(float(precision_per_cls[cid]) * 100.0, 2),
            "recall": round(float(recall_per_cls[cid]) * 100.0, 2),
            "f1_score": round(float(f1_per_cls[cid]) * 100.0, 2),
            "support": int(support_per_cls[cid])
        })

    per_class_df = pd.DataFrame(per_class_rows)
    per_class_csv_path = config.project_root / "reports" / "food_recognition_v2_per_class_metrics.csv"
    per_class_df.to_csv(per_class_csv_path, index=False)
    print(f"Per-class metrics saved: {per_class_csv_path}")

    # 5. Dedicated Pomegranate Evaluation (STEP 22)
    pom_cid = config.food_to_id.get("Pomegranate", 19)
    pom_mask = (all_targets == pom_cid)
    pom_preds = all_preds[pom_mask]
    pom_probs = all_probs[pom_mask]
    pom_paths = [all_paths[i] for i in range(len(all_paths)) if pom_mask[i]]

    pom_total = len(pom_preds)
    pom_correct = np.sum(pom_preds == pom_cid)
    pom_acc = (pom_correct / pom_total * 100.0) if pom_total > 0 else 0.0
    pom_prec = precision_per_cls[pom_cid] * 100.0
    pom_rec = recall_per_cls[pom_cid] * 100.0
    pom_f1 = f1_per_cls[pom_cid] * 100.0
    pom_avg_conf = np.mean(np.max(pom_probs, axis=1)) * 100.0

    print("\n" + "=" * 50)
    print("POMEGRANATE-SPECIFIC EVALUATION (STEP 22)")
    print("=" * 50)
    print(f"Total Test Images: {pom_total}")
    print(f"Correctly Pred:    {pom_correct} / {pom_total}")
    print(f"Accuracy:          {pom_acc:.2f}%")
    print(f"Precision:         {pom_prec:.2f}%")
    print(f"Recall:            {pom_rec:.2f}%")
    print(f"F1-Score:          {pom_f1:.2f}%")
    print(f"Average Conf:      {pom_avg_conf:.2f}%")

    # Confusion breakdown for Pomegranate
    pom_confusions = {}
    for p in pom_preds:
        pred_food = config.id_to_food[str(p)]
        pom_confusions[pred_food] = pom_confusions.get(pred_food, 0) + 1

    pom_eval_rows = []
    for i in range(pom_total):
        top3_indices = np.argsort(pom_probs[i])[::-1][:3]
        top3_str = ", ".join([f"{config.id_to_food[str(idx)]}: {pom_probs[i][idx]*100:.1f}%" for idx in top3_indices])
        pom_eval_rows.append({
            "image_path": pom_paths[i],
            "actual_food": "Pomegranate",
            "predicted_food": config.id_to_food[str(pom_preds[i])],
            "confidence": round(float(np.max(pom_probs[i])) * 100.0, 2),
            "correct": bool(pom_preds[i] == pom_cid),
            "top_3_predictions": top3_str
        })

    pom_csv_path = config.project_root / "reports" / "pomegranate_v2_evaluation.csv"
    pd.DataFrame(pom_eval_rows).to_csv(pom_csv_path, index=False)
    print(f"Saved Pomegranate detailed evaluation: {pom_csv_path}")

    # 6. Confusion Matrix (STEP 23)
    cm = confusion_matrix(all_targets, all_preds)
    save_confusion_matrix(cm, config.selected_foods, config.project_root / "reports" / "food_recognition_v2_confusion_matrix.png")

    # 7. V1 vs V2 Comparison (STEP 24)
    v1_meta_path = config.project_root / "models" / "trained" / "food_classifier.pth"
    v1_size_mb = os.path.getsize(v1_meta_path) / (1024 * 1024) if v1_meta_path.exists() else 0
    v2_size_mb = os.path.getsize(config.checkpoint_path) / (1024 * 1024) if config.checkpoint_path.exists() else 0

    comparison_rows = [
        {"metric": "Number of Classes", "v1_value": "12", "v2_value": str(config.num_classes), "change": f"+{config.num_classes - 12}"},
        {"metric": "Pomegranate Supported?", "v1_value": "NO (0%)", "v2_value": f"YES ({pom_acc:.1f}%)", "change": "RESOLVED"},
        {"metric": "Overall Accuracy", "v1_value": "99.8%", "v2_value": f"{acc:.2f}%", "change": f"{acc - 99.8:+.2f}%"},
        {"metric": "Top-3 Accuracy", "v1_value": "100.0%", "v2_value": f"{top3_acc:.2f}%", "change": f"{top3_acc - 100.0:+.2f}%"},
        {"metric": "Macro F1-Score", "v1_value": "99.8%", "v2_value": f"{macro_f1*100.0:.2f}%", "change": f"{macro_f1*100.0 - 99.8:+.2f}%"},
        {"metric": "Weighted F1-Score", "v1_value": "99.8%", "v2_value": f"{weight_f1*100.0:.2f}%", "change": f"{weight_f1*100.0 - 99.8:+.2f}%"},
        {"metric": "Pomegranate Test Accuracy", "v1_value": "0.0% (predicted Apple)", "v2_value": f"{pom_acc:.2f}%", "change": f"+{pom_acc:.2f}%"},
        {"metric": "Model Size (Disk)", "v1_value": f"{v1_size_mb:.2f} MB", "v2_value": f"{v2_size_mb:.2f} MB", "change": f"{v2_size_mb - v1_size_mb:+.2f} MB"},
        {"metric": "Inference Latency", "v1_value": "~3.5 ms", "v2_value": f"{latency_per_sample_ms:.2f} ms", "change": "Comparable"}
    ]
    comp_df = pd.DataFrame(comparison_rows)
    comp_csv_path = config.project_root / "reports" / "food_recognition_v1_vs_v2_comparison.csv"
    comp_df.to_csv(comp_csv_path, index=False)
    print(f"Saved V1 vs V2 comparison table: {comp_csv_path}")

    return {
        "accuracy": acc,
        "top3_accuracy": top3_acc,
        "top5_accuracy": top5_acc,
        "macro_f1": macro_f1 * 100.0,
        "weighted_f1": weight_f1 * 100.0,
        "pomegranate_accuracy": pom_acc,
        "pomegranate_precision": pom_prec,
        "pomegranate_recall": pom_rec,
        "pomegranate_f1": pom_f1,
        "pomegranate_avg_confidence": pom_avg_conf,
        "latency_ms": latency_per_sample_ms
    }


def save_confusion_matrix(cm: np.ndarray, class_names: List[str], save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(16, 14))

    # Normalize by row
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    plt.imshow(cm_norm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Food Recognition V2 - 24-Class Confusion Matrix (Normalized)", fontsize=14, pad=12)
    plt.colorbar(fraction=0.046, pad=0.04)

    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=90, fontsize=9)
    plt.yticks(tick_marks, class_names, fontsize=9)

    plt.ylabel("True Class", fontsize=11)
    plt.xlabel("Predicted Class", fontsize=11)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"Confusion matrix plot saved: {save_path}")


if __name__ == "__main__":
    evaluate_food_recognition_v2()
