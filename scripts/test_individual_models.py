"""
FoodFresh AI - Individual Hybrid Model Testing
Tests Grounding DINO, SigLIP 2, Raw Food ResNet-50, and Freshness ResNet-18 individually
on canonical project images (Pomegranate, Tomato, Apple, Banana, Orange).
Generates reports/hybrid_model_individual_tests.csv and reports/hybrid_model_individual_tests.md.
"""

import csv
import json
import logging
import time
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.hybrid_vision.grounding_dino_service import get_grounding_dino_service
from ml.hybrid_vision.siglip2_service import get_siglip2_service
from ml.hybrid_vision.raw_food_service import get_raw_food_service
from ml.hybrid_vision.freshness_service import get_freshness_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("foodfresh.test_individual")

TEST_IMAGES = [
    ("Pomegranate", "data/real_world_eval/pomegranate.jpg"),
    ("Tomato", "data/real_world_eval/tomato.jpg"),
    ("Apple", "data/real_world_eval/apple.jpg"),
    ("Banana", "data/real_world_eval/banana.jpg"),
    ("Orange", "data/real_world_eval/orange.jpg"),
]


def run_individual_tests():
    logger.info("Initializing individual services...")
    dino = get_grounding_dino_service()
    siglip = get_siglip2_service()
    raw_food = get_raw_food_service()
    freshness = get_freshness_service()

    results = []

    for expected_name, img_path_str in TEST_IMAGES:
        img_path = Path(img_path_str)
        if not img_path.exists():
            logger.error(f"Image not found: {img_path}")
            continue

        image = Image.open(img_path).convert("RGB")
        logger.info(f"\n--- Testing {expected_name} ({img_path}) ---")

        # 1. Grounding DINO
        try:
            d_res = dino.detect(image)
            top_obj = d_res.food_objects[0] if d_res.food_objects else (d_res.detected_objects[0] if d_res.detected_objects else None)
            pred = top_obj.label if top_obj else "none"
            score = top_obj.confidence if top_obj else 0.0
            top_preds = [f"{o.label} ({o.confidence}%)" for o in d_res.detected_objects[:3]]
            results.append({
                "image": expected_name,
                "model": "Grounding DINO (base)",
                "prediction": pred,
                "confidence_score": score,
                "top_predictions": "; ".join(top_preds) if top_preds else "none",
                "latency_ms": d_res.latency_ms,
                "error": d_res.error or ""
            })
            logger.info(f"Grounding DINO: {pred} ({score}%) in {d_res.latency_ms} ms")
        except Exception as e:
            results.append({
                "image": expected_name,
                "model": "Grounding DINO (base)",
                "prediction": "ERROR",
                "confidence_score": 0.0,
                "top_predictions": "",
                "latency_ms": 0.0,
                "error": str(e)
            })

        # 2. SigLIP 2
        try:
            s_res = siglip.classify(image, top_k=5)
            top_p = s_res.top_predictions[0] if s_res.top_predictions else None
            pred = top_p.label if top_p else "none"
            score = top_p.confidence if top_p else 0.0
            top_preds = [f"{p.label} ({p.confidence}%)" for p in s_res.top_predictions[:3]]
            results.append({
                "image": expected_name,
                "model": "SigLIP 2 (base-patch16-224)",
                "prediction": pred,
                "confidence_score": score,
                "top_predictions": "; ".join(top_preds) if top_preds else "none",
                "latency_ms": s_res.latency_ms,
                "error": s_res.error or ""
            })
            logger.info(f"SigLIP 2: {pred} ({score}%) in {s_res.latency_ms} ms")
        except Exception as e:
            results.append({
                "image": expected_name,
                "model": "SigLIP 2 (base-patch16-224)",
                "prediction": "ERROR",
                "confidence_score": 0.0,
                "top_predictions": "",
                "latency_ms": 0.0,
                "error": str(e)
            })

        # 3. Raw Food ResNet-50
        try:
            r_res = raw_food.classify(image, top_k=5)
            top_p = r_res.top_predictions[0] if r_res.top_predictions else None
            pred = top_p.label if top_p else "none"
            score = top_p.confidence if top_p else 0.0
            top_preds = [f"{p.label} ({p.confidence}%)" for p in r_res.top_predictions[:3]]
            results.append({
                "image": expected_name,
                "model": "Raw Food ResNet-50",
                "prediction": pred,
                "confidence_score": score,
                "top_predictions": "; ".join(top_preds) if top_preds else "none",
                "latency_ms": r_res.latency_ms,
                "error": r_res.error or ""
            })
            logger.info(f"Raw Food ResNet-50: {pred} ({score}%) in {r_res.latency_ms} ms")
        except Exception as e:
            results.append({
                "image": expected_name,
                "model": "Raw Food ResNet-50",
                "prediction": "ERROR",
                "confidence_score": 0.0,
                "top_predictions": "",
                "latency_ms": 0.0,
                "error": str(e)
            })

        # 4. Freshness ResNet-18
        try:
            f_res = freshness.predict(image)
            pred = f_res.label or "none"
            score = f_res.score or 0.0
            top_preds = [f"{k}: {v}%" for k, v in f_res.all_scores.items()]
            results.append({
                "image": expected_name,
                "model": "Freshness ResNet-18",
                "prediction": pred,
                "confidence_score": score,
                "top_predictions": "; ".join(top_preds) if top_preds else "none",
                "latency_ms": f_res.latency_ms,
                "error": f_res.error or ""
            })
            logger.info(f"Freshness: {pred} ({score}%) in {f_res.latency_ms} ms")
        except Exception as e:
            results.append({
                "image": expected_name,
                "model": "Freshness ResNet-18",
                "prediction": "ERROR",
                "confidence_score": 0.0,
                "top_predictions": "",
                "latency_ms": 0.0,
                "error": str(e)
            })

    # Write CSV
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    csv_path = reports_dir / "hybrid_model_individual_tests.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "model", "prediction", "confidence_score", "top_predictions", "latency_ms", "error"])
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Wrote CSV report: {csv_path}")

    # Write Markdown
    md_path = reports_dir / "hybrid_model_individual_tests.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# FoodFresh AI — Individual Hybrid Vision Model Tests\n\n")
        f.write("Evaluation of each individual model in the hybrid vision stack on canonical project images.\n\n")
        f.write("| Image | Model | Prediction | Confidence / Score (%) | Top Predictions | Latency (ms) | Error |\n")
        f.write("|-------|-------|------------|------------------------|-----------------|--------------|-------|\n")
        for r in results:
            err = r["error"] if r["error"] else "None"
            f.write(f"| {r['image']} | {r['model']} | **{r['prediction']}** | {r['confidence_score']:.2f}% | {r['top_predictions']} | {r['latency_ms']:.1f} | {err} |\n")
        f.write("\n## Summary & Observations\n\n")
        f.write("- **Grounding DINO** operates as an open-vocabulary bounding box detector with prompt-based localization.\n")
        f.write("- **SigLIP 2** classifies against the open food vocabulary without fixed-class retraining.\n")
        f.write("- **Raw Food ResNet-50** acts as a domain-specific classifier across 90 raw agricultural classes.\n")
        f.write("- **Freshness ResNet-18** predicts visible surface quality states ('Fresh', 'Slightly Spoiled', 'Rotten').\n")
    logger.info(f"Wrote Markdown report: {md_path}")


if __name__ == "__main__":
    run_individual_tests()
