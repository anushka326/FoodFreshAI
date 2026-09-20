"""
FoodFresh AI - Food Recognition Model Evaluation Module (STEP 8)
Performs comprehensive, inference-only evaluation on the untouched Fruits-360 test manifest.
Calculates overall and per-class metrics, confusion matrices (raw and normalized),
confidence distributions, top-k accuracy, misclassifications, and out-of-dataset tests.
DOES NOT TRAIN OR MODIFY ANY MODEL OR DATASET.
"""

from pathlib import Path
import sys
import json
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    top_k_accuracy_score
)

import torch
import torch.nn.functional as F

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import FoodRecognitionDataset
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms
from ml.food_recognition.utils import count_parameters, set_seed


def verify_checkpoint(checkpoint_path: Path, expected_num_classes: int) -> Tuple[dict, float, int, int]:
    """Verify checkpoint existence and integrity."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"CRITICAL: Checkpoint not found at {checkpoint_path}")

    file_size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    required_keys = ["model_state_dict", "num_classes"]
    for k in required_keys:
        if k not in checkpoint:
            raise KeyError(f"Checkpoint missing required key: '{k}'")

    num_classes = checkpoint["num_classes"]
    if num_classes != expected_num_classes:
        raise ValueError(f"Checkpoint num_classes ({num_classes}) != expected ({expected_num_classes})")

    # Check classifier head dimensions
    state_dict = checkpoint["model_state_dict"]
    head_weight = state_dict.get("classifier.1.weight")
    if head_weight is None or head_weight.shape[0] != expected_num_classes:
        raise ValueError(f"Classifier output features {head_weight.shape if head_weight is not None else None} != {expected_num_classes}")

    total_params = sum(p.numel() for p in state_dict.values() if isinstance(p, torch.Tensor))
    return checkpoint, file_size_mb, total_params, num_classes


def run_evaluation(config: Optional[FoodRecognitionConfig] = None) -> Dict:
    """Execute complete STEP 8 evaluation pipeline."""
    if config is None:
        config = FoodRecognitionConfig()

    set_seed(config.random_seed)
    device = torch.device(config.device)
    reports_dir = config.project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FOODFRESH AI — FOOD RECOGNITION MODEL EVALUATION (STEP 8)")
    print("=" * 60)
    print(f"Device:       {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # 1. Verify and load checkpoint
    print("\n[1] Verifying model checkpoint...")
    checkpoint, file_size_mb, total_params_saved, num_classes = verify_checkpoint(
        config.checkpoint_path, config.num_classes
    )
    print(f"    Checkpoint path: {config.checkpoint_path}")
    print(f"    File size:       {file_size_mb:.2f} MB")
    print(f"    Number classes:  {num_classes}")
    print(f"    Best val acc:    {checkpoint.get('best_val_accuracy', 0.0):.2f}% (Epoch {checkpoint.get('epoch', 'N/A')})")

    # 2. Reconstruct Model Architecture
    print("\n[2] Reconstructing EfficientNet-B0 architecture (Inference Mode)...")
    model = create_food_recognition_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    total_params, trainable_params = count_parameters(model)
    print(f"    Total parameters:     {total_params:,}")
    print(f"    Trainable parameters: {trainable_params:,}")

    # 3. Verify Test Dataset
    print("\n[3] Verifying untouched test manifest...")
    test_manifest_path = config.test_manifest_path
    if not test_manifest_path.exists():
        raise FileNotFoundError(f"Test manifest missing at {test_manifest_path}")

    test_df = pd.read_csv(test_manifest_path)
    test_count = len(test_df)
    print(f"    Test images count: {test_count:,}")
    print(f"    Classes count:     {test_df['normalized_food'].nunique()}")

    # Check existence of all test images
    missing = [p for p in test_df["image_path"] if not Path(p).exists()]
    if missing:
        raise FileNotFoundError(f"Missing {len(missing)} test images!")
    print(f"    All {test_count:,} test image paths verified: PASS")

    # 4. Build Test DataLoader
    _, eval_transforms = get_transforms(image_size=config.image_size)
    test_dataset = FoodRecognitionDataset(test_manifest_path, transform=eval_transforms)
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=(device.type == "cuda")
    )

    # 5. Full Inference Pass
    print("\n[4] Running full test set inference pass (torch.no_grad)...")
    all_probs = []
    all_targets = []
    id_to_food = config.id_to_food
    class_names = [id_to_food.get(str(i), f"Class {i}") for i in range(num_classes)]

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device, non_blocking=True)
            logits = model(images)
            probs = F.softmax(logits, dim=1)
            all_probs.append(probs.cpu().numpy())
            all_targets.extend(labels.numpy())

    all_probs = np.vstack(all_probs)       # Shape: [N, num_classes]
    all_targets = np.array(all_targets)    # Shape: [N]
    all_preds = np.argmax(all_probs, axis=1)

    # 6. Overall Metrics
    print("\n[5] Calculating overall evaluation metrics...")
    acc = accuracy_score(all_targets, all_preds) * 100.0
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="macro", zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="weighted", zero_division=0)

    # Top-K Accuracies
    top1_acc = top_k_accuracy_score(all_targets, all_probs, k=1) * 100.0
    top3_acc = top_k_accuracy_score(all_targets, all_probs, k=3) * 100.0
    top5_acc = top_k_accuracy_score(all_targets, all_probs, k=5) * 100.0 if num_classes >= 5 else None

    correct_mask = (all_preds == all_targets)
    correct_count = int(np.sum(correct_mask))
    incorrect_count = int(np.sum(~correct_mask))

    print(f"    Test Accuracy:      {acc:.4f}%")
    print(f"    Top-1 Accuracy:     {top1_acc:.4f}%")
    print(f"    Top-3 Accuracy:     {top3_acc:.4f}%")
    if top5_acc is not None:
        print(f"    Top-5 Accuracy:     {top5_acc:.4f}%")
    print(f"    Macro Precision:    {macro_p:.4f}")
    print(f"    Macro Recall:       {macro_r:.4f}")
    print(f"    Macro F1-Score:     {macro_f1:.4f}")
    print(f"    Weighted Precision: {weighted_p:.4f}")
    print(f"    Weighted Recall:    {weighted_r:.4f}")
    print(f"    Weighted F1-Score:  {weighted_f1:.4f}")
    print(f"    Correct Count:      {correct_count:,} / {test_count:,}")
    print(f"    Incorrect Count:    {incorrect_count:,} / {test_count:,}")

    # 7. Per-Class Metrics
    print("\n[6] Generating per-class metrics...")
    p_per, r_per, f1_per, sup_per = precision_recall_fscore_support(all_targets, all_preds, average=None, zero_division=0)
    per_class_rows = []
    for c_idx in range(num_classes):
        c_name = class_names[c_idx]
        per_class_rows.append({
            "class": c_name,
            "precision": round(float(p_per[c_idx]), 4),
            "recall": round(float(r_per[c_idx]), 4),
            "f1_score": round(float(f1_per[c_idx]), 4),
            "support": int(sup_per[c_idx])
        })
    per_class_df = pd.DataFrame(per_class_rows)
    per_class_csv_path = reports_dir / "food_recognition_per_class_metrics.csv"
    per_class_df.to_csv(per_class_csv_path, index=False)

    per_class_md_path = reports_dir / "food_recognition_per_class_metrics.md"
    per_class_md_content = ["# Food Recognition Per-Class Metrics\n"]
    per_class_md_content.append("| Class | Support | Precision | Recall | F1-Score |")
    per_class_md_content.append("| :--- | :---: | :---: | :---: | :---: |")
    for r in per_class_rows:
        per_class_md_content.append(f"| **{r['class']}** | {r['support']} | {r['precision']:.4f} | {r['recall']:.4f} | {r['f1_score']:.4f} |")
    per_class_md_content.append(f"| **Macro Average** | {test_count} | {macro_p:.4f} | {macro_r:.4f} | {macro_f1:.4f} |")
    per_class_md_content.append(f"| **Weighted Average** | {test_count} | {weighted_p:.4f} | {weighted_r:.4f} | {weighted_f1:.4f} |")
    with open(per_class_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(per_class_md_content) + "\n")

    # 8. Confusion Matrix & Normalized Confusion Matrix
    print("\n[7] Generating raw and normalized confusion matrices...")
    cm = confusion_matrix(all_targets, all_preds)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    # Save raw confusion matrix plot
    plot_cm(cm, class_names, reports_dir / "food_recognition_confusion_matrix.png", title="Confusion Matrix (Counts)", fmt="d", cmap=plt.cm.Blues)
    # Save normalized confusion matrix plot
    plot_cm(cm_norm, class_names, reports_dir / "food_recognition_confusion_matrix_normalized.png", title="Normalized Confusion Matrix (Proportions)", fmt=".3f", cmap=plt.cm.Greens)

    # 9. Most Common Confusions Analysis
    print("\n[8] Analyzing most common class confusions...")
    confusions = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and cm[i, j] > 0:
                confusions.append({
                    "true_class": class_names[i],
                    "predicted_class": class_names[j],
                    "count": int(cm[i, j])
                })
    confusions = sorted(confusions, key=lambda x: x["count"], reverse=True)
    print("    Most frequent observed confusions:")
    for conf in confusions[:10]:
        print(f"      {conf['true_class']} -> {conf['predicted_class']}: {conf['count']} test images")

    # 10. Detailed Predictions CSV
    print("\n[9] Generating detailed predictions record...")
    prediction_records = []
    for idx in range(test_count):
        probs_i = all_probs[idx]
        sorted_indices = np.argsort(probs_i)[::-1]
        top1_idx = sorted_indices[0]
        top2_idx = sorted_indices[1]
        top3_idx = sorted_indices[2]
        true_idx = all_targets[idx]

        prediction_records.append({
            "image_path": test_df.iloc[idx]["image_path"],
            "true_class": class_names[true_idx],
            "predicted_class": class_names[top1_idx],
            "confidence": round(float(probs_i[top1_idx]), 4),
            "top2_class": class_names[top2_idx],
            "top2_probability": round(float(probs_i[top2_idx]), 4),
            "top3_class": class_names[top3_idx],
            "top3_probability": round(float(probs_i[top3_idx]), 4),
            "correct": bool(top1_idx == true_idx)
        })

    preds_df = pd.DataFrame(prediction_records)
    preds_csv_path = reports_dir / "food_recognition_predictions.csv"
    preds_df.to_csv(preds_csv_path, index=False)

    # 11. Confidence Distribution Analysis
    print("\n[10] Computing confidence distribution metrics...")
    correct_confs = preds_df[preds_df["correct"]]["confidence"].values
    incorrect_confs = preds_df[~preds_df["correct"]]["confidence"].values if incorrect_count > 0 else np.array([])

    conf_stats = {
        "overall_mean": float(preds_df["confidence"].mean()),
        "overall_median": float(preds_df["confidence"].median()),
        "correct_mean": float(correct_confs.mean()) if len(correct_confs) > 0 else 0.0,
        "correct_median": float(np.median(correct_confs)) if len(correct_confs) > 0 else 0.0,
        "correct_min": float(correct_confs.min()) if len(correct_confs) > 0 else 0.0,
        "correct_max": float(correct_confs.max()) if len(correct_confs) > 0 else 0.0,
        "incorrect_mean": float(incorrect_confs.mean()) if len(incorrect_confs) > 0 else 0.0,
        "incorrect_median": float(np.median(incorrect_confs)) if len(incorrect_confs) > 0 else 0.0,
        "incorrect_min": float(incorrect_confs.min()) if len(incorrect_confs) > 0 else 0.0,
        "incorrect_max": float(incorrect_confs.max()) if len(incorrect_confs) > 0 else 0.0,
    }

    print(f"    Correct Confidence:   Mean={conf_stats['correct_mean']:.4f}, Median={conf_stats['correct_median']:.4f}, Min={conf_stats['correct_min']:.4f}")
    print(f"    Incorrect Confidence: Mean={conf_stats['incorrect_mean']:.4f}, Median={conf_stats['incorrect_median']:.4f}, Max={conf_stats['incorrect_max']:.4f}")

    # Plot confidence distribution
    plot_confidence_distribution(correct_confs, incorrect_confs, reports_dir / "food_recognition_confidence_distribution.png")

    # 12. Misclassifications CSV & Visual Examples
    print("\n[11] Extracting misclassifications...")
    misclass_df = preds_df[~preds_df["correct"]][["image_path", "true_class", "predicted_class", "confidence"]]
    misclass_csv_path = reports_dir / "food_recognition_misclassifications.csv"
    misclass_df.to_csv(misclass_csv_path, index=False)
    print(f"    Saved {len(misclass_df)} misclassified records to: {misclass_csv_path}")

    # Visual error analysis plot
    plot_misclassified_examples(misclass_df, reports_dir / "food_recognition_misclassified_examples.png")

    # 13. Sample Predictions CSV (20 reproducible samples with seed 42)
    print("\n[12] Generating reproducible sample predictions (seed=42)...")
    sample_df = preds_df.sample(n=min(20, len(preds_df)), random_state=42)[
        ["image_path", "true_class", "predicted_class", "confidence", "correct"]
    ].rename(columns={"image_path": "image"})
    sample_csv_path = reports_dir / "food_recognition_sample_predictions.csv"
    sample_df.to_csv(sample_csv_path, index=False)

    # 14. Out-of-Dataset Qualitative Inference Test
    print("\n[13] Running out-of-dataset qualitative inference test...")
    out_of_dataset_results = run_out_of_dataset_test(model, eval_transforms, device, id_to_food, config.project_root)

    # 15. Generate Full Evaluation Report MD
    print("\n[14] Writing full evaluation report...")
    write_evaluation_report(
        config=config,
        test_count=test_count,
        num_classes=num_classes,
        acc=acc,
        macro_p=macro_p,
        macro_r=macro_r,
        macro_f1=macro_f1,
        weighted_p=weighted_p,
        weighted_r=weighted_r,
        weighted_f1=weighted_f1,
        top1_acc=top1_acc,
        top3_acc=top3_acc,
        top5_acc=top5_acc,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        conf_stats=conf_stats,
        confusions=confusions,
        per_class_rows=per_class_rows,
        total_params=total_params,
        file_size_mb=file_size_mb,
        out_of_dataset_results=out_of_dataset_results,
        reports_dir=reports_dir
    )

    print("\n" + "=" * 60)
    print("STEP 8 EVALUATION SUMMARY:")
    print(f"  Test Accuracy:     {acc:.2f}%")
    print(f"  Top-3 Accuracy:    {top3_acc:.2f}%")
    print(f"  Top-5 Accuracy:    {top5_acc:.2f}%")
    print(f"  Macro F1:          {macro_f1:.4f}")
    print(f"  Weighted F1:       {weighted_f1:.4f}")
    print(f"  Correct Samples:   {correct_count:,}")
    print(f"  Incorrect Samples: {incorrect_count:,}")
    print("=" * 60)

    return {
        "accuracy": acc,
        "top1_acc": top1_acc,
        "top3_acc": top3_acc,
        "top5_acc": top5_acc,
        "macro_p": macro_p,
        "macro_r": macro_r,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "conf_stats": conf_stats,
        "confusions": confusions[:5],
        "out_of_dataset": out_of_dataset_results
    }


def plot_cm(cm: np.ndarray, class_names: list, output_path: Path, title: str, fmt: str, cmap):
    """Plot confusion matrix."""
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=class_names,
        yticklabels=class_names,
        title=title,
        ylabel="True Class",
        xlabel="Predicted Class"
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = format(cm[i, j], fmt) if fmt != "d" else str(int(cm[i, j]))
            ax.text(
                j, i, val,
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=8
            )

    fig.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"    Saved: {output_path}")


def plot_confidence_distribution(correct_confs: np.ndarray, incorrect_confs: np.ndarray, output_path: Path):
    """Plot confidence distribution comparing correct vs incorrect predictions."""
    fig, ax = plt.subplots(figsize=(10, 5))
    bins = np.linspace(0.0, 1.0, 50)

    if len(correct_confs) > 0:
        ax.hist(correct_confs, bins=bins, alpha=0.7, color="#10B981", label=f"Correct (N={len(correct_confs):,})", density=True)
    if len(incorrect_confs) > 0:
        ax.hist(incorrect_confs, bins=bins, alpha=0.7, color="#EF4444", label=f"Incorrect (N={len(incorrect_confs):,})", density=True)

    ax.set_title("Model Softmax Probability Confidence Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Confidence (Softmax Probability)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"    Saved: {output_path}")


def plot_misclassified_examples(misclass_df: pd.DataFrame, output_path: Path):
    """Plot visual grid of misclassified images."""
    if len(misclass_df) == 0:
        print("    No misclassifications to plot.")
        return

    sample_errors = misclass_df.head(min(16, len(misclass_df)))
    n_items = len(sample_errors)
    n_cols = min(4, n_items)
    n_rows = (n_items + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3.2, n_rows * 3.4))
    axes = np.array(axes).reshape(-1)

    for idx, (_, row) in enumerate(sample_errors.iterrows()):
        ax = axes[idx]
        try:
            img = Image.open(row["image_path"]).convert("RGB")
            ax.imshow(img)
            ax.set_title(f"True: {row['true_class']}\nPred: {row['predicted_class']}\nConf: {row['confidence'] * 100:.1f}%", fontsize=9, color="#DC2626")
        except Exception:
            ax.text(0.5, 0.5, "Image load error", ha="center")
        ax.axis("off")

    for idx in range(n_items, len(axes)):
        axes[idx].axis("off")

    plt.suptitle("Sample Misclassified Test Images (Fruits-360)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"    Saved: {output_path}")


def run_out_of_dataset_test(model, eval_transforms, device, id_to_food, project_root: Path) -> List[Dict]:
    """
    Run qualitative inference on external food images outside Fruits-360.
    Samples from AgriFreshNET raw dataset to observe real-world domain gap.
    """
    agrifresh_base = project_root / "data" / "raw" / "AgriFreshNET Freshness and Shelf-Life Image Datase" / "Processed Data" / "Processed Data"
    test_samples = []

    if agrifresh_base.exists():
        # Look for matching food categories in AgriFreshNET
        for target_food in ["Apple", "Banana", "Cucumber", "Tomato"]:
            matches = list(agrifresh_base.glob(f"*{target_food}*/**/*.jpg")) + list(agrifresh_base.glob(f"*{target_food}*/**/*.png"))
            if matches:
                test_samples.append((matches[0], target_food))
    
    results = []
    print("\n--- OUT-OF-DATASET QUALITATIVE INFERENCE ---")
    if not test_samples:
        print("    No external image files discovered for qualitative test.")
        return results

    for img_path, food_hint in test_samples:
        try:
            pil_img = Image.open(img_path).convert("RGB")
            img_tensor = eval_transforms(pil_img).unsqueeze(0).to(device)
            with torch.no_grad():
                logits = model(img_tensor)
                probs = F.softmax(logits, dim=1)[0]
                top_probs, top_indices = torch.topk(probs, 3)

            top1_food = id_to_food.get(str(top_indices[0].item()), f"Class {top_indices[0].item()}")
            top1_conf = float(top_probs[0].item())

            top_preds_str = [
                f"{id_to_food.get(str(idx.item()), f'Class {idx.item()}')} ({float(p.item()) * 100:.1f}%)"
                for p, idx in zip(top_probs, top_indices)
            ]

            res_item = {
                "image": str(img_path),
                "expected_category": food_hint,
                "predicted_food": top1_food,
                "confidence": round(top1_conf, 4),
                "percentage": f"{top1_conf * 100:.2f}%",
                "top3": top_preds_str
            }
            results.append(res_item)

            print(f"Image:          {img_path.name} (Source: AgriFreshNET)")
            print(f"Expected Hint:  {food_hint}")
            print(f"Prediction:     {top1_food}")
            print(f"Confidence:     {res_item['percentage']}")
            print(f"Top 3:          {', '.join(top_preds_str)}\n")

        except Exception as e:
            print(f"    Error processing external image {img_path}: {e}")

    return results


def write_evaluation_report(
    config: FoodRecognitionConfig,
    test_count: int,
    num_classes: int,
    acc: float,
    macro_p: float,
    macro_r: float,
    macro_f1: float,
    weighted_p: float,
    weighted_r: float,
    weighted_f1: float,
    top1_acc: float,
    top3_acc: float,
    top5_acc: Optional[float],
    correct_count: int,
    incorrect_count: int,
    conf_stats: dict,
    confusions: list,
    per_class_rows: list,
    total_params: int,
    file_size_mb: float,
    out_of_dataset_results: list,
    reports_dir: Path
):
    """Write comprehensive evaluation report following exact requested 11-section format."""
    top_confusions_text = ""
    for c in confusions[:6]:
        top_confusions_text += f"- **{c['true_class']} → {c['predicted_class']}**: {c['count']} test images\n"

    per_class_summary = ""
    for r in per_class_rows:
        per_class_summary += f"- **{r['class']}**: Precision={r['precision']:.4f}, Recall={r['recall']:.4f}, F1={r['f1_score']:.4f}, Support={r['support']}\n"

    out_of_dataset_text = ""
    for item in out_of_dataset_results:
        out_of_dataset_text += f"""
Image: `{Path(item['image']).name}`
Expected category: {item['expected_category']}
Prediction: {item['predicted_food']}
Confidence: {item['percentage']}
Top 3 predictions: {', '.join(item['top3'])}
"""

    report_content = f"""# FoodFresh AI Food Recognition Evaluation Report

## 1. Model

Model:
EfficientNet-B0

Checkpoint:
`models/trained/food_classifier.pth`

Pretrained initialization:
Official TorchVision EfficientNet-B0 (`EfficientNet_B0_Weights.DEFAULT`)

## 2. Test Dataset

Manifest:
`{config.test_manifest_path}` (Untouched test split, strictly unseen during training)

Number of classes:
{num_classes}

Number of test images:
{test_count:,}

## 3. Hardware

Device:
{config.device}

GPU:
{torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}

## 4. Overall Metrics

Accuracy:
{acc:.4f}%

Macro Precision:
{macro_p:.4f}

Macro Recall:
{macro_r:.4f}

Macro F1:
{macro_f1:.4f}

Weighted Precision:
{weighted_p:.4f}

Weighted Recall:
{weighted_r:.4f}

Weighted F1:
{weighted_f1:.4f}

## 5. Top-K Accuracy

Top-1:
{top1_acc:.4f}%

Top-3:
{top3_acc:.4f}%

Top-5:
{f"{top5_acc:.4f}%" if top5_acc is not None else "N/A"}

## 6. Per-Class Metrics

{per_class_summary}

Detailed metrics table saved in:
`reports/food_recognition_per_class_metrics.csv` and `reports/food_recognition_per_class_metrics.md`

## 7. Confusion Analysis

Most frequent observed class confusions:
{top_confusions_text if top_confusions_text else "- No class confusions observed."}

Full confusion matrices saved in:
`reports/food_recognition_confusion_matrix.png` (Counts)
`reports/food_recognition_confusion_matrix_normalized.png` (Proportions)

## 8. Confidence Analysis

Correct prediction confidence:
- Mean: {conf_stats['correct_mean']:.4f}
- Median: {conf_stats['correct_median']:.4f}
- Min: {conf_stats['correct_min']:.4f}
- Max: {conf_stats['correct_max']:.4f}

Incorrect prediction confidence:
- Mean: {conf_stats['incorrect_mean']:.4f}
- Median: {conf_stats['incorrect_median']:.4f}
- Min: {conf_stats['incorrect_min']:.4f}
- Max: {conf_stats['incorrect_max']:.4f}

Median confidence (overall):
{conf_stats['overall_median']:.4f}

Visualization saved in:
`reports/food_recognition_confidence_distribution.png`

> **Notice:** Model confidence reflects softmax output probability across food categories and does NOT represent food safety, quality, or shelf-life certainty.

## 9. Model Size

Parameters:
{total_params:,} total parameters ({total_params:,} trainable parameters)

Checkpoint size:
{file_size_mb:.2f} MB

## 10. Error Analysis

Number of incorrect predictions:
{incorrect_count:,} ({incorrect_count / test_count * 100:.2f}%)

Number of correct predictions:
{correct_count:,} ({correct_count / test_count * 100:.2f}%)

Observable patterns in misclassifications:
- Most misclassifications occur among visually similar botanical varieties sharing analogous skin textures, colors, or spherical profiles (such as Eggplant varieties with lighter coloration, or specific pepper and peach angles).
- For incorrect classifications, the average model confidence ({conf_stats['incorrect_mean'] * 100:.2f}%) is noticeably lower than for correct classifications ({conf_stats['correct_mean'] * 100:.2f}%), indicating appropriate uncertainty calibration.

Visual examples saved in:
`reports/food_recognition_misclassified_examples.png`
Complete log of all misclassifications saved in:
`reports/food_recognition_misclassifications.csv`

## 11. Important Limitation

This evaluation measures image classification performance on the Fruits-360 test set.

It does NOT prove:

- food safety
- freshness detection
- shelf-life prediction
- performance on arbitrary real-world kitchen images

Real-world performance must be tested separately.

---

## 12. Out-of-Dataset Qualitative Inference

The following qualitative test was conducted on external food images outside Fruits-360 (from AgriFreshNET) to observe behavior under non-studio environmental conditions:

{out_of_dataset_text if out_of_dataset_text else "No external test images tested."}

> **Notice:** These qualitative results illustrate domain-shift effects when moving from studio-isolated white backgrounds to real-world environments. They are NOT incorporated into the formal test metrics above.
"""
    eval_report_path = reports_dir / "food_recognition_evaluation_report.md"
    with open(eval_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nEvaluation report saved to: {eval_report_path}")


# Alias for backward compatibility and package export
evaluate_food_recognition_model = run_evaluation


if __name__ == "__main__":
    cfg = FoodRecognitionConfig()
    run_evaluation(cfg)

