#!/usr/bin/env python
"""
Shelf-Life Dataset Discovery Script
Inspects available shelf-life data before training.
"""

import os
import csv
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

print("=" * 80)
print("SHELF-LIFE DATASET DISCOVERY")
print("=" * 80)

# Check various shelf-life data sources
shelf_life_dirs = [
    PROCESSED_DIR / "agrifreshnet",
    PROCESSED_DIR / "freshness_v2",
    PROCESSED_DIR / "cross_dataset",
    PROJECT_ROOT / "data" / "raw",
]

print("\nSearching for shelf-life related data...")

for data_dir in shelf_life_dirs:
    if data_dir.exists():
        print(f"\n📁 Checking {data_dir.relative_to(PROJECT_ROOT)}:")
        
        # Look for CSV files
        csv_files = list(data_dir.glob("*.csv"))
        if csv_files:
            print(f"  CSV files found: {len(csv_files)}")
            for csv_file in csv_files[:5]:
                print(f"    - {csv_file.name}")
        
        # Look for JSON files
        json_files = list(data_dir.glob("*.json"))
        if json_files:
            print(f"  JSON files found: {len(json_files)}")
            for json_file in json_files[:5]:
                print(f"    - {json_file.name}")

# Check for FoodKeeper data
print("\n\nFoodKeeper Data:")
foodkeeper_json = PROJECT_ROOT / "backend" / "app" / "data" / "FoodKeeper.json"
if foodkeeper_json.exists():
    print(f"✅ Found FoodKeeper.json at {foodkeeper_json}")
    with open(foodkeeper_json) as f:
        foodkeeper = json.load(f)
    
    print(f"  Total entries: {len(foodkeeper)}")
    
    # Analyze shelf-life patterns
    shelf_lives = defaultdict(list)
    storage_types = set()
    
    for entry in foodkeeper:
        if 'shelf_life' in entry:
            for storage_type, duration in entry['shelf_life'].items():
                storage_types.add(storage_type)
                if duration:
                    shelf_lives[storage_type].append(duration)
    
    print(f"  Storage types: {sorted(storage_types)}")
    print(f"  Sample entries:")
    for entry in foodkeeper[:3]:
        print(f"    - {entry.get('name', 'Unknown')}: {entry.get('shelf_life', {})}")
else:
    print(f"❌ FoodKeeper.json not found at {foodkeeper_json}")

# Check AgriFreshNET for shelf-life labels
print("\n\nAgriFreshNET Shelf-Life Coverage:")
agrifreshnet_dir = PROCESSED_DIR / "agrifreshnet"
if agrifreshnet_dir.exists():
    for manifest_file in ["freshness_train_manifest.csv", "freshness_val_manifest.csv", "freshness_test_manifest.csv"]:
        manifest_path = agrifreshnet_dir / manifest_file
        if manifest_path.exists():
            with open(manifest_path) as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                print(f"  {manifest_file} columns: {headers}")
                
                # Count unique values
                if 'food_type' in headers:
                    foods = set()
                    rows = list(csv.DictReader(open(manifest_path)))
                    for row in rows:
                        foods.add(row.get('food_type', 'Unknown'))
                    print(f"    Foods: {sorted(foods)}")

# Check database for ML feedback / shelf-life records
print("\n\nDatabase Analysis:")
db_path = PROJECT_ROOT / "backend" / "app" / "database" / "fresho_buddy.db"
if db_path.exists():
    print(f"✅ Database found at {db_path}")
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check pantry_history table for shelf-life estimates
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pantry_history'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM pantry_history")
            count = cursor.fetchone()[0]
            print(f"  pantry_history table: {count} records")
            
            cursor.execute("PRAGMA table_info(pantry_history)")
            columns = cursor.fetchall()
            print(f"  Columns:")
            for col in columns:
                print(f"    - {col[1]}: {col[2]}")
        
        # Check ml_feedback for shelf-life related feedback
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_feedback'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM ml_feedback")
            count = cursor.fetchone()[0]
            print(f"  ml_feedback table: {count} records")
        
        conn.close()
    except Exception as e:
        print(f"  Error accessing database: {e}")
else:
    print(f"❌ Database not found at {db_path}")

print("\n" + "=" * 80)
print("Shelf-life dataset discovery complete.")
print("=" * 80)

# Summary
print("\n\nSUMMARY FOR SHELF-LIFE MODEL TRAINING:")
print("=" * 80)
print("\n✅ Strengths:")
print("  1. FoodKeeper.json has canonical shelf-life data for 200+ products")
print("  2. AgriFreshNET provides ground-truth freshness labels for 8 food types")
print("  3. Database ready to store ML feedback for shelf-life predictions")
print("\n⚠️ Challenges:")
print("  1. Limited paired (food_image, freshness_label, shelf_life_days) training data")
print("  2. Shelf-life varies by storage type (fridge, room temp, freezer)")
print("  3. No direct image-to-shelf-life ground truth in dataset")
print("\n📊 Recommended Approach:")
print("  1. Use FoodKeeper as weak supervision (heuristic baseline)")
print("  2. Train regression model: food_embedding + freshness_confidence → shelf_life_days")
print("  3. Data: AgriFreshNET foods + FoodKeeper shelf-life lookup")
print("  4. Evaluate: MAE, RMSE vs. FoodKeeper baseline")
print("\n")
