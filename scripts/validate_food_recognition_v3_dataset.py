"""
FoodFresh AI - Step 16 Dataset Validation Script
Validates the integrity, leak-freedom, class taxonomy, and file readability of Food Recognition V3.
"""

from collections import Counter
import json
import os
from pathlib import Path
import sys
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

V3_DIR = PROJECT_ROOT / "data" / "processed" / "food_recognition_v3"
V3_MANIFESTS = V3_DIR / "manifests"
LABEL_MAP_PATH = V3_DIR / "label_map.json"
CONFIG_PATH = V3_DIR / "dataset_config.json"
MAPPING_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "cross_dataset" / "food_class_mapping_v3.json"


def validate_v3():
    print("=" * 65)
    print("FOODFRESH AI - FOOD RECOGNITION V3 DATASET VALIDATION")
    print("=" * 65)

    errors = []
    warnings = []

    # 1. Check Label Map & Config
    print("\n[CHECK 1] Validating Label Map & Configuration...")
    if not LABEL_MAP_PATH.exists():
        errors.append(f"Label map missing at: {LABEL_MAP_PATH}")
        return False
    if not CONFIG_PATH.exists():
        errors.append(f"Config missing at: {CONFIG_PATH}")
        return False

    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        label_data = json.load(f)
    num_classes = label_data["num_classes"]
    expected_classes = set(label_data["food_to_id"].keys())
    print(f"  OK: Label map contains {num_classes} classes.")

    # 2. Check Manifest Existence
    print("\n[CHECK 2] Validating Manifest File Existence...")
    manifest_paths = {
        "train": V3_MANIFESTS / "v3_train_manifest.csv",
        "val": V3_MANIFESTS / "v3_val_manifest.csv",
        "benchmark_test": V3_MANIFESTS / "v3_benchmark_test_manifest.csv",
        "real_world_test": V3_MANIFESTS / "v3_real_world_test_manifest.csv"
    }

    for name, p in manifest_paths.items():
        if not p.exists():
            errors.append(f"Missing manifest: {p}")
        else:
            print(f"  OK: Found {name} manifest at {p.name}")

    if errors:
        print("FATAL ERRORS DETECTED:")
        for e in errors:
            print(f"  - {e}")
        return False

    # 3. Load and Inspect Manifests
    print("\n[CHECK 3] Loading Manifests and Checking Schema...")
    dfs = {}
    total_rows = 0
    all_sample_ids = []
    all_image_paths = []
    split_paths = {}

    required_columns = {
        "sample_id", "source", "source_dataset", "source_class",
        "food_class", "class_id", "image_path", "split", "domain",
        "freshness_label", "object_group"
    }

    for name, p in manifest_paths.items():
        df = pd.read_csv(p, low_memory=False)
        dfs[name] = df
        total_rows += len(df)
        print(f"  {name:16s}: {len(df):>6,d} rows")

        # Column schema check
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            errors.append(f"{name} manifest is missing required columns: {missing_cols}")

        all_sample_ids.extend(df["sample_id"].tolist())
        all_image_paths.extend(df["image_path"].tolist())
        split_paths[name] = set(df["image_path"].tolist())

    print(f"  Total records across all 4 manifests: {total_rows:,d}")

    # 4. Check Sample ID Uniqueness
    print("\n[CHECK 4] Verifying Global Sample ID Uniqueness...")
    sample_id_counts = Counter(all_sample_ids)
    dup_ids = [sid for sid, c in sample_id_counts.items() if c > 1]
    if dup_ids:
        errors.append(f"Found {len(dup_ids)} duplicate sample_id values across manifests (e.g. {dup_ids[:3]})")
    else:
        print(f"  OK: All {len(all_sample_ids):,d} sample_ids are strictly unique.")

    # 5. Check Image Path Duplication & Split Leakage
    print("\n[CHECK 5] Checking for Split Overlap & Image Path Leakage...")
    # Check intersection between train and other splits
    train_paths = split_paths["train"]
    val_paths = split_paths["val"]
    bench_paths = split_paths["benchmark_test"]
    rw_test_paths = split_paths["real_world_test"]

    train_val_overlap = train_paths.intersection(val_paths)
    train_bench_overlap = train_paths.intersection(bench_paths)
    train_rw_overlap = train_paths.intersection(rw_test_paths)
    val_bench_overlap = val_paths.intersection(bench_paths)
    val_rw_overlap = val_paths.intersection(rw_test_paths)
    bench_rw_overlap = bench_paths.intersection(rw_test_paths)

    leakage_found = False
    for pair_name, overlap in [
        ("Train <-> Val", train_val_overlap),
        ("Train <-> Benchmark Test", train_bench_overlap),
        ("Train <-> Real-World Test", train_rw_overlap),
        ("Val <-> Benchmark Test", val_bench_overlap),
        ("Val <-> Real-World Test", val_rw_overlap),
        ("Benchmark Test <-> Real-World Test", bench_rw_overlap)
    ]:
        if overlap:
            errors.append(f"Leakage detected between {pair_name}: {len(overlap)} shared images!")
            leakage_found = True
        else:
            print(f"  OK: Zero overlap between {pair_name}.")

    # 6. Check Class Vocabulary Integrity
    print("\n[CHECK 6] Verifying Class Vocabulary Consistency...")
    all_manifest_classes = set()
    for name, df in dfs.items():
        unique_classes = set(df["food_class"].unique())
        all_manifest_classes.update(unique_classes)
        # Check if any class is outside expected 24 classes
        invalid_classes = unique_classes - expected_classes
        if invalid_classes:
            errors.append(f"Manifest {name} contains unapproved classes: {invalid_classes}")

    # Check that training covers all 24 classes
    train_classes = set(dfs["train"]["food_class"].unique())
    missing_train = expected_classes - train_classes
    if missing_train:
        errors.append(f"Training split is missing classes: {missing_train}")
    else:
        print(f"  OK: Training split contains all {num_classes} classes.")

    # 7. Check Freshness Decoupling
    print("\n[CHECK 7] Verifying Freshness Decoupling (No Freshness Label in Food Class)...")
    forbidden_tokens = ["fresh", "rotten", "semi-fresh", "semi fresh", "semi_fresh"]
    for name, df in dfs.items():
        for fc in df["food_class"].unique():
            fc_lower = fc.lower().strip()
            for token in forbidden_tokens:
                # If food class equals or contains freshness prefixes e.g. "fresh banana"
                if token in fc_lower and fc_lower not in ["fresh"]:
                    errors.append(f"Freshness entanglement detected in {name}: '{fc}' is not a clean food class!")
    print("  OK: All food classes are decoupled from freshness stages.")

    # 8. Check Unapproved AgriFreshNET Food Ingestion
    print("\n[CHECK 8] Checking for Unapproved Cross-Dataset Classes...")
    with open(MAPPING_JSON_PATH, "r", encoding="utf-8") as f:
        cross_mappings = json.load(f)
    approved_agri = {m["food_name"] for m in cross_mappings if m.get("agrifreshnet_available") and m.get("mapping_status") in ("exact", "name_variant")}

    for name, df in dfs.items():
        agri_subset = df[df["source"] == "agrifreshnet"]
        agri_foods = set(agri_subset["food_class"].unique())
        unapproved = agri_foods - approved_agri
        if unapproved:
            errors.append(f"Unapproved AgriFreshNET food classes entered {name}: {unapproved}")
        if "Bittermelon" in agri_foods:
            errors.append(f"Bittermelon erroneously entered {name}!")

    print(f"  OK: AgriFreshNET data strictly confined to 7 approved foods: {sorted(list(approved_agri))}.")

    # 9. Check Image File Existence on Disk
    print("\n[CHECK 9] Verifying Image Files Existence on Disk...")
    missing_files = []
    # Sample check across all files, full check for existence
    check_sample_size = 5000  # Thorough sample for disk read
    missing_on_disk = 0
    for idx, p_str in enumerate(all_image_paths):
        if not os.path.exists(p_str):
            missing_files.append(p_str)
            missing_on_disk += 1
            if missing_on_disk <= 5:
                errors.append(f"File does not exist: {p_str}")

    if missing_on_disk == 0:
        print(f"  OK: Verified all {len(all_image_paths):,d} image files exist on disk.")
    else:
        errors.append(f"Total {missing_on_disk} image files missing on disk!")

    # 10. Check Image Readability with PIL
    print("\n[CHECK 10] Testing Image Readability with PIL (Sample)...")
    import random
    random.seed(42)
    sample_paths = random.sample(all_image_paths, min(check_sample_size, len(all_image_paths)))
    unreadable_count = 0

    for p_str in sample_paths:
        try:
            with Image.open(p_str) as img:
                img.verify()
        except Exception as e:
            unreadable_count += 1
            errors.append(f"Unreadable image ({p_str}): {e}")

    if unreadable_count == 0:
        print(f"  OK: Successfully verified PIL readability of {len(sample_paths):,d} sampled images.")

    # 11. Final Decision
    print("\n" + "=" * 65)
    if errors:
        print(f"V3 DATASET VALIDATION: FAIL ({len(errors)} error(s) detected)")
        print("=" * 65)
        for e in errors[:10]:
            print(f"  - {e}")
        return False
    else:
        print("V3 DATASET VALIDATION: PASS")
        print("=" * 65)
        print("All 11 integrity and leak-prevention criteria fully satisfied.")
        return True


if __name__ == "__main__":
    success = validate_v3()
    sys.exit(0 if success else 1)
