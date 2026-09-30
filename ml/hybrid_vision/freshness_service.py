"""
FoodFresh AI - Freshness Detector Service (V2 Promoted with Confidence Calibration)
Uses fine-tuned ResNet-18 (models/trained/freshness_model_v2.pth) on AgriFreshNET produce dataset
with fallback to nathansekar/food-freshness-detector.
Includes two-tier confidence calibration and uncertainty gating.
Classes from model vocab: fresh, rotten, slightly_spoiled
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
import torch
import torch.nn as nn
from torchvision.models import resnet18
import torchvision.transforms as T

from backend.app.model_config import MODEL_CONFIG
from ml.hybrid_vision.config import DEVICE, FRESHNESS_VOCAB, FRESHNESS_WEIGHTS
from ml.hybrid_vision.schemas import FreshnessResult

logger = logging.getLogger("foodfresh.hybrid.freshness")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRESHNESS_CONFIG = MODEL_CONFIG["freshness"]
FRESHNESS_V2_WEIGHTS = PROJECT_ROOT / FRESHNESS_CONFIG["checkpoint_path"]

# Calibration-aware preprocessing transform
EVAL_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class AdaptiveConcatPool2d(nn.Module):
    """Adaptive Concat Pooling layer (AvgPool + MaxPool concatenated)."""
    def __init__(self, sz=None):
        super().__init__()
        self.output_size = sz or 1
        self.ap = nn.AdaptiveAvgPool2d(self.output_size)
        self.mp = nn.AdaptiveMaxPool2d(self.output_size)

    def forward(self, x):
        return torch.cat([self.mp(x), self.ap(x)], 1)


class Flatten(nn.Module):
    """Flattens feature map to 2D vector for linear classifier."""
    def forward(self, x):
        return x.view(x.size(0), -1)


class FreshnessService:
    """
    Visible freshness classification service.
    Estimates visible surface freshness ('Fresh', 'Slightly Spoiled', 'Rotten')
    or returns 'Freshness Uncertain' when visual evidence is ambiguous.
    """

    _instance: Optional["FreshnessService"] = None

    def __init__(self, device: Optional[torch.device] = None):
        self.device = device or DEVICE
        self.vocab: List[str] = []
        self.model: Optional[nn.Module] = None
        self.is_loaded = False
        self.load_error: Optional[str] = None
        self.model_version_label = FRESHNESS_CONFIG["model_version"]
        self.calibration_temperature = 1.0

        self._load_vocab()
        self._load_model()

    @classmethod
    def get_instance(cls) -> "FreshnessService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_vocab(self) -> None:
        """Load official model vocabulary."""
        try:
            if FRESHNESS_VOCAB.exists():
                with open(FRESHNESS_VOCAB, "r", encoding="utf-8") as f:
                    self.vocab = json.load(f)
                logger.info(f"Loaded Freshness vocabulary: {self.vocab}")
            else:
                self.vocab = ["fresh", "rotten", "slightly_spoiled"]
                logger.warning(f"Vocab file not found at {FRESHNESS_VOCAB}. Using default: {self.vocab}")
        except Exception as e:
            logger.error(f"Failed to load freshness vocab: {e}")
            self.vocab = ["fresh", "rotten", "slightly_spoiled"]

    def _load_model(self) -> None:
        """Construct ResNet-18 fastai architecture and load weights."""
        try:
            # Check for promoted fine-tuned V2 checkpoint first
            if FRESHNESS_V2_WEIGHTS.exists():
                weights_path = FRESHNESS_V2_WEIGHTS
                self.calibration_temperature = float(FRESHNESS_CONFIG.get("calibration_temperature", 1.0))
                logger.info(f"Loading Promoted Freshness V2 model from {weights_path} on {self.device}")
            else:
                weights_path = FRESHNESS_WEIGHTS
                self.model_version_label = "nathansekar/food-freshness-detector (V1)"
                self.calibration_temperature = 1.0
                logger.info(f"Loading Freshness V1 model from {weights_path} on {self.device}")

            base = resnet18(weights=None)
            body = nn.Sequential(*list(base.children())[:-2])

            head = nn.Sequential(
                AdaptiveConcatPool2d(),
                Flatten(),
                nn.BatchNorm1d(1024),
                nn.Dropout(0.25),
                nn.Linear(1024, 512, bias=False),
                nn.ReLU(inplace=True),
                nn.BatchNorm1d(512),
                nn.Dropout(0.5),
                nn.Linear(512, len(self.vocab), bias=False)
            )

            model = nn.Sequential(body, head)
            state_dict = torch.load(weights_path, map_location=self.device)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            self.model = model
            self.is_loaded = True
            logger.info(f"Freshness model ({self.model_version_label}) loaded successfully.")
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load Freshness model: {e}")
            self.is_loaded = False

    def predict(self, image: Image.Image) -> FreshnessResult:
        """
        Estimate visible freshness state of a food image.
        Returns FreshnessResult with calibrated label, confidence score, and distribution.
        """
        if not self.is_loaded or self.model is None or not self.vocab:
            return FreshnessResult(
                status="not_available",
                label=None,
                score=None,
                error=self.load_error or "Model not loaded"
            )

        start_time = time.perf_counter()
        try:
            tensor = EVAL_TRANSFORM(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                probs = torch.softmax(logits / self.calibration_temperature, dim=1).squeeze(0)

            scores_list = probs.cpu().tolist()

            label_display_map = {
                "fresh": "Fresh",
                "slightly_spoiled": "Slightly Spoiled",
                "rotten": "Rotten"
            }

            all_scores: Dict[str, float] = {}
            for name, score in zip(self.vocab, scores_list):
                disp_name = label_display_map.get(name.lower(), name.title())
                all_scores[disp_name] = round(score * 100.0, 2)

            top_idx = int(torch.argmax(probs).item())
            top_raw_label = self.vocab[top_idx]
            top_label = label_display_map.get(top_raw_label.lower(), top_raw_label.title())
            top_score = round(scores_list[top_idx] * 100.0, 2)

            # Phase 6: Confidence Calibration & Uncertainty Decision Gate
            # Calculate separation margin between top-1 and runner-up probability
            sorted_scores = sorted(scores_list, reverse=True)
            margin = (sorted_scores[0] - sorted_scores[1]) * 100.0 if len(sorted_scores) > 1 else 100.0

            if top_score < 50.0 or margin < 10.0:
                final_status = "uncertain"
                final_label = "Freshness Uncertain"
            elif top_score < 65.0:
                final_status = "success"
                final_label = f"{top_label} (Moderate Confidence)"
            else:
                final_status = "success"
                final_label = top_label

            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return FreshnessResult(
                status=final_status,
                label=final_label,
                score=top_score,
                all_scores=all_scores,
                modelVersion=self.model_version_label,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"Freshness prediction failed: {e}")
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return FreshnessResult(
                status="not_available",
                label=None,
                score=None,
                modelVersion=self.model_version_label,
                latency_ms=latency,
                error=str(e)
            )


def get_freshness_service() -> FreshnessService:
    return FreshnessService.get_instance()
