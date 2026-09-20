"""
FoodFresh AI - Food Recognition Prediction Interface (STEP 7)
Provides single-image inference and top-K softmax probabilities using
the trained FoodFresh AI EfficientNet-B0 checkpoint (models/trained/food_classifier.pth).
"""

import argparse
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union
from PIL import Image

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn.functional as F
from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms


class FoodPredictor:
    """Inference wrapper for trained Food Recognition models."""

    def __init__(self, checkpoint_path: Optional[Path] = None, device: Optional[str] = None):
        self.config = FoodRecognitionConfig()
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else self.config.checkpoint_path
        self.device = torch.device(device or self.config.device)
        self.model = None
        self.id_to_food = {}
        self.transforms = None

        if self.checkpoint_path.exists():
            self._load_model()
        else:
            print(f"[PREDICTION NOTICE] No trained food-recognition checkpoint found at {self.checkpoint_path}.")
            print("Cannot perform prediction until training has been completed.")

    def _load_model(self):
        """Load state dict and metadata from checkpoint."""
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        num_classes = checkpoint.get("num_classes", self.config.num_classes)
        self.id_to_food = checkpoint.get("id_to_food", self.config.id_to_food)

        self.model = create_food_recognition_model(num_classes=num_classes, pretrained=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

        _, eval_transforms = get_transforms(image_size=self.config.image_size)
        self.transforms = eval_transforms

    def is_ready(self) -> bool:
        """Check if model checkpoint is loaded and ready for inference."""
        return self.model is not None

    def predict(self, image_input: Union[str, Path, Image.Image], top_k: int = 3) -> Dict:
        """
        Run inference on a single image and return predicted food and top-k confidence scores.
        """
        if not self.is_ready():
            return {
                "status": "error",
                "message": f"No trained food-recognition checkpoint found at {self.checkpoint_path}.",
                "food": None,
                "confidence": 0.0,
                "top_predictions": []
            }

        # Open image if path given
        if isinstance(image_input, (str, Path)):
            img_path = Path(image_input)
            if not img_path.exists():
                return {
                    "status": "error",
                    "message": f"Image file not found: {img_path}",
                    "food": None,
                    "confidence": 0.0,
                    "top_predictions": []
                }
            img = Image.open(img_path).convert("RGB")
        elif isinstance(image_input, Image.Image):
            img = image_input.convert("RGB")
        else:
            return {
                "status": "error",
                "message": "Invalid image input type",
                "food": None,
                "confidence": 0.0,
                "top_predictions": []
            }

        img_tensor = self.transforms(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(img_tensor)
            probs = F.softmax(logits, dim=1)[0]
            top_probs, top_indices = torch.topk(probs, min(top_k, len(probs)))

        predicted_idx = top_indices[0].item()
        predicted_conf = float(top_probs[0].item())
        predicted_food = self.id_to_food.get(str(predicted_idx), f"Class {predicted_idx}")

        top_predictions = []
        for prob, idx in zip(top_probs, top_indices):
            idx_int = idx.item()
            name = self.id_to_food.get(str(idx_int), f"Class {idx_int}")
            top_predictions.append({
                "food": name,
                "confidence": round(float(prob.item()), 4),
                "percentage": f"{float(prob.item()) * 100:.2f}%"
            })

        return {
            "status": "success",
            "food": predicted_food,
            "confidence": round(predicted_conf, 4),
            "percentage": f"{predicted_conf * 100:.2f}%",
            "top_predictions": top_predictions
        }


def predict_food(image_path: Union[str, Path], checkpoint_path: Optional[Path] = None, top_k: int = 3) -> Dict:
    """Convenience function for standalone image prediction."""
    predictor = FoodPredictor(checkpoint_path=checkpoint_path)
    return predictor.predict(image_path, top_k=top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FoodFresh AI - Food Recognition Predictor")
    parser.add_argument("image_pos", nargs="?", default=None, help="Path to food image file (positional)")
    parser.add_argument("--image", type=str, default=None, help="Path to food image file (--image)")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to trained .pth checkpoint")
    parser.add_argument("--top_k", type=int, default=3, help="Number of top predictions to display")
    args = parser.parse_args()

    image_path = args.image or args.image_pos
    if not image_path:
        print("Usage: python -m ml.food_recognition.predict <path_to_image> [--checkpoint <path>]")
        sys.exit(1)

    result = predict_food(image_path, checkpoint_path=args.checkpoint, top_k=args.top_k)

    if result.get("status") == "success":
        print(f"Predicted food: {result['food']}")
        print(f"Confidence:     {result['percentage']}")
        print("\nTop predictions:")
        for idx, pred in enumerate(result["top_predictions"], 1):
            print(f"{idx}. {pred['food']} - {pred['percentage']}")
    else:
        print(f"Error: {result.get('message')}")
        sys.exit(1)
