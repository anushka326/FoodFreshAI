"""
FoodFresh AI - Complete End-to-End Real-World Pipeline Test
Executes full HTTP inference tests against the live FastAPI backend on all required produce images.
Validates:
  1. Food recognition & confidence
  2. Grounding DINO scene object detection
  3. Freshness estimation (V2 promoted model + calibration)
  4. USDA FoodKeeper shelf-life calculation
  5. Eat First priority ranking
  6. FreshoBuddy database persistence & chat endpoint
Generates reports/final_real_world_food_tests.csv.
"""

import os
import sys
import csv
import json
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = PROJECT_ROOT / "data" / "real_world_eval"
API_URL = "http://127.0.0.1:8000/api/food-recognition/predict"
FRESHO_CHAT_URL = "http://127.0.0.1:8000/api/fresho-buddy/chat"
FRESHO_CONVS_URL = "http://127.0.0.1:8000/api/fresho-buddy/conversations"
CSV_OUT = PROJECT_ROOT / "reports" / "final_real_world_food_tests.csv"

TEST_IMAGES = [
    ("green_chilli.jpg", "Fresh green chilli", "crisper", 1),
    ("rotten_orange.jpg", "Rotten/moldy orange", "countertop", 10),
    ("rotten_tomato.jpg", "Rotten tomato", "countertop", 14),
    ("bell_pepper.jpg", "Fresh bell pepper", "crisper", 2),
    ("potato.jpg", "Fresh potato", "countertop", 5),
    ("apple.jpg", "Fresh apple", "countertop", 3),
    ("pomegranate.jpg", "Fresh pomegranate", "countertop", 2),
    ("bread.jpg", "Bread / bakery item", "countertop", 2),
    ("banana.jpg", "Fresh banana", "countertop", 2),
    ("tomato.jpg", "Fresh tomato", "countertop", 2)
]


def main():
    print("=" * 65)
    print("FOODFRESH AI — FINAL END-TO-END PIPELINE EVALUATION")
    print("=" * 65)

    results = []

    for filename, description, storage, days in TEST_IMAGES:
        img_path = EVAL_DIR / filename
        if not img_path.exists():
            print(f"File not found: {img_path}")
            continue

        print(f"\nEvaluating: {filename} ({description})...")
        with open(img_path, "rb") as f:
            files = {"file": (filename, f, "image/jpeg")}
            data = {"storage_type": storage, "days_stored": days}
            resp = requests.post(API_URL, files=files, data=data, timeout=60)

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            results.append({
                "image": filename,
                "food_prediction": "ERROR",
                "food_confidence": 0,
                "objects": "none",
                "freshness_prediction": "ERROR",
                "freshness_confidence": 0,
                "shelf_life_status": "error",
                "remaining_min_days": 0,
                "remaining_max_days": 0,
                "eat_first_priority": "ERROR",
                "status": f"HTTP {resp.status_code}"
            })
            continue

        res_json = resp.json()

        food = res_json.get("detectedFood") or "Unknown"
        conf = res_json.get("recognitionConfidence")
        if conf is not None:
            conf_pct = round(conf * 100.0, 1) if conf <= 1.0 else round(conf, 1)
        else:
            conf_pct = 0.0

        # Scene Objects
        objs = res_json.get("detectedObjects", [])
        obj_labels = [o.get("label", "").title() for o in objs if o.get("label")]
        obj_str = " · ".join(obj_labels[:5]) if obj_labels else "No additional objects"

        # Freshness
        freshness = res_json.get("freshness", {})
        f_pred = freshness.get("label", "Uncertain")
        f_conf = freshness.get("score") or freshness.get("confidence") or 0.0

        # Shelf Life
        shelf = res_json.get("shelfLife", {})
        shelf_status = shelf.get("status", "unavailable")
        rem = shelf.get("remaining") or {}
        rem_min = rem.get("minDays") if rem else None
        rem_max = rem.get("maxDays") if rem else None

        # Eat First
        eat = res_json.get("eatFirstPriority", {})
        priority = eat.get("priority") or "NOT_AVAILABLE"

        analysis_status = res_json.get("analysisStatus", "success")

        results.append({
            "image": filename,
            "food_prediction": food,
            "food_confidence": conf_pct,
            "objects": obj_str,
            "freshness_prediction": f_pred,
            "freshness_confidence": round(f_conf, 1),
            "shelf_life_status": shelf_status,
            "remaining_min_days": rem_min if rem_min is not None else "N/A",
            "remaining_max_days": rem_max if rem_max is not None else "N/A",
            "eat_first_priority": priority,
            "status": analysis_status
        })

        print(f"  Food:       {food} ({conf_pct}%)")
        print(f"  Objects:    {obj_str}")
        print(f"  Freshness:  {f_pred} ({f_conf:.1f}%)")
        print(f"  Shelf-Life: {shelf_status} (Remaining: {rem_min}–{rem_max} days)")
        print(f"  Eat First:  {priority}")

    # Write CSV
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "image",
            "food_prediction",
            "food_confidence",
            "objects",
            "freshness_prediction",
            "freshness_confidence",
            "shelf_life_status",
            "remaining_min_days",
            "remaining_max_days",
            "eat_first_priority",
            "status"
        ])
        for r in results:
            writer.writerow([
                r["image"],
                r["food_prediction"],
                r["food_confidence"],
                r["objects"],
                r["freshness_prediction"],
                r["freshness_confidence"],
                r["shelf_life_status"],
                r["remaining_min_days"],
                r["remaining_max_days"],
                r["eat_first_priority"],
                r["status"]
            ])

    print(f"\nSaved CSV to: {CSV_OUT}")

    # Test FreshoBuddy Endpoint
    print("\nTesting FreshoBuddy Persistent Chat...")
    chat_payload = {
        "userId": "test_chef_101",
        "message": "How should I store fresh tomatoes?",
        "analysisContext": {
            "detectedFood": "Tomato",
            "freshness": {"label": "Fresh", "confidence": 100.0},
            "shelfLife": {"remaining": {"minDays": 5, "maxDays": 7}},
            "storageType": "countertop",
            "daysStored": 2
        }
    }
    chat_resp = requests.post(FRESHO_CHAT_URL, json=chat_payload, timeout=30)
    if chat_resp.status_code == 200:
        cdata = chat_resp.json()
        print(f"  Chat Success! Conversation ID: {cdata.get('conversationId')}")
        print(f"  Auto Title: {cdata.get('title')}")
        print(f"  Reply snippet: {cdata.get('reply', {}).get('text')[:90]}...")
    else:
        print(f"  Chat Error: {chat_resp.status_code} {chat_resp.text}")

    # Test Conversation Retrieval
    list_resp = requests.get(f"{FRESHO_CONVS_URL}?user_id=test_chef_101")
    if list_resp.status_code == 200:
        convs = list_resp.json().get("conversations", [])
        print(f"  Retrieved {len(convs)} conversations for user test_chef_101 from SQLite.")


if __name__ == "__main__":
    main()
