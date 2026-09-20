"""
FoodFresh AI - EfficientNet-B0 Initialization & Forward-Pass Verification (STEP 6)
Loads official TorchVision EfficientNet-B0 with ImageNet pretrained weights,
adapts the classification head to the FoodFresh AI dataset class count,
inspects device availability (CUDA/CPU), verifies weight cache,
and executes exactly one forward pass with a dummy tensor.
DOES NOT TRAIN THE MODEL.
"""

from pathlib import Path
import sys
import json
import os

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from ml.food_recognition.utils import load_label_map, count_parameters
from ml.food_recognition.model import create_food_recognition_model, get_official_transforms


def test_efficientnet_initialization():
    print("=" * 60)
    print("FOODFRESH AI — EFFICIENTNET-B0 INITIALIZATION & TEST")
    print("=" * 60)

    # 1. Load label_map.json and determine actual number of classes
    label_map_path = PROJECT_ROOT / "data" / "processed" / "fruits360" / "label_map.json"
    print(f"\n[1] Reading food class configuration from: {label_map_path}")
    if not label_map_path.exists():
        raise FileNotFoundError(f"Label map not found at {label_map_path}")

    food_to_id, id_to_food, num_classes = load_label_map(label_map_path)
    print(f"    Loaded classes count: {num_classes}")
    print(f"    Classes: {list(food_to_id.keys())}")

    # 2. Inspect TorchVision Cache before download
    torch_hub_dir = Path(torch.hub.get_dir())
    checkpoints_dir = torch_hub_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    weights_enum = EfficientNet_B0_Weights.DEFAULT
    weights_url = getattr(weights_enum, "url", None)
    expected_filename = Path(weights_url).name if weights_url else "efficientnet_b0*.pth"
    expected_cache_path = checkpoints_dir / expected_filename if weights_url else None
    
    already_cached = expected_cache_path.exists() if expected_cache_path else False
    print(f"\n[2] TorchVision cache check:")
    print(f"    Torch hub directory: {torch_hub_dir}")
    print(f"    Checkpoints directory: {checkpoints_dir}")
    print(f"    Weight URL: {weights_url}")
    print(f"    Cached before run: {'YES' if already_cached else 'NO'}")

    # 3. Device detection
    cuda_available = torch.cuda.is_available()
    device = torch.device("cuda" if cuda_available else "cpu")
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "N/A"
    print(f"\n[3] Device configuration:")
    print(f"    CUDA Available: {'YES' if cuda_available else 'NO'}")
    print(f"    Active Device: {device}")
    print(f"    GPU Name: {gpu_name}")

    # 4. Load base model with official pretrained weights to inspect original classifier
    print(f"\n[4] Initializing base EfficientNet-B0 with official weights:")
    print(f"    Weight Enum: {weights_enum}")
    base_model = efficientnet_b0(weights=weights_enum)
    orig_classifier = str(base_model.classifier)
    orig_in_features = base_model.classifier[1].in_features
    orig_out_features = base_model.classifier[1].out_features
    print(f"    Original classifier architecture:")
    print(f"      {orig_classifier}")
    print(f"    Original in_features: {orig_in_features}, out_features: {orig_out_features}")

    # Verify cache status after download/load
    cached_after = expected_cache_path.exists() if expected_cache_path else True
    cache_file_size_mb = (expected_cache_path.stat().st_size / (1024 * 1024)) if (expected_cache_path and expected_cache_path.exists()) else None
    print(f"    Cached after run: {'YES' if cached_after else 'UNKNOWN'}")
    if expected_cache_path and expected_cache_path.exists():
        print(f"    Cache file path: {expected_cache_path}")
        print(f"    Cache file size: {cache_file_size_mb:.2f} MB")

    # 5. Create FoodFresh AI model with adapted classifier
    print(f"\n[5] Adapting classifier head for {num_classes} FoodFresh AI classes:")
    model = create_food_recognition_model(num_classes=num_classes, pretrained=True)
    new_classifier = str(model.classifier)
    new_in_features = model.classifier[1].in_features
    new_out_features = model.classifier[1].out_features
    print(f"    Adapted classifier architecture:")
    print(f"      {new_classifier}")
    print(f"    New in_features: {new_in_features}, out_features: {new_out_features}")

    # 6. Parameter counts
    total_params, trainable_params = count_parameters(model)
    print(f"\n[6] Model parameter analysis:")
    print(f"    Total parameters: {total_params:,}")
    print(f"    Trainable parameters: {trainable_params:,}")

    # 7. Preprocessing transforms
    official_transforms = get_official_transforms()
    print(f"\n[7] Official TorchVision transforms:")
    print(f"    {official_transforms}")

    # 8. Single forward pass with dummy tensor
    print(f"\n[8] Executing single forward-pass test (NO TRAINING):")
    model.to(device)
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    print(f"    Dummy input tensor shape: {list(dummy_input.shape)} on {device}")

    with torch.no_grad():
        output = model(dummy_input)

    output_shape = list(output.shape)
    print(f"    Forward pass output tensor shape: {output_shape}")
    expected_shape = [1, num_classes]

    if output_shape == expected_shape:
        forward_pass_result = "PASS"
        print(f"    Forward pass result: PASS (matches expected {expected_shape})")
    else:
        forward_pass_result = "FAIL"
        print(f"    Forward pass result: FAIL (expected {expected_shape}, got {output_shape})")

    # 9. Verify Safety Guarantees
    trained_checkpoint_path = PROJECT_ROOT / "models" / "trained" / "food_classifier.pth"
    checkpoint_exists = trained_checkpoint_path.exists()
    print(f"\n[9] Safety and Integrity Verifications:")
    print(f"    Training executed: NO")
    print(f"    FoodFresh trained checkpoint created: {'YES (UNEXPECTED!)' if checkpoint_exists else 'NO (CORRECT)'}")
    print(f"    Official TorchVision weights used: YES")
    print(f"    Third-party weights used: NO")

    results = {
        "model_name": "EfficientNet-B0",
        "weight_source": "Official TorchVision",
        "weight_enum": str(weights_enum),
        "pretrained_loaded": True,
        "already_cached": already_cached,
        "cache_location": str(expected_cache_path) if expected_cache_path else str(checkpoints_dir),
        "cache_file_size_mb": cache_file_size_mb,
        "num_classes": num_classes,
        "classes": list(food_to_id.keys()),
        "original_classifier": orig_classifier,
        "new_classifier": new_classifier,
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "device": str(device),
        "gpu_name": gpu_name,
        "cuda_available": cuda_available,
        "dummy_input_shape": list(dummy_input.shape),
        "output_shape": output_shape,
        "forward_pass": forward_pass_result,
        "training_executed": False,
        "trained_checkpoint_created": checkpoint_exists
    }

    print("\n" + "=" * 60)
    print("STEP 6 VERIFICATION SUMMARY:")
    print(f"  EfficientNet-B0 loaded: YES")
    print(f"  Pretrained weights loaded: YES")
    print(f"  Weight Enum: {weights_enum}")
    print(f"  Num classes: {num_classes}")
    print(f"  Total params: {total_params:,}")
    print(f"  Device: {device} ({gpu_name})")
    print(f"  Forward pass: {forward_pass_result}")
    print(f"  Output shape: {output_shape}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    test_efficientnet_initialization()
