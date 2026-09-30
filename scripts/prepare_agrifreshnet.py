"""
FoodFresh AI - AgriFreshNET Freshness Dataset Preparation
Prepares reproducible, leak-free manifests and metadata for freshness classification.
"""

import csv
import json
import os
from pathlib import Path
import re
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "agrifreshnet"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Canonical label mapping
FRESHNESS_MAP = {
    "Fresh": 0,
    "Semi-Fresh": 1,
    "Rotten": 2
}

ID_TO_FRESHNESS = {
    0: "Fresh",
    1: "Semi-Fresh",
    2: "Rotten"
}

RANDOM_SEED = 42


def extract_base_stem(image_path: str) -> str:
    """Extract physical photo stem by removing augmentation prefix."""
    filename = Path(image_path).name
    # Strip aug_<digits>_ prefix if present
    base = re.sub(r"^aug_\d+_", "", filename)
    return base


def prepare_agrifreshnet_dataset():
    print("=" * 60)
    print("FOODFRESH AI - STEP 10: AGRIFRESHNET DATASET PREPARATION")
    print("=" * 60)

    # 1. Load image metadata
    metadata_csv = REPORTS_DIR / "agrifreshnet_image_metadata.csv"
    if not metadata_csv.exists():
        raise FileNotFoundError(f"AgriFreshNET metadata not found at: {metadata_csv}")

    df = pd.read_csv(metadata_csv)
    print(f"Loaded {len(df)} records from {metadata_csv.name}")

    # 2. Extract base stem for leak-free grouped splitting
    df["base_stem"] = df["image_path"].apply(extract_base_stem)
    df["food_type"] = df["food"]
    df["freshness_label"] = df["freshness_stage"]
    df["freshness_id"] = df["freshness_label"].map(FRESHNESS_MAP)
    df["original_class"] = df["class_name"]

    # 3. Validate image integrity
    print("\nValidating image files and PIL readability...")
    corrupted_images = []
    for idx, row in df.iterrows():
        p = row["image_path"]
        if not os.path.exists(p):
            corrupted_images.append((p, "File does not exist on disk"))
            continue
        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:
            corrupted_images.append((p, f"Corrupted file: {e}"))

    print(f"Validation complete: {len(df) - len(corrupted_images)} valid, {len(corrupted_images)} corrupted/missing.")
    if corrupted_images:
        print("Excluding corrupted images from manifests...")
        bad_paths = set(p for p, _ in corrupted_images)
        df = df[~df["image_path"].isin(bad_paths)].copy()

    # 4. Perform leak-free grouped stratified train/val/test split
    print(f"\nPerforming grouped stratified split with random seed = {RANDOM_SEED}...")
    # Group by base stem so that all augmentations of the same physical photo remain in the same split
    stem_info = df.groupby("base_stem").agg(
        n_images=("image_path", "count"),
        food=("food_type", "first"),
        freshness=("freshness_label", "first"),
        class_name=("original_class", "first")
    ).reset_index()

    # Shuffle stems reproducibly
    stem_info = stem_info.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)

    # Stratified cumulative thresholding per (food, freshness) stratum
    stem_info["split"] = "train"
    for (food, freshness), g in stem_info.groupby(["food", "freshness"]):
        cum = g["n_images"].cumsum()
        total = g["n_images"].sum()
        val_cut = total * 0.70
        test_cut = total * 0.85
        for idx_val, c in zip(g.index, cum):
            if c <= val_cut:
                stem_info.loc[idx_val, "split"] = "train"
            elif c <= test_cut:
                stem_info.loc[idx_val, "split"] = "val"
            else:
                stem_info.loc[idx_val, "split"] = "test"

    # Merge split assignment back to main dataframe
    df = df.merge(stem_info[["base_stem", "split"]], on="base_stem", how="left")

    # Verify zero stem leakage
    train_stems = set(df[df["split"] == "train"]["base_stem"])
    val_stems = set(df[df["split"] == "val"]["base_stem"])
    test_stems = set(df[df["split"] == "test"]["base_stem"])

    leak_train_val = train_stems.intersection(val_stems)
    leak_train_test = train_stems.intersection(test_stems)
    leak_val_test = val_stems.intersection(test_stems)

    assert len(leak_train_val) == 0, f"Leakage detected between train and val: {len(leak_train_val)} stems"
    assert len(leak_train_test) == 0, f"Leakage detected between train and test: {len(leak_train_test)} stems"
    assert len(leak_val_test) == 0, f"Leakage detected between val and test: {len(leak_val_test)} stems"
    print("Verified: 0 base stem leakage across train, val, and test splits!")

    # 5. Output directories and manifests
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save label map
    label_map_path = PROCESSED_DIR / "freshness_label_map.json"
    label_map_data = {
        "freshness_to_id": FRESHNESS_MAP,
        "id_to_freshness": {str(k): v for k, v in ID_TO_FRESHNESS.items()},
        "num_classes": len(FRESHNESS_MAP)
    }
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump(label_map_data, f, indent=2)
    print(f"Saved: {label_map_path}")

    # Standard manifest columns: image_path,food_type,freshness_label,freshness_id,original_class
    manifest_cols = ["image_path", "food_type", "freshness_label", "freshness_id", "original_class", "base_stem"]

    train_df = df[df["split"] == "train"][manifest_cols]
    val_df = df[df["split"] == "val"][manifest_cols]
    test_df = df[df["split"] == "test"][manifest_cols]

    train_manifest_path = PROCESSED_DIR / "freshness_train_manifest.csv"
    val_manifest_path = PROCESSED_DIR / "freshness_val_manifest.csv"
    test_manifest_path = PROCESSED_DIR / "freshness_test_manifest.csv"

    train_df.to_csv(train_manifest_path, index=False)
    val_df.to_csv(val_manifest_path, index=False)
    test_df.to_csv(test_manifest_path, index=False)

    print(f"Saved: {train_manifest_path} ({len(train_df)} rows, {len(train_df)/len(df)*100:.2f}%)")
    print(f"Saved: {val_manifest_path} ({len(val_df)} rows, {len(val_df)/len(df)*100:.2f}%)")
    print(f"Saved: {test_manifest_path} ({len(test_df)} rows, {len(test_df)/len(df)*100:.2f}%)")

    # 6. Save config JSON
    config_json_path = PROCESSED_DIR / "freshness_config.json"
    config_data = {
        "dataset_name": "AgriFreshNET Freshness",
        "random_seed": RANDOM_SEED,
        "num_classes": len(FRESHNESS_MAP),
        "total_images": len(df),
        "train_count": len(train_df),
        "val_count": len(val_df),
        "test_count": len(test_df),
        "split_proportions": {
            "train": round(len(train_df) / len(df), 4),
            "val": round(len(val_df) / len(df), 4),
            "test": round(len(test_df) / len(df), 4)
        },
        "food_types": sorted(df["food_type"].unique().tolist()),
        "freshness_stages": ["Fresh", "Semi-Fresh", "Rotten"],
        "class_counts_by_split": {
            "train": train_df["freshness_label"].value_counts().to_dict(),
            "val": val_df["freshness_label"].value_counts().to_dict(),
            "test": test_df["freshness_label"].value_counts().to_dict()
        }
    }
    with open(config_json_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    print(f"Saved: {config_json_path}")

    # 7. Generate Dataset Balance Reports
    balance_csv_path = REPORTS_DIR / "freshness_dataset_balance.csv"
    balance_records = []

    # Overall freshness distribution
    for stage in ["Fresh", "Semi-Fresh", "Rotten"]:
        tr_cnt = (train_df["freshness_label"] == stage).sum()
        val_cnt = (val_df["freshness_label"] == stage).sum()
        te_cnt = (test_df["freshness_label"] == stage).sum()
        tot = tr_cnt + val_cnt + te_cnt
        balance_records.append({
            "category_level": "overall_freshness",
            "food_type": "ALL",
            "freshness_label": stage,
            "train_count": tr_cnt,
            "val_count": val_cnt,
            "test_count": te_cnt,
            "total_count": tot,
            "train_pct": round(tr_cnt / tot * 100, 2),
            "val_pct": round(val_cnt / tot * 100, 2),
            "test_pct": round(te_cnt / tot * 100, 2)
        })

    # Breakdown by food_type and freshness
    for food in sorted(df["food_type"].unique()):
        for stage in ["Fresh", "Semi-Fresh", "Rotten"]:
            sub_tr = ((train_df["food_type"] == food) & (train_df["freshness_label"] == stage)).sum()
            sub_val = ((val_df["food_type"] == food) & (val_df["freshness_label"] == stage)).sum()
            sub_te = ((test_df["food_type"] == food) & (test_df["freshness_label"] == stage)).sum()
            sub_tot = sub_tr + sub_val + sub_te
            balance_records.append({
                "category_level": "food_x_freshness",
                "food_type": food,
                "freshness_label": stage,
                "train_count": sub_tr,
                "val_count": sub_val,
                "test_count": sub_te,
                "total_count": sub_tot,
                "train_pct": round(sub_tr / sub_tot * 100, 2) if sub_tot > 0 else 0,
                "val_pct": round(sub_val / sub_tot * 100, 2) if sub_tot > 0 else 0,
                "test_pct": round(sub_te / sub_tot * 100, 2) if sub_tot > 0 else 0
            })

    balance_df = pd.DataFrame(balance_records)
    balance_df.to_csv(balance_csv_path, index=False)
    print(f"Saved: {balance_csv_path}")

    # Generate Markdown preparation report
    prep_report_path = REPORTS_DIR / "freshness_dataset_preparation_report.md"
    with open(prep_report_path, "w", encoding="utf-8") as f:
        f.write("# AgriFreshNET Freshness Dataset Preparation Report\n\n")
        f.write("## Overview\n")
        f.write(f"- **Total images processed:** {len(df):,}\n")
        f.write(f"- **Corrupted/invalid images:** {len(corrupted_images)}\n")
        f.write(f"- **Unique physical image stems:** {df['base_stem'].nunique():,}\n")
        f.write(f"- **Random seed:** {RANDOM_SEED}\n")
        f.write(f"- **Split strategy:** Grouped stratified split by base image stem and (food, freshness) stratum\n\n")

        f.write("## Split Counts\n")
        f.write(f"- **Train:** {len(train_df):,} images ({len(train_df)/len(df)*100:.2f}%)\n")
        f.write(f"- **Validation:** {len(val_df):,} images ({len(val_df)/len(df)*100:.2f}%)\n")
        f.write(f"- **Test:** {len(test_df):,} images ({len(test_df)/len(df)*100:.2f}%)\n\n")

        f.write("## Freshness Stage Distribution\n\n")
        f.write("| Freshness Stage | Class ID | Train | Validation | Test | Total | Train % | Val % | Test % |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for rec in balance_records[:3]:
            f.write(f"| **{rec['freshness_label']}** | {FRESHNESS_MAP[rec['freshness_label']]} | "
                    f"{rec['train_count']:,} | {rec['val_count']:,} | {rec['test_count']:,} | "
                    f"{rec['total_count']:,} | {rec['train_pct']}% | {rec['val_pct']}% | {rec['test_pct']}% |\n")

        f.write("\n## Food Types Represented (8 varieties)\n\n")
        f.write("| Food Type | Fresh (Train/Val/Test) | Semi-Fresh (Train/Val/Test) | Rotten (Train/Val/Test) | Total |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for food in sorted(df["food_type"].unique()):
            f_rec = next(r for r in balance_records if r["food_type"] == food and r["freshness_label"] == "Fresh")
            sf_rec = next(r for r in balance_records if r["food_type"] == food and r["freshness_label"] == "Semi-Fresh")
            r_rec = next(r for r in balance_records if r["food_type"] == food and r["freshness_label"] == "Rotten")
            tot = f_rec['total_count'] + sf_rec['total_count'] + r_rec['total_count']
            f.write(f"| **{food}** | {f_rec['train_count']}/{f_rec['val_count']}/{f_rec['test_count']} | "
                    f"{sf_rec['train_count']}/{sf_rec['val_count']}/{sf_rec['test_count']} | "
                    f"{r_rec['train_count']}/{r_rec['val_count']}/{r_rec['test_count']} | {tot:,} |\n")

        f.write("\n## Leak-Free Guarantee\n")
        f.write("- All augmented variations derived from the same base photograph (`base_stem`) reside in the exact same split.\n")
        f.write("- Base stem intersection between splits is strictly **0**.\n")

    print(f"Saved: {prep_report_path}")
    print("\nDataset preparation completed successfully!")


if __name__ == "__main__":
    prepare_agrifreshnet_dataset()
