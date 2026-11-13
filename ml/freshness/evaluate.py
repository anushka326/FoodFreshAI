"""Held-out evaluation and validation-fitted temperature calibration for freshness models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             confusion_matrix, precision_recall_fscore_support)
from torch.utils.data import DataLoader
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.freshness.config import FreshnessConfig
from ml.freshness.dataset import FreshnessDataset
from ml.freshness.model import create_freshness_model
from ml.freshness.utils import load_checkpoint
from ml.hybrid_vision.freshness_service import FreshnessService

CLASSES = ["Fresh", "Semi-Fresh", "Rotten"]
EVAL_TRANSFORM = transforms.Compose([
    transforms.Resize((256, 256)), transforms.CenterCrop(224), transforms.ToTensor(),
    transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
])


def _collect(model, loader, device, baseline=False):
    model.eval(); logits_all = []; targets_all = []; paths = []; foods = []
    with torch.no_grad():
        for images, labels, batch_foods, batch_paths in loader:
            raw = model(images.to(device)).float()
            if baseline:
                # V2 vocabulary order is fresh, rotten, slightly_spoiled.
                raw = raw[:, [0, 2, 1]]
            logits_all.append(raw.cpu()); targets_all.append(labels.cpu())
            paths.extend(batch_paths); foods.extend(batch_foods)
    return torch.cat(logits_all), torch.cat(targets_all).numpy(), paths, foods


def _temperature(val_logits, val_targets):
    device = val_logits.device
    log_t = torch.zeros((), device=device, requires_grad=True)
    labels = torch.as_tensor(val_targets, dtype=torch.long, device=device)
    optimizer = torch.optim.LBFGS([log_t], lr=.1, max_iter=100, line_search_fn="strong_wolfe")
    def closure():
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(val_logits / log_t.exp(), labels)
        loss.backward()
        return loss
    optimizer.step(closure)
    return float(log_t.detach().exp().clamp(.05, 20).item())


def _ece(probs, targets, bins=15):
    conf = probs.max(axis=1); pred = probs.argmax(axis=1); ece = 0.0; rows = []
    edges = np.linspace(0.0, 1.0, bins + 1)
    for i in range(bins):
        mask = (conf >= edges[i]) & (conf < edges[i + 1] if i < bins - 1 else conf <= edges[i + 1])
        if mask.any():
            accuracy = float((pred[mask] == targets[mask]).mean())
            mean_conf = float(conf[mask].mean())
            ece += float(mask.mean()) * abs(accuracy - mean_conf)
            rows.append({"lower": float(edges[i]), "upper": float(edges[i + 1]),
                         "count": int(mask.sum()), "accuracy": accuracy, "confidence": mean_conf})
        else:
            rows.append({"lower": float(edges[i]), "upper": float(edges[i + 1]),
                         "count": 0, "accuracy": None, "confidence": None})
    return ece, rows


def _metrics(logits, targets, temperature=1.0):
    probs = torch.softmax(logits / temperature, dim=1).numpy()
    pred = probs.argmax(axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(
        targets, pred, labels=[0, 1, 2], zero_division=0
    )
    ece, bins = _ece(probs, targets)
    per_class = {name: {"precision": float(precision[i]), "recall": float(recall[i]),
                        "f1": float(f1[i]), "support": int(support[i])}
                 for i, name in enumerate(CLASSES)}
    return {
        "accuracy": float(accuracy_score(targets, pred)),
        "macro_f1": float(np.mean(f1)),
        "balanced_accuracy": float(balanced_accuracy_score(targets, pred)),
        "macro_precision": float(np.mean(precision)), "macro_recall": float(np.mean(recall)),
        "nll": float(torch.nn.functional.cross_entropy(logits / temperature,
                         torch.as_tensor(targets, dtype=torch.long)).item()),
        "ece_15": float(ece), "per_class": per_class,
        "confusion_matrix": confusion_matrix(targets, pred, labels=[0, 1, 2]).tolist(),
        "probabilities": probs, "reliability_bins": bins,
    }


def _save_reliability_plot(calibrations, output):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    for label, bins in calibrations.items():
        valid = [b for b in bins if b["count"]]
        ax.plot([b["confidence"] for b in valid], [b["accuracy"] for b in valid],
                marker="o", label=label)
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Mean confidence", ylabel="Accuracy",
           title="Freshness test reliability (15 bins)")
    ax.legend(); fig.tight_layout(); fig.savefig(output, dpi=150); plt.close(fig)
    return True


def evaluate_model(checkpoint_path=None, output_dir=None, config=None):
    config = config or FreshnessConfig()
    checkpoint = Path(checkpoint_path or ROOT / "models/candidates/freshness_v3_efficientnet_b0.pth")
    out_dir = Path(output_dir or ROOT / "reports"); out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(config.device)
    datasets = {
        "validation": FreshnessDataset(manifest_path=config.val_manifest_path,
                                        transform=EVAL_TRANSFORM, return_metadata=True),
        "test": FreshnessDataset(manifest_path=config.test_manifest_path,
                                 transform=EVAL_TRANSFORM, return_metadata=True),
    }
    loaders = {split: DataLoader(ds, batch_size=32, shuffle=False, num_workers=0)
               for split, ds in datasets.items()}

    candidate = create_freshness_model(num_classes=3, pretrained=False)
    load_checkpoint(checkpoint, candidate, device=str(device))
    cand_val = _collect(candidate, loaders["validation"], device)
    cand_test = _collect(candidate, loaders["test"], device)
    cand_t = _temperature(cand_val[0], cand_val[1])
    candidate_test_raw = _metrics(cand_test[0], cand_test[1])
    candidate_test_cal = _metrics(cand_test[0], cand_test[1], cand_t)

    baseline = FreshnessService(device=device)
    if not baseline.is_loaded or baseline.model is None:
        raise RuntimeError(f"Production V2 could not load: {baseline.load_error}")
    base_val = _collect(baseline.model, loaders["validation"], device, baseline=True)
    base_test = _collect(baseline.model, loaders["test"], device, baseline=True)
    base_t = _temperature(base_val[0], base_val[1])
    baseline_test_raw = _metrics(base_test[0], base_test[1])
    baseline_test_cal = _metrics(base_test[0], base_test[1], base_t)

    # Save uncalibrated predictions plus calibrated confidence and correctness.
    preds = candidate_test_raw["probabilities"].argmax(axis=1)
    cal_probs = candidate_test_cal["probabilities"]
    records = []
    for i, (path, food) in enumerate(zip(cand_test[2], cand_test[3])):
        records.append({"image_path": path, "food_type": food,
                        "true_freshness": CLASSES[int(cand_test[1][i])],
                        "predicted_freshness": CLASSES[int(preds[i])],
                        "raw_confidence": float(candidate_test_raw["probabilities"][i].max()),
                        "calibrated_confidence": float(cal_probs[i].max()),
                        "correct": bool(preds[i] == cand_test[1][i])})
    pd.DataFrame(records).to_csv(out_dir / "freshness_v3_test_predictions.csv", index=False)

    report = {
        "candidate_checkpoint": str(checkpoint), "production_checkpoint": "models/trained/freshness_model_v2.pth",
        "architecture_candidate": "EfficientNet-B0", "architecture_production": "ResNet-18 fastai-style head",
        "test_samples": len(cand_test[1]), "validation_samples": len(cand_val[1]),
        "candidate_temperature": cand_t, "production_temperature": base_t,
        "candidate_raw": {k: v for k, v in candidate_test_raw.items() if k not in ("probabilities", "reliability_bins")},
        "candidate_calibrated": {k: v for k, v in candidate_test_cal.items() if k not in ("probabilities", "reliability_bins")},
        "production_raw": {k: v for k, v in baseline_test_raw.items() if k not in ("probabilities", "reliability_bins")},
        "production_calibrated": {k: v for k, v in baseline_test_cal.items() if k not in ("probabilities", "reliability_bins")},
        "candidate_reliability": candidate_test_raw["reliability_bins"],
        "candidate_calibrated_reliability": candidate_test_cal["reliability_bins"],
        "production_reliability": baseline_test_raw["reliability_bins"],
        "production_calibrated_reliability": baseline_test_cal["reliability_bins"],
    }
    (out_dir / "freshness_model_v3_evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    diagram = _save_reliability_plot({
        "V3 raw": candidate_test_raw["reliability_bins"],
        "V3 temperature scaled": candidate_test_cal["reliability_bins"],
        "V2 raw": baseline_test_raw["reliability_bins"],
        "V2 temperature scaled": baseline_test_cal["reliability_bins"],
    }, out_dir / "freshness_reliability_diagram.png")
    report_path = out_dir / "freshness_model_v3_evaluation.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Freshness V3 held-out evaluation and production comparison\n\n")
        f.write(f"- Test rows: {report['test_samples']} (same AgriFreshNET held-out split for both models)\n")
        f.write(f"- V3 checkpoint: `{checkpoint}`\n- Production checkpoint: `models/trained/freshness_model_v2.pth`\n\n")
        f.write("| Model | Accuracy | Macro F1 | Balanced accuracy | Macro precision | Macro recall | ECE raw | NLL raw | Temperature (validation) | ECE scaled | NLL scaled |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for label, raw, cal, temp in [
            ("V3 EfficientNet-B0", candidate_test_raw, candidate_test_cal, cand_t),
            ("Production V2 ResNet-18", baseline_test_raw, baseline_test_cal, base_t),
        ]:
            f.write(f"| {label} | {raw['accuracy']:.4f} | {raw['macro_f1']:.4f} | {raw['balanced_accuracy']:.4f} | {raw['macro_precision']:.4f} | {raw['macro_recall']:.4f} | {raw['ece_15']:.4f} | {raw['nll']:.4f} | {temp:.4f} | {cal['ece_15']:.4f} | {cal['nll']:.4f} |\n")
        f.write("\n## V3 per-class test metrics\n\n| Class | Precision | Recall | F1 | Support |\n|---|---:|---:|---:|---:|\n")
        for name, m in candidate_test_raw["per_class"].items():
            f.write(f"| {name} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['support']} |\n")
        f.write("\n## Confusion matrices (rows actual, columns predicted; Fresh, Semi-Fresh, Rotten)\n\n")
        f.write("V3:\n```text\n" + json.dumps(candidate_test_raw["confusion_matrix"]) + "\n```\n\n")
        f.write("Production V2:\n```text\n" + json.dumps(baseline_test_raw["confusion_matrix"]) + "\n```\n")
        f.write("\nTemperature was fitted on validation logits only; all displayed metrics use the untouched test split. ")
        f.write("Reliability diagram: `freshness_reliability_diagram.png`.\n" if diagram else "Matplotlib unavailable; reliability diagram not generated.\n")
        f.write("V3 is not promoted by this script.\n")
    print(report_path)
    print(json.dumps({k: report[k] for k in ("candidate_temperature", "production_temperature", "candidate_raw", "candidate_calibrated", "production_raw", "production_calibrated")}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, default=ROOT / "models/candidates/freshness_v3_efficientnet_b0.pth")
    args = parser.parse_args()
    evaluate_model(checkpoint_path=args.checkpoint)
