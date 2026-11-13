"""
FoodFresh AI - Raw Food ResNet-50 Specialist Service
90-class raw food classification model fine-tuned on the merged raw food dataset.
Repository: ibrahimdaud/raw-food-recognition-models
"""

import json
import logging
import time
from typing import List, Optional
from PIL import Image
import torch
import torch.nn as nn
from torchvision.models import resnet50

from ml.hybrid_vision.config import DEVICE, RAW_FOOD_CLASSES, RAW_FOOD_WEIGHTS
from ml.hybrid_vision.preprocessing import preprocess_for_resnet
from ml.hybrid_vision.schemas import PredictionCandidate, RawFoodResult

logger = logging.getLogger("foodfresh.hybrid.raw_food_resnet")


class RawFoodService:
    """
    Specialist classifier for 90 raw food categories (fruits, vegetables, dairy, etc.).
    Uses ResNet-50 architecture loaded with trained weights.
    """

    _instance: Optional["RawFoodService"] = None

    def __init__(self, device: Optional[torch.device] = None):
        self.device = device or DEVICE
        self.classes: List[str] = []
        self.model: Optional[nn.Module] = None
        self.is_loaded = False
        self.load_error: Optional[str] = None

        self._load_classes()
        self._load_model()

    @classmethod
    def get_instance(cls) -> "RawFoodService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_classes(self) -> None:
        """Load verified class names mapping for the 90 categories."""
        try:
            if RAW_FOOD_CLASSES.exists():
                with open(RAW_FOOD_CLASSES, "r", encoding="utf-8") as f:
                    self.classes = json.load(f)
                logger.info(f"Loaded {len(self.classes)} verified raw food classes.")
            else:
                logger.error(f"Class mapping file not found at: {RAW_FOOD_CLASSES}")
        except Exception as e:
            logger.error(f"Failed to load raw food class names: {e}")

    def _load_model(self) -> None:
        """Build ResNet-50 architecture and load checkpoint weights."""
        if not self.classes:
            self.load_error = "Classes list is empty."
            return

        try:
            logger.info(f"Loading Raw Food ResNet-50 from {RAW_FOOD_WEIGHTS} on {self.device}")
            model = resnet50(weights=None)
            model.fc = nn.Linear(2048, len(self.classes))

            checkpoint = torch.load(RAW_FOOD_WEIGHTS, map_location=self.device)
            state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            self.model = model
            self.is_loaded = True
            logger.info("Raw Food ResNet-50 loaded successfully.")
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load Raw Food ResNet-50: {e}")
            self.is_loaded = False

    def classify(self, image: Image.Image, top_k: int = 5) -> RawFoodResult:
        """
        Classify raw food image into 90 categories.
        Returns top-k predicted classes with softmax percentage confidences.
        """
        if not self.is_loaded or self.model is None or not self.classes:
            return RawFoodResult(
                status="model_not_loaded",
                top_predictions=[],
                error=self.load_error or "Model or classes not loaded"
            )

        start_time = time.perf_counter()
        try:
            tensor = preprocess_for_resnet(image, self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                probs = torch.softmax(logits, dim=1).squeeze(0)

            top_probs, top_indices = torch.topk(probs, k=min(top_k, len(self.classes)))

            top_predictions: List[PredictionCandidate] = []
            for prob, idx in zip(top_probs.cpu().tolist(), top_indices.cpu().tolist()):
                raw_name = self.classes[idx]
                clean_name = raw_name.replace("_", " ").title()
                top_predictions.append(
                    PredictionCandidate(
                        label=clean_name,
                        confidence=round(prob * 100.0, 2),
                        category="Raw Food Specialist"
                    )
                )

            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return RawFoodResult(
                status="success",
                top_predictions=top_predictions,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"Raw food classification failed: {e}")
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return RawFoodResult(
                status="error",
                top_predictions=[],
                latency_ms=latency,
                error=str(e)
            )


def get_raw_food_service() -> RawFoodService:
    return RawFoodService.get_instance()
