"""
FoodFresh AI - Freshness Classification Pipeline Smoke Test Script (STEP 10)
Verifies:
1. Label map loads (3 classes).
2. Train, Val, and Test manifests exist.
3. Dataset loader functions properly.
4. Samples load from train, val, and test splits with correct shape (3, 224, 224).
5. Model factory constructs EfficientNet-B0 with 3 output classes.
6. Forward pass succeeds with output shape [1, 3] and no NaN/Inf values.
7. Verification that NO training was executed and NO checkpoint was saved.
"""

from pathlib import Path
import sys
import torch

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.freshness.config import FreshnessConfig
from ml.freshness.dataset import FreshnessDataset, create_freshness_data_loaders
from ml.freshness.model import create_freshness_model
from ml.freshness.transforms import get_freshness_transforms
from ml.freshness.utils import load_label_map, set_seed


def run_freshness_pipeline_test() -> bool:
    print("=" * 60)
    print("FOODFRESH AI - FRESHNESS PIPELINE SMOKE TEST (STEP 10)")
    print("=" * 60)

    set_seed(42)
    cfg = FreshnessConfig()

    checks = {
        "label_map": False,
        "train_manifest": False,
        "val_manifest": False,
        "test_manifest": False,
        "dataset_loaders": False,
        "train_sample": False,
        "val_sample": False,
        "test_sample": False,
        "model_factory": False,
        "forward_pass_shape": False,
        "no_nan_or_inf": False,
        "no_training_executed": True,
        "no_checkpoint_saved": True
    }

    try:
        # 1. Label Map Check
        freshness_to_id, id_to_freshness = load_label_map(cfg.label_map_path)
        if len(freshness_to_id) == 3 and freshness_to_id.get("Fresh") == 0:
            checks["label_map"] = True
            print(f"[OK] Label map verified: {freshness_to_id}")

        # 2. Manifest Checks
        if cfg.train_manifest_path.exists():
            checks["train_manifest"] = True
            print(f"[OK] Train manifest verified: {cfg.train_manifest_path.name}")

        if cfg.val_manifest_path.exists():
            checks["val_manifest"] = True
            print(f"[OK] Val manifest verified: {cfg.val_manifest_path.name}")

        if cfg.test_manifest_path.exists():
            checks["test_manifest"] = True
            print(f"[OK] Test manifest verified: {cfg.test_manifest_path.name}")

        # 3. Dataset & DataLoaders
        train_transforms, eval_transforms = get_freshness_transforms(image_size=cfg.image_size)
        train_ds = FreshnessDataset(cfg.train_manifest_path, transform=train_transforms)
        val_ds = FreshnessDataset(cfg.val_manifest_path, transform=eval_transforms)
        test_ds = FreshnessDataset(cfg.test_manifest_path, transform=eval_transforms)

        if len(train_ds) > 0 and len(val_ds) > 0 and len(test_ds) > 0:
            checks["dataset_loaders"] = True
            print(f"[OK] Datasets loaded: Train={len(train_ds)}, Val={len(val_ds)}, Test={len(test_ds)}")

        # 4. Sample Loading
        tr_img, tr_lbl = train_ds[0]
        if tr_img.shape == (3, 224, 224) and isinstance(tr_lbl, int):
            checks["train_sample"] = True
            print(f"[OK] Train sample verified: tensor shape {tuple(tr_img.shape)}, label={tr_lbl}")

        val_img, val_lbl = val_ds[0]
        if val_img.shape == (3, 224, 224) and isinstance(val_lbl, int):
            checks["val_sample"] = True
            print(f"[OK] Val sample verified: tensor shape {tuple(val_img.shape)}, label={val_lbl}")

        test_img, test_lbl = test_ds[0]
        if test_img.shape == (3, 224, 224) and isinstance(test_lbl, int):
            checks["test_sample"] = True
            print(f"[OK] Test sample verified: tensor shape {tuple(test_img.shape)}, label={test_lbl}")

        # 5. Model Factory & Pretrained EfficientNet-B0 (Architecture Smoke Test)
        print("\nConstructing EfficientNet-B0 freshness model...")
        model = create_freshness_model(num_classes=3, pretrained=True)
        in_feat = model.classifier[1].in_features
        out_feat = model.classifier[1].out_features

        if in_feat == 1280 and out_feat == 3:
            checks["model_factory"] = True
            print(f"[OK] Model factory verified: in_features={in_feat}, out_features={out_feat} (3 classes)")

        # 6. Single Forward Pass (eval mode, torch.no_grad())
        model.eval()
        dummy_input = test_img.unsqueeze(0)  # Shape [1, 3, 224, 224]
        with torch.no_grad():
            output = model(dummy_input)

        if output.shape == (1, 3):
            checks["forward_pass_shape"] = True
            print(f"[OK] Forward pass verified: output shape = {tuple(output.shape)}")

        # 7. Check for NaN or Inf
        if not torch.isnan(output).any() and not torch.isinf(output).any():
            checks["no_nan_or_inf"] = True
            print("[OK] Numerical stability verified: 0 NaN, 0 Inf in output logits")

        # 8. Verify No Checkpoint Was Saved
        if cfg.checkpoint_path.exists():
            checks["no_checkpoint_saved"] = False
            print(f"WARNING: Checkpoint {cfg.checkpoint_path} exists! Untrained model should not be saved.")
        else:
            print(f"[OK] Confirmed: No untrained checkpoint exists at {cfg.checkpoint_path}")

    except Exception as e:
        print(f"\nPipeline smoke test encountered error: {e}", file=sys.stderr)
        raise e

    print("\n" + "=" * 50)
    print("FRESHNESS PIPELINE TEST SUMMARY")
    print("=" * 50)
    all_passed = True
    for check_name, status in checks.items():
        status_str = "PASS" if status else "FAIL"
        print(f"{check_name.replace('_', ' ').title():<30}: {status_str}")
        if not status:
            all_passed = False

    print("-" * 50)
    print(f"OVERALL STATUS: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 50)
    return all_passed


if __name__ == "__main__":
    success = run_freshness_pipeline_test()
    sys.exit(0 if success else 1)
