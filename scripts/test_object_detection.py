"""
FoodFresh AI - Real-World Object Detection Test Script (Phase 17)
Evaluates Grounding DINO on real-world food and kitchen scene images.
Saves reports/object_detection_real_world_test.csv and reports/object_detection_test_report.md.
"""

import csv
import json
import logging
from pathlib import Path
import sys
import time
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_object_detection")

EVAL_DIR = PROJECT_ROOT / "data" / "real_world_eval"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_REPORT = REPORTS_DIR / "object_detection_real_world_test.csv"
MD_REPORT = REPORTS_DIR / "object_detection_test_report.md"

API_URL = "http://127.0.0.1:8000/api/food-recognition/predict"


def post_multipart_image(url: str, file_path: Path, storage_type: str = "countertop", days_stored: int = 2) -> dict:
    """Send multipart image upload to running FastAPI backend."""
    boundary = "----WebKitFormBoundaryFoodFreshAITest"
    body = bytearray()

    fields = {"storage_type": storage_type, "days_stored": str(days_stored)}
    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8"))

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    filename = file_path.name
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: image/jpeg\r\n\r\n'.encode("utf-8"))
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_object_detection_tests():
    test_images = [
        EVAL_DIR / "pomegranate.jpg",
        EVAL_DIR / "apple.jpg",
        EVAL_DIR / "orange.jpg",
        EVAL_DIR / "banana.jpg",
        EVAL_DIR / "tomato.jpg",
        EVAL_DIR / "mango.jpg",
        EVAL_DIR / "bread.jpg",
        EVAL_DIR / "multi_apple_banana_tomato.jpg",
    ]

    records = []

    print("\n" + "=" * 80)
    print("FOODFRESH AI - GROUNDING DINO OBJECT DETECTION REAL-WORLD TEST")
    print("=" * 80)

    for img_path in test_images:
        if not img_path.exists():
            logger.warning(f"File {img_path} not found. Skipping.")
            continue

        rel_name = img_path.name
        logger.info(f"Testing image via API: {rel_name}")

        try:
            start_t = time.perf_counter()
            data = post_multipart_image(API_URL, img_path)
            elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 1)

            detected_food = data.get("detectedFood") or "Uncertain / None"
            raw_objects = data.get("detectedObjects", [])
            scene_objects = [o.get("label") for o in raw_objects]
            scene_confs = [f"{o.get('confidence', 0):.1f}%" for o in raw_objects]
            num_objects = len(raw_objects)
            status = "SUCCESS" if data.get("success") else "FAILED"

            dino_meta = data.get("foodRecognition", {}).get("groundingDino", {})
            all_raw_dino = [f"{o.get('label')} ({o.get('confidence', 0):.1f}%)" for o in dino_meta.get("objects", [])]

            record = {
                "image": rel_name,
                "detected_food": detected_food,
                "objects": " | ".join(scene_objects) if scene_objects else "none",
                "object_confidences": " | ".join(scene_confs) if scene_confs else "none",
                "number_of_objects": num_objects,
                "status": status,
                "latency_ms": elapsed_ms,
                "all_dino_objects": all_raw_dino,
                "shelf_life": data.get("shelfLife", {}),
                "eat_first": data.get("eatFirstPriority", {})
            }
            records.append(record)

            print(f"\n[Image: {rel_name}]")
            print(f"  • Detected Food: {detected_food} ({data.get('recognitionConfidence')}%)")
            print(f"  • Scene Objects: {record['objects']}")
            print(f"  • Object Confidences: {record['object_confidences']}")
            print(f"  • Number of Scene Objects: {num_objects}")
            print(f"  • Shelf-Life: {data.get('shelfLife', {}).get('status')} ({data.get('shelfLife', {}).get('remaining')})")
            print(f"  • Eat First: {data.get('eatFirstPriority', {}).get('priority')} - {data.get('eatFirstPriority', {}).get('reason')}")
            print(f"  • Status: {status} ({elapsed_ms}ms)")

        except Exception as e:
            logger.error(f"Error testing {rel_name}: {e}", exc_info=True)
            records.append({
                "image": rel_name,
                "detected_food": "ERROR",
                "objects": "none",
                "object_confidences": "none",
                "number_of_objects": 0,
                "status": f"ERROR: {e}",
                "latency_ms": 0.0,
                "all_dino_objects": []
            })


    # Save CSV
    with open(CSV_REPORT, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["image", "detected_food", "objects", "object_confidences", "number_of_objects", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "image": r["image"],
                "detected_food": r["detected_food"],
                "objects": r["objects"],
                "object_confidences": r["object_confidences"],
                "number_of_objects": r["number_of_objects"],
                "status": r["status"]
            })

    logger.info(f"Saved CSV report to {CSV_REPORT}")

    # Generate Markdown Report
    generate_markdown_report(records)
    logger.info(f"Saved Markdown report to {MD_REPORT}")


def generate_markdown_report(records):
    md = []
    md.append("# FoodFresh AI — Grounding DINO Object Detection Evaluation Report\n")
    md.append("**Date:** September 2026  \n")
    md.append("**Model:** IDEA-Research/grounding-dino-base  \n")
    md.append("**Task:** Open-vocabulary scene context and kitchen object detection  \n")
    md.append("**Controlled Vocabulary:** `table`, `countertop`, `plate`, `bowl`, `spoon`, `fork`, `knife`, `glass`, `cup`, `tray`, `container`, `basket`, `cutting board`, `bag`, `food`, `fruit`, `vegetable`\n\n")

    md.append("## 1. Executive Summary\n")
    md.append(
        "Grounding DINO is utilized as an open-vocabulary object detector operating in dual mode: "
        "first isolating candidate food regions for high-resolution specialist classification, "
        "and second identifying ambient kitchen objects (e.g., plates, countertops, cutting boards, bowls) "
        "to contextualize produce storage and consumption environments.\n\n"
    )

    md.append("## 2. Real-World Test Results\n\n")
    md.append("| Image | Primary Detected Food | Scene Objects Detected | Confidences | Count | Status |\n")
    md.append("|---|---|---|---|:---:|:---:|\n")
    for r in records:
        objs = r["objects"] if r["objects"] != "none" else "*No additional scene objects*"
        confs = r["object_confidences"] if r["object_confidences"] != "none" else "-"
        md.append(f"| `{r['image']}` | **{r['detected_food']}** | {objs} | {confs} | {r['number_of_objects']} | `{r['status']}` |\n")

    md.append("\n## 3. Detailed Per-Image Analysis\n\n")
    for r in records:
        md.append(f"### `{r['image']}`\n")
        md.append(f"- **Primary Food Recognized:** {r['detected_food']}\n")
        md.append(f"- **Scene Objects Isolated:** {r['objects']}\n")
        md.append(f"- **Scene Confidences:** {r['object_confidences']}\n")
        md.append(f"- **All Raw DINO Detections:** {', '.join(r.get('all_dino_objects', [])) or 'None'}\n")
        md.append(f"- **Pipeline Execution Time:** {r.get('latency_ms', 0)} ms\n\n")

    md.append("## 4. Key Findings and Methodology\n")
    md.append(
        "1. **Food Deduplication:** When a food item (e.g. Apple) is identified as the primary produce, "
        "duplicate food labels are suppressed from the secondary scene object caption.\n"
        "2. **Confidence-Sorted Presentation:** Scene objects are ranked strictly by model confidence, "
        "ensuring the most prominent context elements appear first (e.g., Plate · Table · Countertop).\n"
        "3. **Maximum Limit Enforcement:** At most 5 useful scene objects are presented to keep the user interface uncluttered.\n"
        "4. **No-Object Graceful Fallback:** Images featuring isolated produce without background containers correctly report "
        "`No additional scene objects detected.` without throwing errors or breaking UI cards.\n"
    )

    with open(MD_REPORT, "w", encoding="utf-8") as f:
        f.write("".join(md))


if __name__ == "__main__":
    run_object_detection_tests()
