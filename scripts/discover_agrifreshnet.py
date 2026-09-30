#!/usr/bin/env python
"""
Dataset Discovery Script
Inspects AgriFreshNET manifests to understand the exact data composition before training.
"""

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "agrifreshnet"

# Load manifests
train_df = pd.read_csv(PROCESSED_DIR / "freshness_train_manifest.csv")
val_df = pd.read_csv(PROCESSED_DIR / "freshness_val_manifest.csv")
test_df = pd.read_csv(PROCESSED_DIR / "freshness_test_manifest.csv")

print("=" * 80)
print("AGRIFRESHNET DATASET DISCOVERY")
print("=" * 80)

# Basic stats
print(f"\nDataset Splits:")
print(f"  Train: {len(train_df):,} images")
print(f"  Val:   {len(val_df):,} images")
print(f"  Test:  {len(test_df):,} images")
print(f"  Total: {len(train_df) + len(val_df) + len(test_df):,} images")

# Analyze all data
all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)

print(f"\n\nFood Types in Dataset:")
foods = all_df['food_type'].unique()
print(f"  Count: {len(foods)}")
print(f"  Foods: {sorted(foods)}")

print(f"\n\nFreshness Labels in Dataset:")
labels = all_df['freshness_label'].unique()
print(f"  Count: {len(labels)}")
print(f"  Labels: {sorted(labels)}")

print(f"\n\nClass Distribution (Overall):")
class_dist = all_df['freshness_label'].value_counts().sort_index()
for label, count in class_dist.items():
    pct = 100.0 * count / len(all_df)
    print(f"  {label:20s}: {count:6,} ({pct:5.1f}%)")

print(f"\n\nClass Distribution by Split:")
for split_name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
    print(f"\n{split_name}:")
    dist = df['freshness_label'].value_counts().sort_index()
    for label, count in dist.items():
        pct = 100.0 * count / len(df)
        print(f"  {label:20s}: {count:6,} ({pct:5.1f}%)")

print(f"\n\nFood-Freshness Combinations (Train Set):")
combinations = train_df.groupby(['food_type', 'freshness_label']).size().sort_values(ascending=False)
for (food, freshness), count in combinations.items():
    print(f"  {food:20s} + {freshness:15s}: {count:6,}")

print(f"\n\nFreshness by Food Type (All Data):")
pivot = all_df.groupby(['food_type', 'freshness_label']).size().unstack(fill_value=0)
print(pivot)

print(f"\n\nDataset URL Encoding Check:")
# Sample image paths
sample_paths = all_df['image_path'].head(3).tolist()
for path in sample_paths:
    print(f"  {path}")

print(f"\n\nBase Stem Unique Count (for leakage checking):")
print(f"  Train unique base stems: {train_df['base_stem'].nunique()}")
print(f"  Val unique base stems:   {val_df['base_stem'].nunique()}")
print(f"  Test unique base stems:  {test_df['base_stem'].nunique()}")

# Check for stem leakage
train_stems = set(train_df['base_stem'])
val_stems = set(val_df['base_stem'])
test_stems = set(test_df['base_stem'])

leak_train_val = train_stems.intersection(val_stems)
leak_train_test = train_stems.intersection(test_stems)
leak_val_test = val_stems.intersection(test_stems)

print(f"\n\nLeakage Check:")
print(f"  Train-Val overlap:   {len(leak_train_val)}")
print(f"  Train-Test overlap:  {len(leak_train_test)}")
print(f"  Val-Test overlap:    {len(leak_val_test)}")
if len(leak_train_val) == 0 and len(leak_train_test) == 0 and len(leak_val_test) == 0:
    print("  ✅ NO LEAKAGE DETECTED - Dataset splits are clean!")
else:
    print("  ⚠️ LEAKAGE DETECTED - Investigate!")

print(f"\n\nLabel Map:")
label_map_path = PROCESSED_DIR / "freshness_label_map.json"
if label_map_path.exists():
    import json
    with open(label_map_path) as f:
        label_map = json.load(f)
    print(f"  {label_map}")

print("\n" + "=" * 80)
print("Dataset discovery complete. Ready for training.")
print("=" * 80)
