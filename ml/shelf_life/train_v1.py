#!/usr/bin/env python
"""
FoodFresh AI - Shelf-Life Model V1 Training
Trains a regression model to predict shelf-life from food type + freshness + storage type.
Uses FoodKeeper.json as ground-truth labels via lookup.
"""

import os
import sys
import csv
import json
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "agrifreshnet"
TRAIN_MANIFEST = PROCESSED_DIR / "freshness_train_manifest.csv"
VAL_MANIFEST = PROCESSED_DIR / "freshness_val_manifest.csv"
TEST_MANIFEST = PROCESSED_DIR / "freshness_test_manifest.csv"
LABEL_MAP_PATH = PROCESSED_DIR / "freshness_label_map.json"

FOODKEEPER_PATH = PROJECT_ROOT / "data" / "raw" / "foodkeeper" / "FoodKeeper.json"
CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
REPORTS_DIR = PROJECT_ROOT / "reports"

CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_SAVE_PATH = CANDIDATES_DIR / "shelf_life_v1_regression.pth"
ENCODER_SAVE_PATH = CANDIDATES_DIR / "shelf_life_v1_encoders.pkl"

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 32
NUM_WORKERS = 0 if os.name == 'nt' else 4
EPOCHS = 30
EARLY_STOPPING_PATIENCE = 7
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
RANDOM_SEED = 42

# Storage types (one-hot encoding)
STORAGE_TYPES = ['Room Temperature', 'Refrigerator', 'Freezer']

# Set random seed
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Load label map
with open(LABEL_MAP_PATH) as f:
    label_data = json.load(f)
    FRESHNESS_CLASSES = [label_data["id_to_freshness"][str(i)] for i in range(label_data["num_classes"])]

print(f"Freshness classes: {FRESHNESS_CLASSES}")

# Load FoodKeeper data for ground-truth shelf-life lookup
print(f"Loading FoodKeeper data from {FOODKEEPER_PATH}...")
with open(FOODKEEPER_PATH, encoding='utf-8') as f:
    foodkeeper_entries = json.load(f)

# Build mapping: food_name -> shelf_life_days for each storage type
foodkeeper_map = {}
for entry in foodkeeper_entries:
    name = entry.get('name', '').lower()
    shelf_life = entry.get('shelf_life', {})
    foodkeeper_map[name] = {
        'Room Temperature': shelf_life.get('Room Temperature', shelf_life.get('Room Temp', None)),
        'Refrigerator': shelf_life.get('Refrigerator', shelf_life.get('Fridge', None)),
        'Freezer': shelf_life.get('Freezer', None),
    }

print(f"Loaded {len(foodkeeper_map)} food entries from FoodKeeper")

def get_shelf_life(food_name: str, freshness: str, storage_type: str):
    """Get shelf-life from FoodKeeper based on food, freshness, and storage type."""
    food_key = food_name.lower()
    if food_key not in foodkeeper_map:
        return None
    
    shelf_life_dict = foodkeeper_map[food_key]
    base_days = shelf_life_dict.get(storage_type)
    
    if base_days is None:
        return None
    
    # Heuristic: Adjust shelf-life based on freshness
    # Fresh: +0% (baseline)
    # Semi-Fresh: -30% (already aging)
    # Rotten: -70% (almost expired)
    if freshness == 'Fresh':
        return base_days
    elif freshness == 'Semi-Fresh':
        return max(1, int(base_days * 0.7))
    elif freshness == 'Rotten':
        return max(1, int(base_days * 0.3))
    else:
        return base_days


class ShelfLifeDataset(Dataset):
    """Dataset for shelf-life prediction."""
    
    def __init__(self, manifest_path: Path, storage_type: str = 'Refrigerator'):
        self.samples = []
        self.storage_type = storage_type
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                food_type = row['food_type']
                freshness = row['freshness_label']
                
                shelf_life = get_shelf_life(food_type, freshness, storage_type)
                if shelf_life is not None:
                    self.samples.append({
                        'food_type': food_type,
                        'freshness': freshness,
                        'shelf_life': shelf_life,
                        'storage_type': storage_type
                    })
        
        print(f"Loaded {len(self.samples)} samples from {manifest_path.name} (storage: {storage_type})")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx]


class ShelfLifeRegressor(nn.Module):
    """Neural network for shelf-life prediction."""
    
    def __init__(self, num_foods: int, num_freshness: int):
        super().__init__()
        
        # Embeddings
        self.food_embedding = nn.Embedding(num_foods, 16)
        self.freshness_embedding = nn.Embedding(num_freshness, 8)
        
        # Input features: food_emb(16) + freshness_emb(8) + storage_type_one_hot(3) = 27
        self.fc1 = nn.Linear(16 + 8 + len(STORAGE_TYPES), 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(0.3)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(32, 16)
        
        # Output: single regression value (shelf-life in days)
        self.fc_out = nn.Linear(16, 1)
        
        # Activation
        self.relu = nn.ReLU()
    
    def forward(self, food_ids, freshness_ids, storage_type_one_hot):
        # Embeddings
        food_emb = self.food_embedding(food_ids)
        freshness_emb = self.freshness_embedding(freshness_ids)
        
        # Concatenate all features
        x = torch.cat([food_emb, freshness_emb, storage_type_one_hot], dim=1)
        
        # Dense layers
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        x = self.relu(x)
        
        # Output (with ReLU to ensure positive shelf-life)
        x = self.fc_out(x)
        x = torch.nn.functional.relu(x)
        
        return x


def prepare_batch(batch, food_encoder, freshness_encoder, device):
    """Prepare batch of samples for training."""
    
    # Encode categorical features
    foods = torch.tensor([food_encoder.transform([item['food_type']])[0] for item in batch], device=device)
    freshness = torch.tensor([freshness_encoder.transform([item['freshness']])[0] for item in batch], device=device)
    
    # One-hot encode storage type
    storage_type = torch.zeros((len(batch), len(STORAGE_TYPES)), device=device)
    for i, item in enumerate(batch):
        storage_idx = STORAGE_TYPES.index(item['storage_type'])
        storage_type[i, storage_idx] = 1
    
    # Target: shelf-life in days
    targets = torch.tensor([item['shelf_life'] for item in batch], device=device, dtype=torch.float32)
    
    return foods, freshness, storage_type, targets


def main():
    print("=" * 80)
    print("FOODFRESH AI - SHELF-LIFE MODEL V1 TRAINING")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Storage types: {STORAGE_TYPES}")
    print()
    
    # Create datasets for each storage type
    print("Loading datasets...")
    train_datasets = {st: ShelfLifeDataset(TRAIN_MANIFEST, st) for st in STORAGE_TYPES}
    val_datasets = {st: ShelfLifeDataset(VAL_MANIFEST, st) for st in STORAGE_TYPES}
    test_datasets = {st: ShelfLifeDataset(TEST_MANIFEST, st) for st in STORAGE_TYPES}
    
    # Combine all samples for encoders
    all_samples = []
    for datasets in [train_datasets, val_datasets, test_datasets]:
        for st_samples in datasets.values():
            all_samples.extend(st_samples.samples)
    
    # Create encoders
    food_encoder = LabelEncoder()
    freshness_encoder = LabelEncoder()
    
    foods = [s['food_type'] for s in all_samples]
    freshnesses = [s['freshness'] for s in all_samples]
    
    food_encoder.fit(list(set(foods)))
    freshness_encoder.fit(list(set(freshnesses)))
    
    print(f"\nFood classes: {list(food_encoder.classes_)}")
    print(f"Freshness classes: {list(freshness_encoder.classes_)}")
    
    # Create model
    print("\nCreating model...")
    model = ShelfLifeRegressor(len(food_encoder.classes_), len(freshness_encoder.classes_))
    model.to(DEVICE)
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    # For now, train on Refrigerator storage type (most common)
    train_dataset = train_datasets['Refrigerator']
    val_dataset = val_datasets['Refrigerator']
    test_dataset = test_datasets['Refrigerator']
    
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, collate_fn=lambda batch: batch
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, collate_fn=lambda batch: batch
    )
    test_loader = DataLoader(
        test_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, collate_fn=lambda batch: batch
    )
    
    # Training loop
    print("\nStarting training...")
    history = []
    best_val_mae = float('inf')
    patience_counter = 0
    
    for epoch in range(EPOCHS):
        # Train
        model.train()
        train_loss = 0.0
        train_preds = []
        train_targets = []
        
        for batch_idx, batch in enumerate(train_loader):
            foods, freshness, storage_type, targets = prepare_batch(batch, food_encoder, freshness_encoder, DEVICE)
            
            optimizer.zero_grad()
            outputs = model(foods, freshness, storage_type).squeeze()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * len(batch)
            train_preds.extend(outputs.detach().cpu().numpy())
            train_targets.extend(targets.cpu().numpy())
            
            if (batch_idx + 1) % 20 == 0:
                print(f"  Epoch {epoch+1}/{EPOCHS}, Batch {batch_idx+1}/{len(train_loader)}, Loss: {loss.item():.4f}")
        
        train_loss /= len(train_dataset)
        train_mae = mean_absolute_error(train_targets, train_preds)
        scheduler.step()
        
        # Validate
        print(f"\n  Evaluating on validation set...")
        model.eval()
        val_loss = 0.0
        val_preds = []
        val_targets = []
        
        with torch.no_grad():
            for batch in val_loader:
                foods, freshness, storage_type, targets = prepare_batch(batch, food_encoder, freshness_encoder, DEVICE)
                outputs = model(foods, freshness, storage_type).squeeze()
                loss = criterion(outputs, targets)
                
                val_loss += loss.item() * len(batch)
                val_preds.extend(outputs.cpu().numpy())
                val_targets.extend(targets.cpu().numpy())
        
        val_loss /= len(val_dataset)
        val_mae = mean_absolute_error(val_targets, val_preds)
        
        print(f"Epoch {epoch+1:2d}/{EPOCHS}: Train Loss: {train_loss:.4f} (MAE: {train_mae:.2f}) | Val Loss: {val_loss:.4f} (MAE: {val_mae:.2f})")
        
        history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_mae': train_mae,
            'val_loss': val_loss,
            'val_mae': val_mae,
        })
        
        # Early stopping
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  ✅ Saved model (best MAE: {best_val_mae:.2f})")
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print(f"Early stopping triggered after {EARLY_STOPPING_PATIENCE} epochs without improvement")
                break
    
    # Load best model
    print(f"\n\nLoading best model from {MODEL_SAVE_PATH}...")
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    
    # Final evaluation
    print("\nFinal Evaluation:")
    print("=" * 80)
    
    model.eval()
    with torch.no_grad():
        # Test set
        test_preds = []
        test_targets = []
        
        for batch in test_loader:
            foods, freshness, storage_type, targets = prepare_batch(batch, food_encoder, freshness_encoder, DEVICE)
            outputs = model(foods, freshness, storage_type).squeeze()
            test_preds.extend(outputs.cpu().numpy())
            test_targets.extend(targets.cpu().numpy())
    
    test_mae = mean_absolute_error(test_targets, test_preds)
    test_mse = mean_squared_error(test_targets, test_preds)
    test_rmse = np.sqrt(test_mse)
    test_r2 = r2_score(test_targets, test_preds)
    
    print(f"\nTest Set Metrics:")
    print(f"  MAE:  {test_mae:.2f} days")
    print(f"  RMSE: {test_rmse:.2f} days")
    print(f"  R2:   {test_r2:.4f}")
    
    # Save encoders
    with open(ENCODER_SAVE_PATH, 'wb') as f:
        pickle.dump({
            'food_encoder': food_encoder,
            'freshness_encoder': freshness_encoder,
        }, f)
    print(f"\nEncoders saved to {ENCODER_SAVE_PATH}")
    
    # Save history
    history_csv = REPORTS_DIR / "shelf_life_v1_training_history.csv"
    with open(history_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
    print(f"Training history saved to {history_csv}")
    
    # Save report
    report_path = REPORTS_DIR / "shelf_life_v1_training_report.md"
    with open(report_path, 'w') as f:
        f.write("# Shelf-Life Model V1 Training Report\n\n")
        f.write(f"**Model:** Neural Network Regression\n")
        f.write(f"**Dataset:** AgriFreshNET + FoodKeeper Lookup\n")
        f.write(f"**Train/Val/Test Split:** {len(train_dataset)}/{len(val_dataset)}/{len(test_dataset)}\n")
        f.write(f"**Training Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Device:** {DEVICE}\n")
        f.write(f"**Storage Type:** Refrigerator (primary training scenario)\n\n")
        
        f.write("## Model Architecture\n")
        f.write("- Food Type Embedding: 16-dim\n")
        f.write("- Freshness Embedding: 8-dim\n")
        f.write("- Storage Type: One-hot (3-dim)\n")
        f.write("- FC1: 27 → 64 (BatchNorm + ReLU + Dropout)\n")
        f.write("- FC2: 64 → 32 (BatchNorm + ReLU + Dropout)\n")
        f.write("- FC3: 32 → 16 (ReLU)\n")
        f.write("- Output: 16 → 1 (Shelf-life in days, ReLU)\n\n")
        
        f.write("## Final Metrics (Test Set)\n")
        f.write(f"- **MAE:** {test_mae:.2f} days\n")
        f.write(f"- **RMSE:** {test_rmse:.2f} days\n")
        f.write(f"- **R2:** {test_r2:.4f}\n\n")
        
        f.write("## Comparison with FoodKeeper Baseline\n")
        f.write("- FoodKeeper baseline: Uses canonical shelf-life lookup + heuristic adjustments for freshness\n")
        f.write("- ML model: Learns patterns from food + freshness + storage type\n")
        f.write("- Expected benefit: Handles edge cases and provides confidence calibration\n\n")
        
        f.write("## Limitations\n")
        f.write("- Weak supervision: Labels derived from FoodKeeper heuristics, not ground-truth observations\n")
        f.write("- Limited food diversity: Only 8 food types from AgriFreshNET\n")
        f.write("- Simplified freshness adjustment: Linear decay (Fresh → Semi-Fresh → Rotten)\n\n")
        
        f.write("## Next Steps\n")
        f.write("1. Evaluate ML vs. FoodKeeper on validation set\n")
        f.write("2. Collect real-world feedback to improve training signal\n")
        f.write("3. Consider multi-task learning: freshness + shelf-life\n")
        f.write("4. Expand to more food types and storage conditions\n")
    
    print(f"Report saved to {report_path}")
    
    print("\n" + "=" * 80)
    print("Shelf-Life Model V1 training complete!")
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print(f"Encoders saved to: {ENCODER_SAVE_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
