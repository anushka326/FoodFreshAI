"""
FoodFresh AI - Training Smoke Test (STEP 7 Preparation)
Verifies forward pass, loss calculation, backward pass, gradient flow,
and parameter updates on a small batch before starting full training.
"""

from pathlib import Path
import sys
import torch
import torch.nn as nn
from torch.optim import AdamW

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import create_data_loaders
from ml.food_recognition.model import create_food_recognition_model


def run_training_smoke_test():
    print("=" * 60)
    print("FOODFRESH AI — TRAINING SMOKE TEST")
    print("=" * 60)

    cfg = FoodRecognitionConfig()
    cfg.batch_size = 4
    device = torch.device(cfg.device)
    print(f"Device: {device}")

    # 1. Load small batch
    print("[1] Loading small batch from DataLoader...")
    train_loader, val_loader, _ = create_data_loaders(cfg)
    images, labels = next(iter(train_loader))
    images, labels = images.to(device), labels.to(device)
    print(f"    Batch shape: images={list(images.shape)}, labels={list(labels.shape)}")

    # 2. Build model with official pretrained weights
    print("[2] Initializing model...")
    model = create_food_recognition_model(num_classes=cfg.num_classes, pretrained=True).to(device)
    
    # Store initial classifier weights
    initial_weights = model.classifier[1].weight.clone().detach()

    # 3. Setup loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=1e-3)

    # 4. Forward pass
    print("[3] Running forward pass...")
    outputs = model(images)
    loss = criterion(outputs, labels)
    print(f"    Initial loss: {loss.item():.4f}")

    # 5. Backward pass
    print("[4] Running backward pass...")
    optimizer.zero_grad()
    loss.backward()

    # 6. Verify gradients
    grad = model.classifier[1].weight.grad
    if grad is None:
        raise RuntimeError("Gradients are None after backward()!")
    grad_norm = grad.norm().item()
    print(f"    Classifier gradient norm: {grad_norm:.6f} (PASS)")
    if grad_norm == 0.0:
        raise RuntimeError("Classifier gradients are zero!")

    # 7. Optimizer step and parameter update
    print("[5] Running optimizer step...")
    optimizer.step()

    updated_weights = model.classifier[1].weight.clone().detach()
    weight_diff = (updated_weights - initial_weights).abs().max().item()
    print(f"    Max parameter change: {weight_diff:.6f} (PASS)")
    if weight_diff == 0.0:
        raise RuntimeError("Model parameters did not change after optimizer.step()!")

    print("\n" + "=" * 60)
    print("TRAINING SMOKE TEST RESULT: PASS")
    print("Forward pass, backward pass, gradient computation, and weight update verified.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    run_training_smoke_test()
