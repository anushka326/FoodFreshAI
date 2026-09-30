"""
FoodFresh AI - Real-World Food Recognition V2 Evaluation Script
Scans data/real_world_eval/ directory, runs Food Recognition V2 inference,
evaluates out-of-domain generalization, and generates CSV and Markdown reports.
"""

from collections import defaultdict
import csv
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from backend.app.services.food_recognition_service import FoodRecognitionService

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def evaluate_real_world():
    eval_dir = PROJECT_ROOT / "data" / "real_world_eval"
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = reports_dir / "food_recognition_v2_real_world_predictions.csv"
    report_path = reports_dir / "food_recognition_v2_real_world_report.md"

    print("==================================================")
    print("FoodFresh AI - Real-World Food Recognition V2 Evaluation")
    print("==================================================")
    print(f"Scanning directory: {eval_dir}")

    # Discover images grouped by folder (folder name = ground truth class)
    image_entries = []
    if eval_dir.exists():
        for category_dir in eval_dir.iterdir():
            if category_dir.is_dir():
                ground_truth = category_dir.name
                for file_path in category_dir.iterdir():
                    if file_path.suffix.lower() in IMAGE_EXTENSIONS and file_path.is_file():
                        image_entries.append((file_path, ground_truth))

    print(f"Discovered {len(image_entries)} real-world evaluation images.")

    if not image_entries:
        print("No real-world evaluation images were available.")
        # 1. Write empty CSV with standard schema
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "image_path",
                "actual_food",
                "predicted_food",
                "confidence",
                "top_3",
                "is_correct",
                "status",
                "model_version"
            ])

        # 2. Write Markdown report documenting dataset absence
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# FoodFresh AI — Real-World Food Recognition V2 Evaluation Report\n\n")
            f.write("## Status\n")
            f.write("**No real-world evaluation images were available.**\n\n")
            f.write("The `data/real_world_eval/` folder structure has been prepared with subfolders for:\n")
            f.write("- `Apple/`\n- `Banana/`\n- `Orange/`\n- `Pomegranate/`\n- `Tomato/`\n- `Mango/`\n\n")
            f.write("## Confidence Threshold & Calibration Note\n")
            f.write("- **Confidence threshold requires additional calibration data.**\n")
            f.write("- Softmax confidence outputs do not represent calibrated true probabilities on out-of-distribution real-world images.\n")
            f.write("- When real-world user photos are added to `data/real_world_eval/`, re-run `python scripts/evaluate_real_world_food.py` to calculate accuracy and establish an empirically grounded confidence threshold.\n")

        print(f"Saved empty predictions schema to: {csv_path}")
        print(f"Saved real-world report to: {report_path}")
        return

    # Initialize V2 service
    print("Initializing Food Recognition V2 inference service...")
    service = FoodRecognitionService(model_version="v2")
    if not service.is_loaded:
        print(f"Error loading Food Recognition V2 model: {service.load_error}")
        return

    records = []
    per_class_stats = defaultdict(lambda: {"total": 0, "correct": 0, "confidences": []})
    confusion = defaultdict(lambda: defaultdict(int))
    high_conf_errors = []

    for img_path, ground_truth in image_entries:
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()

            result = service.predict_image(img_bytes, top_k=3)
            predicted = result.get("detectedFood") or "Unknown"
            conf = result.get("recognitionConfidence", 0.0)
            top_preds = result.get("topPredictions", [])
            top_3_str = "; ".join([f"{p['food']}: {p['confidence']}%" for p in top_preds])
            status = result.get("status", "unknown")
            model_ver = result.get("modelVersion", "v2")

            is_correct = (predicted.lower() == ground_truth.lower())

            per_class_stats[ground_truth]["total"] += 1
            if is_correct:
                per_class_stats[ground_truth]["correct"] += 1
            else:
                if conf >= 70.0:
                    high_conf_errors.append({
                        "path": str(img_path.relative_to(PROJECT_ROOT)),
                        "actual": ground_truth,
                        "predicted": predicted,
                        "confidence": conf,
                        "top_3": top_3_str
                    })

            per_class_stats[ground_truth]["confidences"].append(conf)
            confusion[ground_truth][predicted] += 1

            records.append({
                "image_path": str(img_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "actual_food": ground_truth,
                "predicted_food": predicted,
                "confidence": conf,
                "top_3": top_3_str,
                "is_correct": is_correct,
                "status": status,
                "model_version": model_ver
            })
        except Exception as e:
            print(f"Failed to evaluate {img_path}: {e}")

    # Write predictions CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "actual_food", "predicted_food", "confidence", "top_3", "is_correct", "status", "model_version"
        ])
        writer.writeheader()
        writer.writerows(records)

    # Compute overall statistics
    total_samples = len(records)
    total_correct = sum(1 for r in records if r["is_correct"])
    overall_acc = (total_correct / total_samples * 100.0) if total_samples > 0 else 0.0

    # Write detailed markdown report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# FoodFresh AI — Real-World Food Recognition V2 Evaluation Report\n\n")
        f.write(f"- **Evaluated Images:** {total_samples}\n")
        f.write(f"- **Overall Accuracy:** {overall_acc:.2f}% ({total_correct}/{total_samples})\n")
        f.write(f"- **Model Version:** V2 (EfficientNet-B0, 24 classes)\n\n")

        f.write("## Per-Class Evaluation Summary\n\n")
        f.write("| Food Category | Total Samples | Correct | Accuracy | Mean Confidence |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for cls_name in sorted(per_class_stats.keys()):
            stats = per_class_stats[cls_name]
            acc = (stats["correct"] / stats["total"] * 100.0) if stats["total"] > 0 else 0.0
            mean_conf = (sum(stats["confidences"]) / len(stats["confidences"])) if stats["confidences"] else 0.0
            f.write(f"| {cls_name} | {stats['total']} | {stats['correct']} | {acc:.1f}% | {mean_conf:.1f}% |\n")

        f.write("\n## High-Confidence Errors (Confidence >= 70%)\n\n")
        if high_conf_errors:
            f.write("| Image | Actual | Predicted | Confidence | Top 3 |\n")
            f.write("| :--- | :--- | :--- | :---: | :--- |\n")
            for err in high_conf_errors:
                f.write(f"| `{err['path']}` | {err['actual']} | {err['predicted']} | {err['confidence']}% | {err['top_3']} |\n")
        else:
            f.write("No high-confidence incorrect predictions recorded.\n")

        f.write("\n## Confidence & Calibration Assessment\n")
        f.write("- **Confidence threshold requires additional calibration data.**\n")
        f.write("- Softmax confidence represents intra-distribution mathematical normalization rather than true Bayesian probability.\n")

    print(f"Real-world evaluation complete: {overall_acc:.2f}% overall accuracy.")
    print(f"Results saved to:\n  {csv_path}\n  {report_path}")


if __name__ == "__main__":
    evaluate_real_world()
