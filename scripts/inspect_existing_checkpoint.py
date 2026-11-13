import shutil
from pathlib import Path
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ckpt_path = PROJECT_ROOT / "models" / "trained" / "food_classifier.pth"
backup_path = PROJECT_ROOT / "models" / "trained" / "food_classifier_backup.pth"

print("=" * 60, flush=True)
print("EXISTING CHECKPOINT INSPECTION & SAFETY BACKUP", flush=True)
print("=" * 60, flush=True)

if ckpt_path.exists():
    size_mb = ckpt_path.stat().st_size / (1024 * 1024)
    print(f"Checkpoint found at: {ckpt_path} ({size_mb:.2f} MB)", flush=True)
    
    # Load and inspect
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    print(f"Checkpoint type: {type(ckpt)}", flush=True)
    if isinstance(ckpt, dict):
        print(f"Keys: {list(ckpt.keys())}", flush=True)
        print(f"Model Name: {ckpt.get('model_name')}", flush=True)
        print(f"Num Classes: {ckpt.get('num_classes')}", flush=True)
        print(f"Best Val Accuracy: {ckpt.get('best_val_accuracy')}", flush=True)
        print(f"Epoch: {ckpt.get('epoch')}", flush=True)
        print(f"Stage: {ckpt.get('stage')}", flush=True)
        print(f"Training Config: {ckpt.get('training_config')}", flush=True)
    
    # Backup
    if not backup_path.exists():
        shutil.copy2(ckpt_path, backup_path)
        print(f"Created safety backup at: {backup_path}", flush=True)
    else:
        print(f"Safety backup already exists at: {backup_path} ({backup_path.stat().st_size / (1024*1024):.2f} MB)", flush=True)
else:
    print(f"No existing checkpoint found at {ckpt_path}", flush=True)
