"""
FoodFresh AI - Fruits-360 V2 Dataset Preparation (STEP 12)
Prepares expanded 24-class food vocabulary including Pomegranate:
- Canonical contiguous label mapping (0 to 23)
- Train / Val / Test manifests (80/20 train/val split of Training set, untouched Test set)
- Comprehensive leakage verification
- Image validation & class balance analysis
"""

import csv
import json
import os
from pathlib import Path
import random
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fruits-360-100x100-main"
PROCESSED_V2_DIR = PROJECT_ROOT / "data" / "processed" / "fruits360_v2"
REPORTS_DIR = PROJECT_ROOT / "reports"

RANDOM_SEED = 42

# 24 Evidence-Based Selected Food Classes (sorted alphabetically)
V2_SELECTED_FOODS = [
    "Apple",
    "Avocado",
    "Banana",
    "Cherry",
    "Corn",
    "Cucumber",
    "Eggplant",
    "Grape",
    "Guava",
    "Lemon",
    "Mango",
    "Onion",
    "Orange",
    "Papaya",
    "Peach",
    "Pear",
    "Pepper",
    "Pineapple",
    "Plum",
    "Pomegranate",
    "Potato",
    "Strawberry",
    "Tomato",
    "Watermelon"
]


def map_raw_folder_to_food(folder_name: str) -> str:
    """Map raw Fruits-360 folder name to normalized food name."""
    fn = folder_name.strip()
    fl = fn.lower()

    # Rule 1: Direct matches
    for food in V2_SELECTED_FOODS:
        if fl.startswith(food.lower()):
            # Disambiguation:
            # Avoid matching 'Grapefruit' as 'Grape'
            if food == "Grape" and fl.startswith("grapefruit"):
                continue
            return food

    return None


def prepare_fruits360_v2():
    print("=" * 60)
    print("FOODFRESH AI - PREPARING FOOD RECOGNITION V2 DATASET")
    print("=" * 60)

    train_dir = RAW_DIR / "Training"
    test_dir = RAW_DIR / "Test"

    if not train_dir.exists() or not test_dir.exists():
        raise FileNotFoundError(f"Raw Fruits-360 directories not found at: {RAW_DIR}")

    PROCESSED_V2_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build authoritative V2 Label Map
    food_to_id = {food: idx for idx, food in enumerate(V2_SELECTED_FOODS)}
    id_to_food = {str(idx): food for idx, food in enumerate(V2_SELECTED_FOODS)}

    label_map = {
        "num_classes": len(V2_SELECTED_FOODS),
        "id_to_food": id_to_food,
        "food_to_id": food_to_id
    }

    label_map_path = PROCESSED_V2_DIR / "label_map.json"
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"Authoritative V2 label map saved: {label_map_path} ({len(V2_SELECTED_FOODS)} classes)")

    # 2. Map all raw folders and save original_to_food_v2.json
    all_raw_folders = sorted(os.listdir(train_dir))
    original_to_food_map = {}
    selected_raw_folders = []

    for folder in all_raw_folders:
        norm = map_raw_folder_to_food(folder)
        is_sel = norm is not None
        original_to_food_map[folder] = {
            "normalized_food": norm,
            "selected": is_sel,
            "class_id": food_to_id.get(norm) if is_sel else None
        }
        if is_sel:
            selected_raw_folders.append((folder, norm, food_to_id[norm]))

    with open(PROCESSED_V2_DIR / "original_to_food_v2.json", "w", encoding="utf-8") as f:
        json.dump(original_to_food_map, f, indent=2)

    print(f"Mapped {len(all_raw_folders)} raw folders. {len(selected_raw_folders)} selected for V2.")

    # 3. Gather raw image files for selected classes
    print("\nScanning raw image files...")
    raw_train_records = []
    raw_test_records = []

    for folder, norm_food, cls_id in selected_raw_folders:
        # Train folder
        tr_folder_path = train_dir / folder
        for fname in os.listdir(tr_folder_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                p = (tr_folder_path / fname).resolve().as_posix()
                raw_train_records.append({
                    "image_path": p,
                    "food_type": norm_food,
                    "class_id": cls_id,
                    "original_class": folder
                })

        # Test folder
        te_folder_name = folder if folder != "BlackBerry 4" else "Blackberry 4"
        te_folder_path = test_dir / te_folder_name
        if te_folder_path.exists():
            for fname in os.listdir(te_folder_path):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    p = (te_folder_path / fname).resolve().as_posix()
                    raw_test_records.append({
                        "image_path": p,
                        "food_type": norm_food,
                        "class_id": cls_id,
                        "original_class": folder
                    })

    print(f"Collected {len(raw_train_records)} raw training images and {len(raw_test_records)} raw test images.")

    # 4. Stratified Split of Training images: 80% Train, 20% Validation
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    train_df_full = pd.DataFrame(raw_train_records)
    test_df = pd.DataFrame(raw_test_records)

    train_rows = []
    val_rows = []

    # Stratify by (original_class) to preserve fine-grained distribution
    for orig_cls, group in train_df_full.groupby("original_class"):
        shuffled = group.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
        n_val = int(round(len(shuffled) * 0.20))
        # Ensure at least 1 val sample if folder has >= 5 images
        if n_val == 0 and len(shuffled) >= 5:
            n_val = 1
        val_rows.append(shuffled.iloc[:n_val])
        train_rows.append(shuffled.iloc[n_val:])

    train_df = pd.concat(train_rows, ignore_index=True)
    val_df = pd.concat(val_rows, ignore_index=True)

    print(f"Split results:")
    print(f"  Train:      {len(train_df)} images ({len(train_df)/(len(train_df)+len(val_df))*100:.2f}%)")
    print(f"  Validation: {len(val_df)} images ({len(val_df)/(len(train_df)+len(val_df))*100:.2f}%)")
    print(f"  Test:       {len(test_df)} images (100% untouched raw test set)")

    # 5. Data Leakage Verification
    print("\nRunning strict data leakage verification...")
    train_paths = set(train_df["image_path"])
    val_paths = set(val_df["image_path"])
    test_paths = set(test_df["image_path"])

    leak_tr_val = train_paths.intersection(val_paths)
    leak_tr_te = train_paths.intersection(test_paths)
    leak_val_te = val_paths.intersection(test_paths)

    leakage_report = {
        "random_seed": RANDOM_SEED,
        "train_image_count": len(train_df),
        "val_image_count": len(val_df),
        "test_image_count": len(test_df),
        "total_images": len(train_df) + len(val_df) + len(test_df),
        "leak_train_val_count": len(leak_tr_val),
        "leak_train_test_count": len(leak_tr_te),
        "leak_val_test_count": len(leak_val_te),
        "leakage_detected": bool(leak_tr_val or leak_tr_te or leak_val_te),
        "all_paths_unique": len(train_paths | val_paths | test_paths) == (len(train_df) + len(val_df) + len(test_df))
    }

    with open(REPORTS_DIR / "fruits360_v2_leakage_check.json", "w", encoding="utf-8") as f:
        json.dump(leakage_report, f, indent=2)

    assert not leakage_report["leakage_detected"], f"Data leakage detected! Tr-Val:{len(leak_tr_val)}, Tr-Te:{len(leak_tr_te)}, Val-Te:{len(leak_val_te)}"
    print("[OK] Verified: ZERO data leakage across train, val, and test splits.")

    # 6. Image Validation Check
    print("\nValidating image files with PIL...")
    all_dfs = [("train", train_df), ("val", val_df), ("test", test_df)]
    bad_records = []

    for split_name, df_split in all_dfs:
        for idx, row in df_split.iterrows():
            p = row["image_path"]
            if not os.path.exists(p):
                bad_records.append({"image_path": p, "split": split_name, "error": "File does not exist"})
                continue
            # Fast check header
            try:
                with Image.open(p) as img:
                    img.verify()
            except Exception as e:
                bad_records.append({"image_path": p, "split": split_name, "error": str(e)})

    bad_df = pd.DataFrame(bad_records)
    bad_df.to_csv(REPORTS_DIR / "fruits360_v2_bad_images.csv", index=False)
    print(f"[OK] Image validation complete: {len(bad_records)} corrupted images found.")

    # 7. Write V2 Manifests
    train_manifest_path = PROCESSED_V2_DIR / "fruits360_v2_train_manifest.csv"
    val_manifest_path = PROCESSED_V2_DIR / "fruits360_v2_val_manifest.csv"
    test_manifest_path = PROCESSED_V2_DIR / "fruits360_v2_test_manifest.csv"

    manifest_cols = ["image_path", "food_type", "class_id", "original_class"]
    train_df[manifest_cols].to_csv(train_manifest_path, index=False)
    val_df[manifest_cols].to_csv(val_manifest_path, index=False)
    test_df[manifest_cols].to_csv(test_manifest_path, index=False)

    print(f"Saved: {train_manifest_path}")
    print(f"Saved: {val_manifest_path}")
    print(f"Saved: {test_manifest_path}")

    # 8. Class Balance Analysis
    print("\nGenerating Class Balance report...")
    balance_records = []
    for food in V2_SELECTED_FOODS:
        cid = food_to_id[food]
        tr_c = (train_df["food_type"] == food).sum()
        val_c = (val_df["food_type"] == food).sum()
        te_c = (test_df["food_type"] == food).sum()
        tot = tr_c + val_c + te_c
        balance_records.append({
            "class_id": cid,
            "food_type": food,
            "train_count": tr_c,
            "val_count": val_c,
            "test_count": te_c,
            "total_count": tot,
            "train_pct": round(tr_c / tot * 100, 2),
            "val_pct": round(val_c / tot * 100, 2),
            "test_pct": round(te_c / tot * 100, 2)
        })

    balance_df = pd.DataFrame(balance_records)
    balance_df.to_csv(REPORTS_DIR / "fruits360_v2_class_balance.csv", index=False)
    print(f"Saved: {REPORTS_DIR / 'fruits360_v2_class_balance.csv'}")

    # Save V2 Config JSON
    config_v2 = {
        "dataset_name": "Fruits-360 V2",
        "num_classes": len(V2_SELECTED_FOODS),
        "selected_foods": V2_SELECTED_FOODS,
        "total_images": len(train_df) + len(val_df) + len(test_df),
        "train_count": len(train_df),
        "val_count": len(val_df),
        "test_count": len(test_df),
        "pomegranate_stats": {
            "class_id": food_to_id["Pomegranate"],
            "train_count": int((train_df["food_type"] == "Pomegranate").sum()),
            "val_count": int((val_df["food_type"] == "Pomegranate").sum()),
            "test_count": int((test_df["food_type"] == "Pomegranate").sum()),
            "total_count": int((test_df["food_type"] == "Pomegranate").sum() + (train_df["food_type"] == "Pomegranate").sum() + (val_df["food_type"] == "Pomegranate").sum())
        }
    }
    with open(PROCESSED_V2_DIR / "fruits360_v2_config.json", "w", encoding="utf-8") as f:
        json.dump(config_v2, f, indent=2)

    print("\nV2 Dataset Preparation successfully finished!")


if __name__ == "__main__":
    prepare_fruits360_v2()
