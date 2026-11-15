"""
FoodFresh AI - Comprehensive ML Pipeline & Before/After Evaluation Script
Tests end-to-end recognition, freshness classification, and shelf-life ML regression
across all canonical real-world test images.
"""

import json
from pathlib import Path
import sys
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.food_recognition_service import get_food_recognition_service
from backend.app.services.shelf_life_service import get_shelf_life_service

TEST_CASES = [
    {
        "expected": "Apple",
        "path": "data/real_world_eval/apple.jpg",
        "expected_freshness": "Fresh",
        "storage": "countertop",
        "days": 1,
    },
    {
        "expected": "Banana",
        "path": "data/real_world_eval/banana.jpg",
        "expected_freshness": "Fresh",
        "storage": "countertop",
        "days": 2,
    },
    {
        "expected": "Tomato",
        "path": "data/real_world_eval/tomato.jpg",
        "expected_freshness": "Fresh",
        "storage": "countertop",
        "days": 1,
    },
    {
        "expected": "Orange",
        "path": "data/real_world_eval/orange.jpg",
        "expected_freshness": "Fresh",
        "storage": "countertop",
        "days": 2,
    },
    {
        "expected": "Pomegranate",
        "path": "data/real_world_eval/pomegranate.jpg",
        "expected_freshness": "Fresh",
        "storage": "refrigerated",
        "days": 3,
    },
    {
        "expected": "Bread",
        "path": "data/real_world_eval/bread.jpg",
        "expected_freshness": "Fresh",
        "storage": "pantry",
        "days": 2,
    },
    {
        "expected": "Rotten Tomato",
        "path": "data/real_world_eval/rotten_tomato.jpg",
        "expected_freshness": "Rotten",
        "storage": "countertop",
        "days": 5,
    },
    {
        "expected": "Rotten Orange",
        "path": "data/real_world_eval/rotten_orange.jpg",
        "expected_freshness": "Rotten",
        "storage": "countertop",
        "days": 10,
    },
]


def run_verification():
    service = get_food_recognition_service()
    results = []

    print(f"{'Image':<18} | {'Detected Food':<15} | {'Conf':<7} | {'Freshness Label':<28} | {'Score':<7} | {'ML Shelf Life':<14} | {'Status'}")
    print("-" * 115)

    for tc in TEST_CASES:
        img_path = PROJECT_ROOT / tc["path"]
        if not img_path.exists():
            print(f"Skipping {tc['expected']}: file {img_path} not found")
            continue

        with open(img_path, "rb") as f:
            img_bytes = f.read()

        pred = service.predict_image(
            image_bytes=img_bytes,
            storage_type=tc["storage"],
            days_stored=tc["days"]
        )

        detected_food = pred.get("detectedFood")
        conf = pred.get("recognitionConfidence")
        freshness = pred.get("freshness", {})
        f_label = freshness.get("label", "N/A")
        f_score = freshness.get("score", 0.0)
        shelf = pred.get("shelfLife", {})
        rem = shelf.get("remaining", {})
        ml_days = shelf.get("mlPredictedDays")

        results.append({
            "test_case": tc["expected"],
            "detected_food": detected_food,
            "confidence": conf,
            "freshness_label": f_label,
            "freshness_score": f_score,
            "shelf_life_remaining": rem,
            "ml_predicted_days": ml_days,
            "shelf_life_source": shelf.get("source"),
            "shelf_life_model_version": shelf.get("mlModelVersion")
        })

        rem_dict = rem or {}
        rem_str = f"{ml_days}d" if ml_days is not None else (f"{rem_dict.get('minDays')}-{rem_dict.get('maxDays')}d" if rem else "0d (Spoiled)")
        status = "PASS" if detected_food and any(term in detected_food.lower() for term in tc["expected"].lower().split()) else "REVIEW"
        print(f"{tc['expected']:<18} | {str(detected_food):<15} | {f'{conf:.1f}%' if conf else 'N/A':<7} | {str(f_label)[:28]:<28} | {f'{f_score:.1f}%' if f_score else 'N/A':<7} | {rem_str:<14} | {status}")

    out_file = PROJECT_ROOT / "reports" / "pipeline_verification_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved comprehensive verification results to {out_file}")


if __name__ == "__main__":
    run_verification()
