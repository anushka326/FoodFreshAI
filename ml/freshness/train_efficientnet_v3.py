#!/usr/bin/env python
"""
FoodFresh AI - Freshness Model V3 Training
Trains EfficientNet-B0 on AgriFreshNET dataset with proper evaluation.
Candidate to be compared against existing ResNet-18 model.
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
from torchvision.models import efficientnet_b0
import torchvision.transforms as T
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score,
    precision_score, recall_score, balanced_accuracy_score, accuracy_score
)
from PIL import Image, ImageOps

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "agrifreshnet"
TRAIN_MANIFEST = PROCESSED_DIR / "freshness_train_manifest.csv"
VAL_MANIFEST = PROCESSED_DIR / "freshness_val_manifest.csv"
TEST_MANIFEST = PROCESSED_DIR / "freshness_test_manifest.csv"
LABEL_MAP_PATH = PROCESSED_DIR / "freshness_label_map.json"

CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
MODEL_SAVE_PATH = CANDIDATES_DIR / "freshness_v3_efficientnet_b0.pth"
REPORTS_DIR = PROJECT_ROOT / "reports"

CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load label map
with open(LABEL_MAP_PATH) as f:
    label_data = json.load(f)
    CLASS_NAMES = [label_data["id_to_freshness"][str(i)] for i in range(label_data["num_classes"])]
    NUM_CLASSES = label_data["num_classes"]

print(f"Classes: {CLASS_NAMES}")
print(f"Num classes: {NUM_CLASSES}")

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 32
NUM_WORKERS = 0 if os.name == 'nt' else 4
EPOCHS = 20
EARLY_STOPPING_PATIENCE = 5
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
RANDOM_SEED = 42

# Set random seed for reproducibility
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Preprocessing transforms
TRAIN_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.RandomCrop(224),
    T.RandomHorizontalFlip(p=0.5),
    T.RandomRotation(degrees=15),
    T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    T.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

EVAL_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class AgriFreshDataset(Dataset):
    """Load images and labels from manifest CSV."""
    
    def __init__(self, manifest_path: Path, transform=None):
        self.samples = []
        self.transform = transform
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_path = Path(row['image_path'])
                label = int(row['freshness_id'])
                self.samples.append((image_path, label))
        
        print(f"Loaded {len(self.samples)} samples from {manifest_path.name}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        image_path, label = self.samples[idx]
        
        try:
            image = Image.open(image_path)
            # Ensure RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            # Fix EXIF orientation
            image = ImageOps.exif_transpose(image)
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            # Return black image + label on error
            return torch.zeros(3, 224, 224), label


def create_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    """Create EfficientNet-B0 model."""
    model = efficientnet_b0(weights='DEFAULT' if pretrained else None)
    
    # Replace classifier
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
    
    return model


def evaluate_model(model, loader, device, criterion):
    """Evaluate model on a dataset."""
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(loader):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(loader.dataset)
    accuracy = accuracy_score(all_labels, all_preds)
    balanced_acc = balanced_accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    weighted_f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    precisions = precision_score(all_labels, all_preds, average=None, zero_division=0)
    recalls = recall_score(all_labels, all_preds, average=None, zero_division=0)
    f1s = f1_score(all_labels, all_preds, average=None, zero_division=0)
    
    cm = confusion_matrix(all_labels, all_preds, labels=range(NUM_CLASSES))
    
    return {
        'loss': avg_loss,
        'accuracy': accuracy,
        'balanced_accuracy': balanced_acc,
        'macro_f1': macro_f1,
        'weighted_f1': weighted_f1,
        'precisions': precisions,
        'recalls': recalls,
        'f1s': f1s,
        'confusion_matrix': cm,
        'predictions': all_preds,
        'labels': all_labels
    }


def main():
    print("=" * 80)
    print("FOODFRESH AI - FRESHNESS MODEL V3 TRAINING (EfficientNet-B0)")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Classes: {CLASS_NAMES}")
    print()
    
    # Create datasets
    print("Loading datasets...")
    train_dataset = AgriFreshDataset(TRAIN_MANIFEST, transform=TRAIN_TRANSFORM)
    val_dataset = AgriFreshDataset(VAL_MANIFEST, transform=EVAL_TRANSFORM)
    test_dataset = AgriFreshDataset(TEST_MANIFEST, transform=EVAL_TRANSFORM)
    
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=True
    )
    
    # Create model
    print("\nCreating model...")
    model = create_model(NUM_CLASSES, pretrained=True)
    model.to(DEVICE)
    
    # Loss and optimizer
    class_weights = torch.tensor([1.0, 1.0, 1.0], device=DEVICE)  # Balanced
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    # Training loop
    print("\nStarting training...")
    history = []
    best_val_f1 = 0.0
    patience_counter = 0
    
    for epoch in range(EPOCHS):
        # Train
        model.train()
        train_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
            
            if (batch_idx + 1) % 50 == 0:
                print(f"  Epoch {epoch+1}/{EPOCHS}, Batch {batch_idx+1}/{len(train_loader)}, Loss: {loss.item():.4f}")
        
        train_loss /= len(train_dataset)
        scheduler.step()
        
        # Validate
        print(f"\n  Evaluating on validation set...")
        val_metrics = evaluate_model(model, val_loader, DEVICE, criterion)
        val_f1 = val_metrics['macro_f1']
        
        print(f"Epoch {epoch+1:2d}/{EPOCHS}: Train Loss: {train_loss:.4f} | Val Loss: {val_metrics['loss']:.4f} | Val F1: {val_f1:.4f} | Val Acc: {val_metrics['accuracy']:.4f}")
        
        history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'val_loss': val_metrics['loss'],
            'val_accuracy': val_metrics['accuracy'],
            'val_balanced_accuracy': val_metrics['balanced_accuracy'],
            'val_macro_f1': val_f1,
            'val_weighted_f1': val_metrics['weighted_f1']
        })
        
        # Early stopping
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  ✅ Saved model (best F1: {best_val_f1:.4f})")
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
    
    print("\nTrain Set Metrics:")
    train_metrics = evaluate_model(model, train_loader, DEVICE, criterion)
    print(f"  Loss: {train_metrics['loss']:.4f}")
    print(f"  Accuracy: {train_metrics['accuracy']:.4f}")
    print(f"  Balanced Accuracy: {train_metrics['balanced_accuracy']:.4f}")
    print(f"  Macro F1: {train_metrics['macro_f1']:.4f}")
    print(f"  Weighted F1: {train_metrics['weighted_f1']:.4f}")
    
    print("\nValidation Set Metrics:")
    print(f"  Loss: {val_metrics['loss']:.4f}")
    print(f"  Accuracy: {val_metrics['accuracy']:.4f}")
    print(f"  Balanced Accuracy: {val_metrics['balanced_accuracy']:.4f}")
    print(f"  Macro F1: {val_metrics['macro_f1']:.4f}")
    print(f"  Weighted F1: {val_metrics['weighted_f1']:.4f}")
    
    print("\nTest Set Metrics:")
    test_metrics = evaluate_model(model, test_loader, DEVICE, criterion)
    print(f"  Loss: {test_metrics['loss']:.4f}")
    print(f"  Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"  Balanced Accuracy: {test_metrics['balanced_accuracy']:.4f}")
    print(f"  Macro F1: {test_metrics['macro_f1']:.4f}")
    print(f"  Weighted F1: {test_metrics['weighted_f1']:.4f}")
    
    print("\nPer-Class Metrics (Test Set):")
    print(f"{'Class':<15} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print("-" * 55)
    for i, class_name in enumerate(CLASS_NAMES):
        support = np.sum(np.array(test_metrics['labels']) == i)
        print(f"{class_name:<15} {test_metrics['precisions'][i]:>10.4f} {test_metrics['recalls'][i]:>10.4f} {test_metrics['f1s'][i]:>10.4f} {support:>10d}")
    
    print("\nConfusion Matrix (Test Set):")
    print("Rows: True labels, Columns: Predicted labels")
    print(f"{'':10s} {CLASS_NAMES[0]:>12s} {CLASS_NAMES[1]:>12s} {CLASS_NAMES[2]:>12s}")
    for i, class_name in enumerate(CLASS_NAMES):
        print(f"{class_name:<10s} {test_metrics['confusion_matrix'][i, 0]:>12d} {test_metrics['confusion_matrix'][i, 1]:>12d} {test_metrics['confusion_matrix'][i, 2]:>12d}")
    
    # Save training history
    history_csv = REPORTS_DIR / "freshness_v3_training_history.csv"
    with open(history_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
    print(f"\nTraining history saved to {history_csv}")
    
    # Save detailed report
    report_path = REPORTS_DIR / "freshness_v3_training_report.md"
    with open(report_path, 'w') as f:
        f.write("# Freshness Model V3 Training Report\n\n")
        f.write(f"**Model:** EfficientNet-B0\n")
        f.write(f"**Dataset:** AgriFreshNET (Fresh, Semi-Fresh, Rotten)\n")
        f.write(f"**Train/Val/Test Split:** {len(train_dataset)}/{len(val_dataset)}/{len(test_dataset)}\n")
        f.write(f"**Training Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Device:** {DEVICE}\n")
        f.write(f"**Classes:** {', '.join(CLASS_NAMES)}\n\n")
        
        f.write("## Final Metrics\n\n")
        f.write("### Test Set (Held-out)\n")
        f.write(f"- **Accuracy:** {test_metrics['accuracy']:.4f}\n")
        f.write(f"- **Balanced Accuracy:** {test_metrics['balanced_accuracy']:.4f}\n")
        f.write(f"- **Macro F1:** {test_metrics['macro_f1']:.4f}\n")
        f.write(f"- **Weighted F1:** {test_metrics['weighted_f1']:.4f}\n")
        f.write(f"- **Loss:** {test_metrics['loss']:.4f}\n\n")
        
        f.write("### Per-Class Metrics (Test Set)\n")
        f.write(f"| Class | Precision | Recall | F1 | Support |\n")
        f.write(f"|-------|-----------|--------|----|---------|\n")
        for i, class_name in enumerate(CLASS_NAMES):
            support = np.sum(np.array(test_metrics['labels']) == i)
            f.write(f"| {class_name} | {test_metrics['precisions'][i]:.4f} | {test_metrics['recalls'][i]:.4f} | {test_metrics['f1s'][i]:.4f} | {support} |\n")
        
        f.write("\n### Confusion Matrix (Test Set)\n")
        f.write(f"Rows: True labels, Columns: Predicted labels\n\n")
        f.write(f"| Actual \\ Predicted | {CLASS_NAMES[0]} | {CLASS_NAMES[1]} | {CLASS_NAMES[2]} |\n")
        f.write(f"|-------------------|{'---'*13}|\n")
        for i, class_name in enumerate(CLASS_NAMES):
            f.write(f"| {class_name} | {test_metrics['confusion_matrix'][i, 0]} | {test_metrics['confusion_matrix'][i, 1]} | {test_metrics['confusion_matrix'][i, 2]} |\n")
        
        f.write("\n## Dataset Information\n")
        f.write("- **Foods in Dataset:** Banana, Bittermelon, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato\n")
        f.write("- **Classes:** Fresh (33.3%), Semi-Fresh (33.3%), Rotten (33.3%)\n")
        f.write("- **Note:** Training data does NOT include green chilli or dried chilli\n")
        f.write("  - Green chilli failures on this model would be due to unseen domain\n")
        f.write("  - Dried chilli is a different form and needs form-aware handling\n\n")
        
        f.write("## Comparison with Production Model (to be performed)\n")
        f.write("- Current production: nathansekar/food-freshness-detector fallback\n")
        f.write("- This candidate: EfficientNet-B0 on AgriFreshNET\n")
        f.write("- Decision: Evaluate on protected regression cases before promotion\n")
    
    print(f"Report saved to {report_path}")
    
    print("\n" + "=" * 80)
    print("Training complete!")
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
