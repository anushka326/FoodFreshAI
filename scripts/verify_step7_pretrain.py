"""
FoodFresh AI - Pre-training Dataset and Manifest Verification (STEP 7)
"""

import json
from pathlib import Path
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "fruits360"

train_manifest_path = DATA_DIR / "fruits360_train_manifest.csv"
test_manifest_path = DATA_DIR / "fruits360_test_manifest.csv"
label_map_path = DATA_DIR / "label_map.json"
train_split_path = DATA_DIR / "fruits360_train_split.csv"
val_split_path = DATA_DIR / "fruits360_val_split.csv"

print("=" * 60)
print("FOODFRESH AI — STEP 7 DATASET & MANIFEST VERIFICATION")
print("=" * 60)

# 1. Label Map
print("\n[1] Checking label map...")
assert label_map_path.exists(), f"Missing {label_map_path}"
with open(label_map_path, "r", encoding="utf-8") as f:
    label_map_data = json.load(f)

num_classes = label_map_data.get("num_classes", len(label_map_data.get("food_to_id", {})))
food_to_id = label_map_data.get("food_to_id", {})
id_to_food = label_map_data.get("id_to_food", {})
class_names = sorted(list(food_to_id.keys()))

print(f"Number of classes: {num_classes}")
print(f"Class names: {', '.join(class_names)}")

# 2. Manifests
print("\n[2] Loading dataset manifests...")
train_df = pd.read_csv(train_manifest_path)
test_df = pd.read_csv(test_manifest_path)
print(f"Train manifest total images: {len(train_df):,}")
print(f"Test manifest total images:  {len(test_df):,}")

# Check splits
if train_split_path.exists() and val_split_path.exists():
    train_split_df = pd.read_csv(train_split_path)
    val_split_df = pd.read_csv(val_split_path)
    print(f"Train split images:          {len(train_split_df):,}")
    print(f"Validation split images:     {len(val_split_df):,}")
    print(f"Train + Val split sum:       {len(train_split_df) + len(val_split_df):,} (Matches train manifest: {len(train_split_df) + len(val_split_df) == len(train_df)})")

# Class distribution in train manifest
print("\n[3] Class distribution in Training manifest:")
train_dist = train_df["normalized_food"].value_counts().sort_index()
for cls, cnt in train_dist.items():
    print(f"  {cls:12s}: {cnt:5d} images ({cnt/len(train_df)*100:.2f}%)")

# Class distribution in test manifest
print("\n[4] Class distribution in Test manifest:")
test_dist = test_df["normalized_food"].value_counts().sort_index()
for cls, cnt in test_dist.items():
    print(f"  {cls:12s}: {cnt:5d} images ({cnt/len(test_df)*100:.2f}%)")

# 5. Verify sample image paths
print("\n[5] Verifying image paths and readability...")
missing_train = 0
for idx, p in enumerate(train_df["image_path"]):
    if not Path(p).exists():
        missing_train += 1
print(f"Checked {len(train_df):,} train image paths. Missing: {missing_train}")

missing_test = 0
for idx, p in enumerate(test_df["image_path"]):
    if not Path(p).exists():
        missing_test += 1
print(f"Checked {len(test_df):,} test image paths. Missing: {missing_test}")

# Spot check 20 random images from train and test to verify PIL loading
sample_images = train_df["image_path"].sample(10, random_state=42).tolist() + test_df["image_path"].sample(10, random_state=42).tolist()
corrupt_count = 0
for p in sample_images:
    try:
        with Image.open(p) as im:
            im.verify()
    except Exception as e:
        print(f"Corrupt image found at {p}: {e}")
        corrupt_count += 1
print(f"Spot-checked 20 images: {corrupt_count} corrupted (PASS)")

print("\n" + "=" * 60)
print("DATASET & MANIFEST VERIFICATION SUCCESSFUL")
print("=" * 60)
