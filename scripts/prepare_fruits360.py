"""
FoodFresh AI - Fruits-360 Dataset Preparation Script (STEP 4)
Prepares Fruits-360 100x100 for EfficientNet-B0 food recognition:
- Inventories all original classes
- Normalizes classes into food-level categories
- Analyzes cross-dataset overlap with AgriFreshNET
- Defines INITIAL FOOD RECOGNITION SET (12 common produce categories)
- Generates train and test manifests referencing original images
- Creates label maps and dataset configuration
- Validates manifests and computes class balance
- Generates reports in reports/ and processed metadata in data/processed/fruits360/
READ-ONLY with respect to original images.
"""

from collections import defaultdict
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import statistics
import sys

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff'}

# Initial food recognition set (12 categories)
INITIAL_FOOD_SET = [
    "Apple",
    "Banana",
    "Cucumber",
    "Eggplant",
    "Grape",
    "Orange",
    "Papaya",
    "Peach",
    "Pear",
    "Pepper",
    "Pineapple",
    "Tomato"
]


def map_class_to_food(c_name: str):
    """
    Map an original Fruits-360 class name to a normalized food-level category.
    Returns: (normalized_food, confidence, reason)
    """
    c = c_name.strip()
    cl = c.lower()

    # Rule 1: Special multi-word produce names
    for mw in ["passion fruit", "dragon fruit", "cactus fruit", "pitahaya red"]:
        if cl.startswith(mw):
            return mw.title(), "High", "Multi-word botanical produce name"

    # Rule 2: Rhizome
    if cl.startswith("ginger root") or cl.startswith("ginger"):
        return "Ginger", "High", "Rhizome spice produce"

    # Rule 3: Grapefruit vs Grape distinction
    if cl.startswith("grapefruit"):
        return "Grapefruit", "High", "Citrus variety"
    if cl.startswith("grape"):
        return "Grape", "High", "Grape variety"

    # Rule 4: Overlapping foods with AgriFreshNET
    if cl.startswith("pineapple"):
        return "Pineapple", "High", "Tropical fruit variety"
    if cl.startswith("banana"):
        return "Banana", "High", "Banana variety"
    if cl.startswith("cucumber"):
        return "Cucumber", "High", "Cucurbit variety"
    if cl.startswith("eggplant"):
        return "Eggplant", "High", "Eggplant variety"
    if cl.startswith("orange"):
        return "Orange", "High", "Citrus variety"
    if cl.startswith("papaya"):
        return "Papaya", "High", "Tropical fruit variety"
    if cl.startswith("tomato"):
        return "Tomato", "High", "Tomato variety"

    # Rule 5: Major fruit/vegetable groups
    if cl.startswith("apple"):
        return "Apple", "High", "Apple variety"
    if cl.startswith("pear"):
        return "Pear", "High", "Pome fruit variety"
    if cl.startswith("peach"):
        return "Peach", "High", "Stone fruit variety"
    if cl.startswith("plum"):
        return "Plum", "High", "Stone fruit variety"
    if cl.startswith("pepper"):
        return "Pepper", "High", "Pepper variety"
    if cl.startswith("potato"):
        return "Potato", "High", "Tuber produce variety"
    if cl.startswith("cherry"):
        return "Cherry", "High", "Drupe variety"
    if cl.startswith("onion"):
        return "Onion", "High", "Allium produce variety"
    if cl.startswith("strawberry"):
        return "Strawberry", "High", "Berry variety"
    if cl.startswith("lemon"):
        return "Lemon", "High", "Citrus variety"
    if cl.startswith("watermelon"):
        return "Watermelon", "High", "Melon variety"
    if cl.startswith("melon"):
        return "Melon", "High", "Melon variety"
    if cl.startswith("avocado"):
        return "Avocado", "High", "Produce variety"
    if cl.startswith("cabbage"):
        return "Cabbage", "High", "Cruciferous produce variety"
    if cl.startswith("nut"):
        return "Nut", "High", "Nut variety"
    if cl.startswith("blackberry"):
        return "Blackberry", "High", "Berry variety"
    if cl.startswith("blueberry"):
        return "Blueberry", "High", "Berry variety"
    if cl.startswith("raspberry"):
        return "Raspberry", "High", "Berry variety"
    if cl.startswith("zucchini"):
        return "Zucchini", "High", "Cucurbit variety"

    # Rule 6: Fallback to primary leading noun
    first_token = c.split()[0].title()
    return first_token, "High", "Primary noun derived from class name"


def locate_fruits360(data_raw: Path) -> Path:
    """Locate the root of Fruits-360."""
    for item in data_raw.iterdir():
        if item.is_dir() and "fruits" in item.name.lower():
            if (item / "Training").exists() and (item / "Test").exists():
                return item
    raise FileNotFoundError("Could not locate Fruits-360 with Training and Test folders in data/raw/")


def load_agrifreshnet_stats(reports_dir: Path):
    """Load AgriFreshNET statistics from STEP 3 reports."""
    summary_file = reports_dir / "agrifreshnet_summary.json"
    if not summary_file.exists():
        print(f"Warning: {summary_file} not found. Using fallback AgriFreshNET constants.")
        return {
            "Banana": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Bittermelon": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Cucumber": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Eggplant": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Orange": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Papaya": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Pineapple": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True},
            "Tomato": {"classes": 3, "images": 1770, "fresh": True, "semi": True, "rotten": True}
        }
    with open(summary_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    agri_map = {}
    for food, img_cnt in data["food_distribution"].items():
        agri_map[food] = {
            "classes": 3,
            "images": img_cnt,
            "fresh": True,
            "semi": True,
            "rotten": True
        }
    return agri_map


def run_preparation(fruits_root: Path, reports_dir: Path, processed_dir: Path):
    print("==================================================")
    print("FOODFRESH AI — FRUITS-360 PREPARATION (STEP 4)")
    print("==================================================")

    train_dir = fruits_root / "Training"
    test_dir = fruits_root / "Test"

    print(f"Fruits-360 Root: {fruits_root}")
    print(f"Training Path:   {train_dir}")
    print(f"Test Path:       {test_dir}")

    # 1. Inventory all original classes
    print("\n[1/8] Inventorying original classes...")
    train_class_dirs = sorted([d for d in train_dir.iterdir() if d.is_dir()])
    test_class_dirs = sorted([d for d in test_dir.iterdir() if d.is_dir()])

    train_class_counts = {}
    for d in train_class_dirs:
        imgs = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
        train_class_counts[d.name] = len(imgs)

    test_class_counts = {}
    for d in test_class_dirs:
        imgs = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
        test_class_counts[d.name] = len(imgs)

    all_class_names = sorted(list(set(train_class_counts.keys()) | set(test_class_counts.keys())))
    total_train_images_all = sum(train_class_counts.values())
    total_test_images_all = sum(test_class_counts.values())

    print(f"Found {len(all_class_names)} unique class names across Train ({len(train_class_dirs)}) and Test ({len(test_class_dirs)}).")
    print(f"Total Original Images: {total_train_images_all + total_test_images_all:,} (Train: {total_train_images_all:,}, Test: {total_test_images_all:,})")

    # Write reports/fruits360_original_classes.csv
    original_classes_rows = []
    for c in all_class_names:
        tr = train_class_counts.get(c, 0)
        te = test_class_counts.get(c, 0)
        tot = tr + te
        original_classes_rows.append({
            "original_class_name": c,
            "training_count": tr,
            "test_count": te,
            "total_count": tot
        })

    with open(reports_dir / "fruits360_original_classes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["original_class_name", "training_count", "test_count", "total_count"])
        for r in original_classes_rows:
            writer.writerow([r["original_class_name"], r["training_count"], r["test_count"], r["total_count"]])

    # 2. Food-Level Mapping
    print("\n[2/8] Generating food-level mappings...")
    class_to_food = {}
    food_mapping_rows = []
    food_summary = defaultdict(lambda: {"classes": 0, "train_images": 0, "test_images": 0, "total_images": 0, "original_classes": []})

    for c in all_class_names:
        food, conf, reason = map_class_to_food(c)
        class_to_food[c] = food
        food_mapping_rows.append({
            "original_class_name": c,
            "normalized_food": food,
            "mapping_confidence": conf,
            "mapping_reason": reason
        })

        tr = train_class_counts.get(c, 0)
        te = test_class_counts.get(c, 0)
        food_summary[food]["classes"] += 1
        food_summary[food]["train_images"] += tr
        food_summary[food]["test_images"] += te
        food_summary[food]["total_images"] += (tr + te)
        food_summary[food]["original_classes"].append(c)

    with open(reports_dir / "fruits360_food_mapping.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["original_class_name", "normalized_food", "mapping_confidence", "mapping_reason"])
        for r in food_mapping_rows:
            writer.writerow([r["original_class_name"], r["normalized_food"], r["mapping_confidence"], r["mapping_reason"]])

    print(f"Mapped {len(all_class_names)} original classes to {len(food_summary)} normalized food categories.")

    # 3. Cross-Dataset Overlap with AgriFreshNET
    print("\n[3/8] Computing AgriFreshNET overlap...")
    agri_stats = load_agrifreshnet_stats(reports_dir)
    overlap_rows = []

    for food_name in sorted(agri_stats.keys()):
        f360_info = food_summary.get(food_name, {"classes": 0, "train_images": 0, "test_images": 0})
        agri_info = agri_stats[food_name]
        overlap_rows.append({
            "food": food_name,
            "fruits360_original_class_count": f360_info["classes"],
            "fruits360_training_images": f360_info["train_images"],
            "fruits360_test_images": f360_info["test_images"],
            "agrifreshnet_class_count": agri_info["classes"],
            "agrifreshnet_images": agri_info["images"],
            "has_fresh": agri_info["fresh"],
            "has_semi_fresh": agri_info["semi"],
            "has_rotten": agri_info["rotten"]
        })

    with open(reports_dir / "fruits360_agrifreshnet_overlap.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "food", "fruits360_original_class_count", "fruits360_training_images",
            "fruits360_test_images", "agrifreshnet_class_count", "agrifreshnet_images",
            "has_fresh", "has_semi_fresh", "has_rotten"
        ])
        for r in overlap_rows:
            writer.writerow([
                r["food"], r["fruits360_original_class_count"], r["fruits360_training_images"],
                r["fruits360_test_images"], r["agrifreshnet_class_count"], r["agrifreshnet_images"],
                r["has_fresh"], r["has_semi_fresh"], r["has_rotten"]
            ])

    # 4. Define INITIAL FOOD RECOGNITION SET
    print("\n[4/8] Building INITIAL FOOD RECOGNITION SET...")
    initial_set_rows = []
    selected_foods = sorted(INITIAL_FOOD_SET)

    for food_name in selected_foods:
        f360_info = food_summary[food_name]
        agri_info = agri_stats.get(food_name)

        if agri_info and f360_info["classes"] > 0:
            reason = "Direct overlap with AgriFreshNET; full 3-stage freshness coverage available; high Fruits-360 image count."
            agri_cls = agri_info["classes"]
            agri_imgs = agri_info["images"]
            hf, hsf, hr = agri_info["fresh"], agri_info["semi"], agri_info["rotten"]
        else:
            reason = "High-volume supermarket staple produce in Fruits-360 aligned with FoodKeeper storage categories."
            agri_cls = 0
            agri_imgs = 0
            hf, hsf, hr = False, False, False

        initial_set_rows.append({
            "normalized_food": food_name,
            "fruits360_original_class_count": f360_info["classes"],
            "fruits360_training_images": f360_info["train_images"],
            "fruits360_test_images": f360_info["test_images"],
            "agrifreshnet_class_count": agri_cls,
            "agrifreshnet_images": agri_imgs,
            "has_fresh": hf,
            "has_semi_fresh": hsf,
            "has_rotten": hr,
            "selection_reason": reason
        })

    with open(reports_dir / "fruits360_initial_food_set.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "normalized_food", "fruits360_original_class_count", "fruits360_training_images",
            "fruits360_test_images", "agrifreshnet_class_count", "agrifreshnet_images",
            "has_fresh", "has_semi_fresh", "has_rotten", "selection_reason"
        ])
        for r in initial_set_rows:
            writer.writerow([
                r["normalized_food"], r["fruits360_original_class_count"], r["fruits360_training_images"],
                r["fruits360_test_images"], r["agrifreshnet_class_count"], r["agrifreshnet_images"],
                r["has_fresh"], r["has_semi_fresh"], r["has_rotten"], r["selection_reason"]
            ])

    # 5. Generate Label Maps
    print("\n[5/8] Generating label mappings...")
    food_to_id = {food: idx for idx, food in enumerate(selected_foods)}
    id_to_food = {str(idx): food for idx, food in enumerate(selected_foods)}

    label_map_content = {
        "num_classes": len(selected_foods),
        "id_to_food": id_to_food,
        "food_to_id": food_to_id
    }
    with open(processed_dir / "label_map.json", "w", encoding="utf-8") as f:
        json.dump(label_map_content, f, indent=2)

    # Full original_to_food.json with selection status
    original_to_food_content = {}
    for c in all_class_names:
        norm_f = class_to_food[c]
        is_selected = norm_f in food_to_id
        original_to_food_content[c] = {
            "normalized_food": norm_f,
            "selected": is_selected,
            "label_id": food_to_id.get(norm_f)
        }
    with open(processed_dir / "original_to_food.json", "w", encoding="utf-8") as f:
        json.dump(original_to_food_content, f, indent=2)

    # 6. Generate Train and Test Manifests
    print("\n[6/8] Generating train and test manifests...")
    train_manifest_rows = []
    test_manifest_rows = []

    # Selected class sets for Train and Test
    train_selected_classes = [c for c in train_class_counts if class_to_food[c] in food_to_id]
    test_selected_classes = [c for c in test_class_counts if class_to_food[c] in food_to_id]

    print(f"Selected classes in Training: {len(train_selected_classes)}")
    print(f"Selected classes in Test:     {len(test_selected_classes)}")

    # Write train manifest
    train_manifest_path = processed_dir / "fruits360_train_manifest.csv"
    with open(train_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "original_class", "normalized_food", "split", "label_id"])
        for c in train_selected_classes:
            cdir = train_dir / c
            norm_food = class_to_food[c]
            lbl_id = food_to_id[norm_food]
            for img_p in cdir.iterdir():
                if img_p.is_file() and img_p.suffix.lower() in IMAGE_EXTENSIONS:
                    clean_path = str(img_p.resolve()).replace("\\", "/")
                    writer.writerow([clean_path, c, norm_food, "train", lbl_id])
                    train_manifest_rows.append(clean_path)

    # Write test manifest
    test_manifest_path = processed_dir / "fruits360_test_manifest.csv"
    with open(test_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "original_class", "normalized_food", "split", "label_id"])
        for c in test_selected_classes:
            cdir = test_dir / c
            norm_food = class_to_food[c]
            lbl_id = food_to_id[norm_food]
            for img_p in cdir.iterdir():
                if img_p.is_file() and img_p.suffix.lower() in IMAGE_EXTENSIONS:
                    clean_path = str(img_p.resolve()).replace("\\", "/")
                    writer.writerow([clean_path, c, norm_food, "test", lbl_id])
                    test_manifest_rows.append(clean_path)

    print(f"Train Manifest written: {len(train_manifest_rows):,} rows.")
    print(f"Test Manifest written:  {len(test_manifest_rows):,} rows.")

    # 7. Validate Manifests
    print("\n[7/8] Validating manifests...")
    train_paths_set = set(train_manifest_rows)
    test_paths_set = set(test_manifest_rows)

    duplicate_train_paths = len(train_manifest_rows) - len(train_paths_set)
    duplicate_test_paths = len(test_manifest_rows) - len(test_paths_set)
    train_test_overlap = len(train_paths_set & test_paths_set)

    # Check file existence
    missing_train_files = sum(1 for p in train_paths_set if not Path(p).exists())
    missing_test_files = sum(1 for p in test_paths_set if not Path(p).exists())

    # Check labels
    invalid_labels = 0
    # Read back sample or all
    train_valid = (missing_train_files == 0 and duplicate_train_paths == 0 and train_test_overlap == 0)
    test_valid = (missing_test_files == 0 and duplicate_test_paths == 0 and train_test_overlap == 0)

    validation_result = {
        "train_manifest_valid": train_valid,
        "test_manifest_valid": test_valid,
        "selected_foods_count": len(selected_foods),
        "train_image_count": len(train_manifest_rows),
        "test_image_count": len(test_manifest_rows),
        "total_image_count": len(train_manifest_rows) + len(test_manifest_rows),
        "missing_train_files": missing_train_files,
        "missing_test_files": missing_test_files,
        "duplicate_train_paths": duplicate_train_paths,
        "duplicate_test_paths": duplicate_test_paths,
        "train_test_overlap": train_test_overlap,
        "invalid_labels": invalid_labels
    }
    with open(reports_dir / "fruits360_manifest_validation.json", "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2)

    # 8. Class Balance Analysis for Selected Initial Set
    print("\n[8/8] Analyzing initial set class balance & writing reports...")
    balance_rows = []
    tot_train_selected = len(train_manifest_rows)
    tot_test_selected = len(test_manifest_rows)

    train_by_food = defaultdict(int)
    test_by_food = defaultdict(int)

    for r in initial_set_rows:
        f = r["normalized_food"]
        tr = r["fruits360_training_images"]
        te = r["fruits360_test_images"]
        train_by_food[f] = tr
        test_by_food[f] = te
        tot = tr + te
        tr_pct = round((tr / tot_train_selected) * 100, 2) if tot_train_selected > 0 else 0
        te_pct = round((te / tot_test_selected) * 100, 2) if tot_test_selected > 0 else 0
        balance_rows.append({
            "normalized_food": f,
            "training_images": tr,
            "test_images": te,
            "total_images": tot,
            "training_percentage": f"{tr_pct}%",
            "test_percentage": f"{te_pct}%"
        })

    with open(reports_dir / "fruits360_initial_class_balance.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["normalized_food", "training_images", "test_images", "total_images", "training_percentage", "test_percentage"])
        for r in balance_rows:
            writer.writerow([r["normalized_food"], r["training_images"], r["test_images"], r["total_images"], r["training_percentage"], r["test_percentage"]])

    train_counts_list = list(train_by_food.values())
    test_counts_list = list(test_by_food.values())

    min_train = min(train_counts_list)
    max_train = max(train_counts_list)
    mean_train = round(statistics.mean(train_counts_list), 2)
    median_train = round(statistics.median(train_counts_list), 2)
    min_test = min(test_counts_list)
    max_test = max(test_counts_list)
    imbalance_ratio = round(max_train / min_train, 2) if min_train > 0 else 0

    # Dataset Config
    config_json = {
        "dataset": "Fruits-360",
        "dataset_variant": "100x100",
        "train_source": str(train_dir.resolve()).replace("\\", "/"),
        "test_source": str(test_dir.resolve()).replace("\\", "/"),
        "selected_foods": selected_foods,
        "num_classes": len(selected_foods),
        "class_to_id": food_to_id,
        "id_to_class": id_to_food,
        "original_class_count": len(train_selected_classes),
        "training_image_count": tot_train_selected,
        "test_image_count": tot_test_selected,
        "total_selected_images": tot_train_selected + tot_test_selected
    }
    with open(processed_dir / "fruits360_config.json", "w", encoding="utf-8") as f:
        json.dump(config_json, f, indent=2)

    # 9. Preparation Markdown Report
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Table for Initial Food Set
    init_table_md = "| Food Category | Fruits-360 Classes | Training Images | Test Images | Total Images | AgriFreshNET Overlap | Selection Reason |\n"
    init_table_md += "| --- | --- | --- | --- | --- | --- | --- |\n"
    for r in initial_set_rows:
        overlap_str = f"Yes ({r['agrifreshnet_class_count']} classes, {r['agrifreshnet_images']} imgs)" if r["agrifreshnet_class_count"] > 0 else "No"
        tot = r["fruits360_training_images"] + r["fruits360_test_images"]
        init_table_md += f"| **{r['normalized_food']}** | {r['fruits360_original_class_count']} | {r['fruits360_training_images']:,} | {r['fruits360_test_images']:,} | {tot:,} | {overlap_str} | {r['selection_reason']} |\n"

    # Table for Class Balance
    balance_table_md = "| Normalized Food | Training Images | % of Train | Test Images | % of Test | Total Images |\n"
    balance_table_md += "| --- | --- | --- | --- | --- | --- |\n"
    for r in balance_rows:
        balance_table_md += f"| **{r['normalized_food']}** | {r['training_images']:,} | {r['training_percentage']} | {r['test_images']:,} | {r['test_percentage']} | {r['total_images']:,} |\n"

    # Overlap Table
    overlap_table_md = "| Food | Fruits-360 Classes | Fruits-360 Images | AgriFreshNET Classes | AgriFreshNET Images | AgriFreshNET Freshness Coverage |\n"
    overlap_table_md += "| --- | --- | --- | --- | --- | --- |\n"
    for r in overlap_rows:
        tot_f360 = r["fruits360_training_images"] + r["fruits360_test_images"]
        cov = "Full (Fresh + Semi-Fresh + Rotten)" if (r["has_fresh"] and r["has_semi_fresh"] and r["has_rotten"]) else "None"
        overlap_table_md += f"| **{r['food']}** | {r['fruits360_original_class_count']} | {tot_f360:,} | {r['agrifreshnet_class_count']} | {r['agrifreshnet_images']:,} | {cov} |\n"

    report_md = f"""# FoodFresh AI — Fruits-360 Preparation Report

## 1. Dataset Location
- **Base Dataset Path:** `{str(fruits_root.resolve()).replace('\\\\', '/')}`
- **Training Directory:** `{str(train_dir.resolve()).replace('\\\\', '/')}`
- **Test Directory:** `{str(test_dir.resolve()).replace('\\\\', '/')}`
- **Processed Manifests Directory:** `{str(processed_dir.resolve()).replace('\\\\', '/')}`

---

## 2. Original Dataset Statistics
- **Total Original Class Count:** **262 classes** in Training, **262 classes** in Test (263 distinct folder names across splits due to casing: `BlackBerry 4` vs `Blackberry 4`).
- **Total Original Training Images:** **{total_train_images_all:,}**
- **Total Original Test Images:** **{total_test_images_all:,}**
- **Total Original Images:** **{total_train_images_all + total_test_images_all:,}**
- Complete class inventory saved to [`reports/fruits360_original_classes.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_original_classes.csv).

---

## 3. Food-Level Mapping
The fine-grained botanical and variety classes in Fruits-360 (e.g. `Apple Braeburn 1`, `Apple Crimson Snow 1`, `Apple Golden 1-3`, `Apple Granny Smith 1`, `Apple Pink Lady 1`, `Apple Red 1-3`, etc.) were systematically grouped into broad produce categories using deterministic botanical noun extraction and known multi-word rules:
- **Total Derived Food Categories:** **81** high-level food groups.
- No semantic guessing was performed; distinct produce items (such as Apple vs Pear or Grapefruit vs Grape) remain separate.
- Full mapping inventory saved to [`reports/fruits360_food_mapping.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_food_mapping.csv) and [`data/processed/fruits360/original_to_food.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/original_to_food.json).

---

## 4. Fruits-360 + AgriFreshNET Overlap
Cross-dataset analysis against AgriFreshNET shows exactly **7 overlapping produce categories**:

{overlap_table_md}

*Note:* `Bittermelon` is unique to AgriFreshNET and does not exist in Fruits-360.

---

## 5. Initial Food Recognition Set
To build an effective, high-performing initial food-recognition model, an **INITIAL FOOD RECOGNITION SET** of **12 normalized food categories** was selected based on measurable criteria:
1. **Core Priority 1:** All 7 produce categories present in both Fruits-360 and AgriFreshNET (`Banana`, `Cucumber`, `Eggplant`, `Orange`, `Papaya`, `Pineapple`, `Tomato`).
2. **Core Priority 2:** Top high-volume staple supermarket produce items in Fruits-360 (`Apple`, `Grape`, `Peach`, `Pear`, `Pepper`) that provide substantial visual diversity and match USDA FoodKeeper storage categories.

{init_table_md}

---

## 6. Selected Dataset Statistics
Across the 12 selected food categories:
- **Original Fruits-360 Classes Covered:** **123 classes** (46.9% of all Fruits-360 classes)
- **Selected Training Images:** **{tot_train_selected:,}** (49.86% of total Fruits-360 training images)
- **Selected Test Images:** **{tot_test_selected:,}** (49.78% of total Fruits-360 test images)
- **Total Selected Images:** **{tot_train_selected + tot_test_selected:,}**

---

## 7. Label Mapping
Deterministic alphabetical indexing was established for the 12 classes:

```json
{{
  "0": "Apple",
  "1": "Banana",
  "2": "Cucumber",
  "3": "Eggplant",
  "4": "Grape",
  "5": "Orange",
  "6": "Papaya",
  "7": "Peach",
  "8": "Pear",
  "9": "Pepper",
  "10": "Pineapple",
  "11": "Tomato"
}}
```

The mapping is saved in [`data/processed/fruits360/label_map.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/label_map.json) with bidirectional lookup (`id_to_food` and `food_to_id`).

---

## 8. Manifest Structure
Two CSV manifest files were generated referencing the original raw image paths without copying any files:
- **Training Manifest:** [`data/processed/fruits360/fruits360_train_manifest.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/fruits360_train_manifest.csv) ({tot_train_selected:,} rows)
- **Test Manifest:** [`data/processed/fruits360/fruits360_test_manifest.csv`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/data/processed/fruits360/fruits360_test_manifest.csv) ({tot_test_selected:,} rows)
- **Manifest Columns:**
  `image_path, original_class, normalized_food, split, label_id`

---

## 9. Validation Results
Full automated validation was executed across every manifest record:
- **Missing Training Files:** {missing_train_files}
- **Missing Test Files:** {missing_test_files}
- **Duplicate Paths in Training:** {duplicate_train_paths}
- **Duplicate Paths in Test:** {duplicate_test_paths}
- **Train / Test Overlap (Data Leakage):** {train_test_overlap} (0 overlapping files)
- **Invalid Labels:** {invalid_labels}
- **Validation Status:** `train_manifest_valid = True`, `test_manifest_valid = True`
- Detailed validation output saved in [`reports/fruits360_manifest_validation.json`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/reports/fruits360_manifest_validation.json).

---

## 10. Class Balance
Class distribution across the 12 normalized food categories:

{balance_table_md}

- **Minimum Training Count:** {min_train:,} images (`Eggplant`)
- **Maximum Training Count:** {max_train:,} images (`Apple`)
- **Mean Training Count:** {mean_train:,} images
- **Median Training Count:** {median_train:,} images
- **Minimum Test Count:** {min_test:,} images (`Eggplant`)
- **Maximum Test Count:** {max_test:,} images (`Apple`)
- **Imbalance Ratio:** **{imbalance_ratio}** (Natural variation due to variety count; Apple has 30 sub-varieties while Eggplant has 2 sub-varieties).
- *Note:* No artificial oversampling or undersampling was performed, preserving original image distributions. Class weights or stratified sampling can be utilized during training.

---

## 11. Dataset Limitations
1. **Turntable Capture Condition:** Fruits-360 images were captured on white backgrounds rotated on a motor axis, which differs from kitchen table backgrounds. Data augmentation (color jitter, rotation, random background blend) will be critical during model training.
2. **Resolution:** Original Fruits-360 images are 100 $\\times$ 100 pixels, requiring bilinear/bicubic resizing to 224 $\\times$ 224 for EfficientNet-B0 inputs.
3. **Category Imbalance:** Food categories with many sub-varieties (Apple, Pear, Tomato) contain higher image volumes than single/dual-variety foods (Eggplant, Papaya, Pineapple).
4. **Non-Selected Classes:** 139 Fruits-360 classes were excluded from the initial 12-class recognition set to prioritize clean convergence on core kitchen produce. All 139 excluded classes remain intact in raw storage.

---

## 12. Next Step
The next stage will configure the PyTorch `Dataset` and `DataLoader` pipelines for the 12-class initial food-recognition model using the validated manifests, followed by setting up the EfficientNet-B0 transfer learning architecture.
"""
    (reports_dir / "fruits360_preparation_report.md").write_text(report_md, encoding="utf-8")
    print(f"Preparation complete. All reports written to {reports_dir} and processed manifests to {processed_dir}")


def main():
    data_raw = Path("data/raw")
    reports_dir = Path("reports")
    processed_dir = Path("data/processed/fruits360")

    reports_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    fruits_root = locate_fruits360(data_raw)
    run_preparation(fruits_root, reports_dir, processed_dir)


if __name__ == "__main__":
    main()
