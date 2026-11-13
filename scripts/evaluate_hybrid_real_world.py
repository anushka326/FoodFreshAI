"""
FoodFresh AI - Real-World Hybrid Vision Evaluation & Multi-Object Benchmark
Evaluates end-to-end HybridVisionPipeline on real-world food items:
Pomegranate, Tomato, Apple, Banana, Orange, and Multi-food collage (Apple + Banana + Tomato).
Generates reports/hybrid_real_world_evaluation.csv.
"""

import csv
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.hybrid_vision.hybrid_pipeline import get_hybrid_vision_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("foodfresh.eval_real_world")

EVAL_IMAGES = [
    ("Pomegranate", "data/real_world_eval/pomegranate.jpg"),
    ("Tomato", "data/real_world_eval/tomato.jpg"),
    ("Apple", "data/real_world_eval/apple.jpg"),
    ("Banana", "data/real_world_eval/banana.jpg"),
    ("Orange", "data/real_world_eval/orange.jpg"),
    ("Multi-Food (Apple, Banana, Tomato)", "data/real_world_eval/multi_apple_banana_tomato.jpg"),
]


def run_hybrid_evaluation():
    logger.info("Initializing Hybrid Vision Pipeline...")
    pipeline = get_hybrid_vision_pipeline()

    records = []

    for actual_label, img_path_str in EVAL_IMAGES:
        img_path = Path(img_path_str)
        if not img_path.exists():
            logger.error(f"Image missing: {img_path}")
            continue

        logger.info(f"\n==================================================")
        logger.info(f"Evaluating: {actual_label} ({img_path})")
        logger.info(f"==================================================")

        res = pipeline.analyze(img_path_str)

        # Extract sub-model outputs for auditing
        dino_info = res.foodRecognition.groundingDino or {}
        dino_objs = [f"{o['label']} ({o['confidence']}%)" for o in dino_info.get("objects", [])]
        dino_str = "; ".join(dino_objs) if dino_objs else "none"

        raw_info = res.foodRecognition.rawFoodResNet or {}
        raw_preds = [f"{p['label']} ({p['confidence']}%)" for p in raw_info.get("topPredictions", [])[:3]]
        raw_str = "; ".join(raw_preds) if raw_preds else "none"

        sig_info = res.foodRecognition.siglip2 or {}
        sig_preds = [f"{p['label']} ({p['confidence']}%)" for p in sig_info.get("topPredictions", [])[:3]]
        sig_str = "; ".join(sig_preds) if sig_preds else "none"

        top_cand_str = "; ".join([f"{c.label} ({c.confidence}%)" for c in res.topPredictions[:3]])

        freshness_label = res.freshness.label or "N/A"
        freshness_score = f"{res.freshness.score:.1f}%" if res.freshness.score is not None else "N/A"
        freshness_str = f"{freshness_label} ({freshness_score})"

        total_latency = res.latencyMs.get("total_pipeline_ms", 0.0)

        record = {
            "actual_known_class": actual_label,
            "image_path": str(img_path),
            "analysis_status": res.analysisStatus,
            "detected_food": res.detectedFood or "Uncertain / None",
            "recognition_confidence": f"{res.recognitionConfidence:.2f}%" if res.recognitionConfidence is not None else "N/A",
            "grounding_dino_output": dino_str,
            "raw_food_output": raw_str,
            "siglip2_output": sig_str,
            "top_candidates": top_cand_str,
            "freshness_output": freshness_str,
            "shelf_life_status": res.shelfLife.status,
            "pipeline_latency_ms": total_latency,
            "decision_message": res.message or ""
        }
        records.append(record)

        logger.info(f"-> Status: {res.analysisStatus}")
        logger.info(f"-> Detected Food: {res.detectedFood} ({res.recognitionConfidence}%)")
        logger.info(f"-> Freshness: {freshness_str}")
        logger.info(f"-> Latency: {total_latency} ms")
        logger.info(f"-> Decision: {res.message}")

    # Write CSV
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    csv_path = reports_dir / "hybrid_real_world_evaluation.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "actual_known_class",
            "image_path",
            "analysis_status",
            "detected_food",
            "recognition_confidence",
            "grounding_dino_output",
            "raw_food_output",
            "siglip2_output",
            "top_candidates",
            "freshness_output",
            "shelf_life_status",
            "pipeline_latency_ms",
            "decision_message"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    logger.info(f"\nSuccessfully wrote real-world evaluation CSV to: {csv_path}")


if __name__ == "__main__":
    run_hybrid_evaluation()
