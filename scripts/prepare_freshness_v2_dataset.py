"""
FoodFresh AI - Prepare AgriFreshNET Freshness V2 Dataset
Leakage-safe group-aware splitting into train, validation, and test manifests.
Maps AgriFreshNET (Fresh, Semi-Fresh, Rotten) -> (fresh, slightly_spoiled, rotten).
"""

import os
import sys
import re
import json
import csv
import random
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGRI_BASE = PROJECT_ROOT / "data" / "raw" / "AgriFreshNET Freshness and Shelf-Life Image Datase" / "Processed Data" / "Processed Data"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "freshness_v2"

LABEL_MAP = {
    "fresh": 0,
    "rotten": 1,
    "slightly_spoiled": 2
}

INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

VOCAB = ["fresh", "rotten", "slightly_spoiled"]


def get_stage_and_commodity(folder_name: str):
    """
    Parse commodity and freshness stage from folder name.
    Folder patterns:
      'Fresh Banana(1-4)' -> stage: 'Fresh', commodity: 'banana'
      'Semi fresh banana(4-7)' -> stage: 'Semi-Fresh', commodity: 'banana'
      'Rotten banana(7-13)' -> stage: 'Rotten', commodity: 'banana'
    """
    fn = folder_name.strip()
    fl = fn.lower()

    if fl.startswith("fresh"):
        stage = "Fresh"
        target_class = "fresh"
    elif "semi" in fl:
        stage = "Semi-Fresh"
        target_class = "slightly_spoiled"
    elif fl.startswith("rotten"):
        stage = "Rotten"
        target_class = "rotten"
    else:
        raise ValueError(f"Unknown freshness folder pattern: {folder_name}")

    # Extract commodity
    clean = re.sub(r'\(.*?\)', '', fn).strip()
    clean = re.sub(r'^(fresh|semi fresh|semi_fresh|rotten)\s*', '', clean, flags=re.IGNORECASE).strip()
    commodity = clean.lower()

    return stage, target_class, commodity


def get_capture_group_id(filename: str) -> str:
    """
    Extract original capture ID to prevent data leakage across augmentations.
    aug_0_IMG_20251104_131910090_HDR_AE~2.jpg -> IMG_20251104_131910090_HDR_AE
    """
    stem = os.path.splitext(filename)[0]
    # Remove aug_XXX_ prefix
    stem = re.sub(r'^aug_\d+_', '', stem, flags=re.IGNORECASE)
    # Remove suffix variations like ~2, (1), etc.
    stem = re.sub(r'~.*$', '', stem)
    stem = re.sub(r'\s*\(\d+\)$', '', stem)
    return stem


def main():
    print("=" * 60)
    print("PREPARING AGRIFRESHNET FRESHNESS V2 DATASET")
    print("=" * 60)

    if not AGRI_BASE.exists():
        print(f"Error: AgriFreshNET directory not found at {AGRI_BASE}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Collect all images and index by group
    # Group structure: group_key -> list of record dicts
    groups = defaultdict(list)
    total_images = 0

    for folder in sorted(os.listdir(AGRI_BASE)):
        folder_path = AGRI_BASE / folder
        if not folder_path.is_dir():
            continue

        stage, target_class, commodity = get_stage_and_commodity(folder)
        target_idx = LABEL_MAP[target_class]

        for fname in sorted(os.listdir(folder_path)):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            rel_path = str((folder_path / fname).relative_to(PROJECT_ROOT)).replace("\\", "/")
            cap_id = get_capture_group_id(fname)
            group_key = f"{folder}::{cap_id}"

            record = {
                "filepath": rel_path,
                "filename": fname,
                "commodity": commodity,
                "source_stage": stage,
                "target_class": target_class,
                "label": target_idx,
                "group_id": group_key
            }
            groups[group_key].append(record)
            total_images += 1

    print(f"Discovered {total_images} images across {len(groups)} unique capture groups.")

    # 2. Stratified Group Splitting
    # We want ~70% train, 15% validation, 15% test
    # Stratified by target_class
    random.seed(42)

    class_to_groups = defaultdict(list)
    for g_key, recs in groups.items():
        cls_idx = recs[0]["label"]
        class_to_groups[cls_idx].append((g_key, recs))

    train_records = []
    val_records = []
    test_records = []

    for cls_idx, g_list in class_to_groups.items():
        # Shuffle groups deterministically
        random.shuffle(g_list)
        total_cls_imgs = sum(len(recs) for _, recs in g_list)
        target_train = int(total_cls_imgs * 0.70)
        target_val = int(total_cls_imgs * 0.15)

        cur_train = 0
        cur_val = 0

        for g_key, recs in g_list:
            if cur_train < target_train:
                train_records.extend(recs)
                cur_train += len(recs)
            elif cur_val < target_val:
                val_records.extend(recs)
                cur_val += len(recs)
            else:
                test_records.extend(recs)

    print(f"\nSplit complete:")
    print(f"  Train images: {len(train_records)} ({len(train_records)/total_images*100:.1f}%)")
    print(f"  Val images:   {len(val_records)} ({len(val_records)/total_images*100:.1f}%)")
    print(f"  Test images:  {len(test_records)} ({len(test_records)/total_images*100:.1f}%)")

    # Verify zero leakage across splits
    train_groups = set(r["group_id"] for r in train_records)
    val_groups = set(r["group_id"] for r in val_records)
    test_groups = set(r["group_id"] for r in test_records)

    leakage_train_val = train_groups.intersection(val_groups)
    leakage_train_test = train_groups.intersection(test_groups)
    leakage_val_test = val_groups.intersection(test_groups)

    assert len(leakage_train_val) == 0, f"Leakage detected between train and val: {len(leakage_train_val)}"
    assert len(leakage_train_test) == 0, f"Leakage detected between train and test: {len(leakage_train_test)}"
    assert len(leakage_val_test) == 0, f"Leakage detected between val and test: {len(leakage_val_test)}"
    print("Leakage verification passed: 0 group overlaps across train, validation, and test splits.")

    # 3. Write Manifests
    def write_manifest(filepath, records):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filepath", "filename", "commodity", "source_stage", "target_class", "label", "group_id"])
            for r in records:
                writer.writerow([r["filepath"], r["filename"], r["commodity"], r["source_stage"], r["target_class"], r["label"], r["group_id"]])

    write_manifest(OUTPUT_DIR / "train_manifest.csv", train_records)
    write_manifest(OUTPUT_DIR / "val_manifest.csv", val_records)
    write_manifest(OUTPUT_DIR / "test_manifest.csv", test_records)
    print(f"Saved manifests to: {OUTPUT_DIR}")

    # 4. Write label_map.json
    label_map_data = {
        "classes": VOCAB,
        "label_to_index": LABEL_MAP,
        "index_to_label": INV_LABEL_MAP,
        "display_names": {
            "fresh": "Fresh",
            "slightly_spoiled": "Slightly Spoiled",
            "rotten": "Rotten"
        },
        "source_mapping_rationale": (
            "AgriFreshNET 'Fresh' maps to 'Fresh' (peak post-harvest quality). "
            "AgriFreshNET 'Semi-Fresh' maps to 'Slightly Spoiled' (early softening, surface spotting, or initial oxidation). "
            "AgriFreshNET 'Rotten' maps to 'Rotten' (microbial decay, structural decomposition, extensive mold)."
        )
    }
    with open(OUTPUT_DIR / "label_map.json", "w", encoding="utf-8") as f:
        json.dump(label_map_data, f, indent=2)

    # 5. Class balance statistics
    def get_class_counts(records):
        counts = {cls: 0 for cls in VOCAB}
        for r in records:
            counts[r["target_class"]] += 1
        return counts

    train_counts = get_class_counts(train_records)
    val_counts = get_class_counts(val_records)
    test_counts = get_class_counts(test_records)

    config_data = {
        "dataset_name": "AgriFreshNET Freshness V2",
        "total_images": total_images,
        "total_capture_groups": len(groups),
        "split_counts": {
            "train": len(train_records),
            "val": len(val_records),
            "test": len(test_records)
        },
        "class_counts": {
            "train": train_counts,
            "val": val_counts,
            "test": test_counts
        },
        "target_classes": VOCAB,
        "image_size": 224,
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        },
        "leakage_safe": True
    }

    with open(OUTPUT_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    print("\nDataset generation complete!")
    print(f"Class distributions:")
    print(f"  Train: {train_counts}")
    print(f"  Val:   {val_counts}")
    print(f"  Test:  {test_counts}")


if __name__ == "__main__":
    main()
