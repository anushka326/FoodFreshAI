"""
FoodFresh AI - Fruits-360 Dataset Verification and Train/Validation Split (STEP 7)
Verifies manifest paths, label mappings, class balance, and creates
a reproducible stratified validation split strictly from the training manifest.
"""

from pathlib import Path
import sys
import json
import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def verify_and_prepare_splits():
    print("=" * 60)
    print("FOODFRESH AI — FRUITS-360 DATASET VERIFICATION")
    print("=" * 60)

    processed_dir = PROJECT_ROOT / "data" / "processed" / "fruits360"
    train_manifest_path = processed_dir / "fruits360_train_manifest.csv"
    test_manifest_path = processed_dir / "fruits360_test_manifest.csv"
    label_map_path = processed_dir / "label_map.json"

    # 1. Load label map
    print("\n[1] Loading label map...")
    with open(label_map_path, "r", encoding="utf-8") as f:
        label_map = json.load(f)
    
    num_classes = label_map.get("num_classes", len(label_map.get("food_to_id", {})))
    food_to_id = label_map.get("food_to_id", {})
    id_to_food = label_map.get("id_to_food", {})
    print(f"    Number of classes: {num_classes}")
    print(f"    Classes: {list(food_to_id.keys())}")

    # 2. Load manifests
    print("\n[2] Loading train and test manifests...")
    df_train = pd.read_csv(train_manifest_path)
    df_test = pd.read_csv(test_manifest_path)
    print(f"    Training manifest images: {len(df_train):,}")
    print(f"    Test manifest images:     {len(df_test):,}")

    # 3. Verify class distribution
    print("\n[3] Training class distribution:")
    train_dist = df_train["normalized_food"].value_counts().to_dict()
    for food, cnt in train_dist.items():
        print(f"    {food:<12}: {cnt:>6} images ({cnt / len(df_train) * 100:.2f}%)")

    print("\n    Test class distribution:")
    test_dist = df_test["normalized_food"].value_counts().to_dict()
    for food, cnt in test_dist.items():
        print(f"    {food:<12}: {cnt:>6} images ({cnt / len(df_test) * 100:.2f}%)")

    # 4. Verify path existence
    print("\n[4] Verifying filesystem image paths...")
    missing_train = [p for p in df_train["image_path"] if not Path(p).exists()]
    missing_test = [p for p in df_test["image_path"] if not Path(p).exists()]

    if missing_train:
        raise FileNotFoundError(f"Missing {len(missing_train)} training images!")
    if missing_test:
        raise FileNotFoundError(f"Missing {len(missing_test)} test images!")
    print(f"    All {len(df_train):,} training image paths verified: PASS")
    print(f"    All {len(df_test):,} test image paths verified: PASS")

    # 5. Verify label IDs
    print("\n[5] Verifying label consistency...")
    invalid_train_labels = df_train[~df_train["label_id"].isin(range(num_classes))]
    invalid_test_labels = df_test[~df_test["label_id"].isin(range(num_classes))]
    if len(invalid_train_labels) > 0 or len(invalid_test_labels) > 0:
        raise ValueError("Invalid label IDs detected outside [0, num_classes-1] range!")
    print(f"    All label IDs in train and test within [0, {num_classes - 1}]: PASS")

    # 6. Verify duplicate paths between train and test
    print("\n[6] Checking for data leakage (duplicate paths between train & test)...")
    train_set = set(df_train["image_path"])
    test_set = set(df_test["image_path"])
    leakage = train_set.intersection(test_set)
    if leakage:
        raise ValueError(f"CRITICAL: Found {len(leakage)} duplicate image paths between train and test!")
    print(f"    Duplicate image paths between train and test: {len(leakage)} (ZERO LEAKAGE PASS)")

    # 7. Create reproducible Stratified Train/Val Split from training manifest
    print("\n[7] Generating reproducible stratified Train/Validation split (90% train, 10% val)...")
    train_split_df, val_split_df = train_test_split(
        df_train,
        test_size=0.10,
        stratify=df_train["label_id"],
        random_state=42
    )

    train_split_path = processed_dir / "fruits360_train_split.csv"
    val_split_path = processed_dir / "fruits360_val_split.csv"

    train_split_df.to_csv(train_split_path, index=False)
    val_split_df.to_csv(val_split_path, index=False)

    print(f"    Train split saved:      {train_split_path} ({len(train_split_df):,} images)")
    print(f"    Validation split saved: {val_split_path} ({len(val_split_df):,} images)")
    print(f"    Test set untouched:     {test_manifest_path} ({len(df_test):,} images)")

    print("\n" + "=" * 60)
    print("DATASET VERIFICATION SUMMARY:")
    print(f"  Food classes:      {num_classes}")
    print(f"  Training images:   {len(train_split_df):,}")
    print(f"  Validation images: {len(val_split_df):,}")
    print(f"  Test images:       {len(df_test):,}")
    print(f"  Path Integrity:    100% PASS")
    print(f"  Data Leakage:      0% PASS")
    print("=" * 60)

    return {
        "num_classes": num_classes,
        "train_count": len(train_split_df),
        "val_count": len(val_split_df),
        "test_count": len(df_test),
        "train_split_path": str(train_split_path),
        "val_split_path": str(val_split_path),
        "test_path": str(test_manifest_path)
    }


if __name__ == "__main__":
    verify_and_prepare_splits()
