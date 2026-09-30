"""
FoodFresh AI - Freshness Inference Module
Predicts freshness status (Fresh, Semi-Fresh, Rotten) for a single input image.
NOTE: Requires trained checkpoint 'models/trained/freshness_classifier.pth'.
In Step 10, the architecture is prepared but model training is deferred to Step 11.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union
from PIL import Image, ImageOps
import torch
import torch.nn.functional as F

from ml.freshness.config import FreshnessConfig
from ml.freshness.model import create_freshness_model
from ml.freshness.transforms import get_freshness_transforms
from ml.freshness.utils import load_checkpoint


class FreshnessPredictor:
    """
    Inference predictor for single-image freshness classification.
    """

    def __init__(self, checkpoint_path: Optional[Path] = None, config: Optional[FreshnessConfig] = None):
        self.config = config or FreshnessConfig()
        self.checkpoint_path = checkpoint_path or self.config.checkpoint_path
        self.device = self.config.device

        # Setup transforms
        _, self.transform = get_freshness_transforms(image_size=self.config.image_size)

        # Build model architecture
        self.model = create_freshness_model(
            num_classes=self.config.num_classes,
            pretrained=False
        )

        if not self.checkpoint_path.exists():
            self.model_loaded = False
        else:
            load_checkpoint(self.checkpoint_path, self.model, device=self.device)
            self.model_loaded = True

        self.model.to(self.device)
        self.model.eval()

    @torch.no_grad()
    def predict_image(self, image_input: Union[str, Path, Image.Image]) -> Dict[str, Any]:
        """
        Run inference on a single image.

        Args:
            image_input: File path (str/Path) or PIL Image object.

        Returns:
            Dictionary with freshness, confidence, probabilities, and status.
        """
        if not self.model_loaded:
            return {
                "success": False,
                "freshness": None,
                "confidence": 0.0,
                "status": "model_not_trained",
                "message": f"Checkpoint not found at {self.checkpoint_path}. Train the model first."
            }

        if isinstance(image_input, (str, Path)):
            with Image.open(image_input) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGB")
                tensor = self.transform(img).unsqueeze(0).to(self.device)
        elif isinstance(image_input, Image.Image):
            img = ImageOps.exif_transpose(image_input).convert("RGB")
            tensor = self.transform(img).unsqueeze(0).to(self.device)
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

        logits = self.model(tensor)
        probs = F.softmax(logits, dim=1).squeeze(0)

        pred_idx = torch.argmax(probs).item()
        confidence = probs[pred_idx].item() * 100.0

        pred_label = self.config.id_to_freshness.get(str(pred_idx), f"Class_{pred_idx}")

        all_probs = {
            self.config.id_to_freshness.get(str(i), f"Class_{i}"): round(probs[i].item() * 100.0, 2)
            for i in range(self.config.num_classes)
        }

        return {
            "success": True,
            "freshness": pred_label,
            "confidence": round(confidence, 2),
            "probabilities": all_probs,
            "status": "success"
        }
