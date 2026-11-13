"""
FoodFresh AI - Post-Training Checkpoint Verification Script (STEP 7)
Verifies:
1. checkpoint exists
2. checkpoint can be loaded
3. model architecture can be reconstructed
4. class mapping can be loaded
5. one test image can be loaded
6. preprocessing works
7. inference works
8. output shape is [1, num_classes]
9. predicted class is one of the valid FoodFresh classes
10. probabilities sum approximately to 1
DOES NOT RETRAIN THE MODEL.
"""

from pathlib import Path
import sys
import pandas as pd
from PIL import Image
import torch
import torch.nn.functional as F

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms


def test_trained_checkpoint():
    print("=" * 60)
    print("FOODFRESH AI — TRAINED CHECKPOINT VERIFICATION")
    print("=" * 60)

    cfg = FoodRecognitionConfig()
    device = torch.device(cfg.device)
    checkpoint_path = cfg.checkpoint_path

    # 1. Checkpoint exists
    print("\n[1] Verifying checkpoint existence...")
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")
    file_size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
    print(f"    Checkpoint path: {checkpoint_path}")
    print(f"    Checkpoint size: {file_size_mb:.2f} MB (PASS)")

    # 2. Checkpoint can be loaded
    print("\n[2] Loading checkpoint dictionary...")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    print(f"    Keys present: {list(checkpoint.keys())} (PASS)")

    # 3. Class mapping can be loaded
    print("\n[3] Loading class mapping from checkpoint...")
    num_classes = checkpoint.get("num_classes", cfg.num_classes)
    food_to_id = checkpoint.get("food_to_id", checkpoint.get("class_to_idx", {}))
    id_to_food = checkpoint.get("id_to_food", checkpoint.get("idx_to_class", {}))
    print(f"    Number of classes: {num_classes}")
    print(f"    Class mappings count: {len(food_to_id)} (PASS)")
    if num_classes != 12 or len(food_to_id) != 12:
        raise ValueError(f"Expected 12 classes, got num_classes={num_classes}")

    # 4. Model architecture can be reconstructed
    print("\n[4] Reconstructing model architecture...")
    model = create_food_recognition_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    print(f"    Model architecture reconstructed and weights loaded successfully (PASS)")

    # 5. One test image can be loaded
    print("\n[5] Sampling one real image from test manifest...")
    test_manifest_path = cfg.test_manifest_path
    if not test_manifest_path.exists():
        raise FileNotFoundError(f"Test manifest missing at {test_manifest_path}")
    
    test_df = pd.read_csv(test_manifest_path)
    sample_row = test_df.iloc[0]
    sample_image_path = Path(sample_row["image_path"])
    true_label_name = sample_row["normalized_food"]
    true_label_id = int(sample_row["label_id"])

    print(f"    Test image path: {sample_image_path}")
    print(f"    True food class: {true_label_name} (ID: {true_label_id})")
    if not sample_image_path.exists():
        raise FileNotFoundError(f"Sample test image file does not exist: {sample_image_path}")

    pil_img = Image.open(sample_image_path).convert("RGB")
    print(f"    Original image size: {pil_img.size} (PASS)")

    # 6. Preprocessing works
    print("\n[6] Applying evaluation preprocessing transforms...")
    _, eval_transforms = get_transforms(image_size=cfg.image_size)
    img_tensor = eval_transforms(pil_img).unsqueeze(0).to(device)
    print(f"    Transformed tensor shape: {list(img_tensor.shape)} (PASS)")

    # 7. Inference works
    print("\n[7] Running inference forward pass...")
    with torch.no_grad():
        logits = model(img_tensor)

    # 8. Output shape is [1, num_classes]
    output_shape = list(logits.shape)
    expected_shape = [1, num_classes]
    print(f"    Output shape: {output_shape}")
    if output_shape != expected_shape:
        raise ValueError(f"Expected output shape {expected_shape}, got {output_shape}")
    print(f"    Output shape matches expected: PASS")

    # 9. Predicted class is one of the valid FoodFresh classes
    probs = F.softmax(logits, dim=1)[0]
    pred_idx = torch.argmax(probs).item()
    pred_food = id_to_food.get(str(pred_idx), f"Class {pred_idx}")
    pred_conf = probs[pred_idx].item()

    print(f"    Predicted food: {pred_food} (ID: {pred_idx})")
    print(f"    Confidence:     {pred_conf * 100:.2f}%")
    valid_classes = set(food_to_id.keys())
    if pred_food not in valid_classes:
        raise ValueError(f"Predicted class '{pred_food}' not in valid classes: {valid_classes}")
    print(f"    Predicted class is valid FoodFresh food: PASS")

    # 10. Probabilities sum approximately to 1
    prob_sum = probs.sum().item()
    print(f"    Sum of softmax probabilities: {prob_sum:.6f}")
    if abs(prob_sum - 1.0) > 1e-4:
        raise ValueError(f"Softmax probabilities do not sum to 1.0 (sum={prob_sum})")
    print(f"    Softmax normalization: PASS")

    print("\n" + "=" * 60)
    print("CHECKPOINT VERIFICATION SUMMARY: ALL 10 TESTS PASSED")
    print(f"Checkpoint:      {checkpoint_path}")
    print(f"Best Val Acc:    {checkpoint.get('best_val_accuracy', 0.0):.2f}%")
    print(f"Best Epoch:      {checkpoint.get('epoch', 'N/A')}")
    print(f"Test prediction: {pred_food} ({pred_conf * 100:.2f}%)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_trained_checkpoint()
