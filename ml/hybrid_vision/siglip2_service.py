"""
FoodFresh AI - SigLIP 2 Zero-Shot Food Identification Service
Uses google/siglip2-base-patch16-224 for open-vocabulary image classification with dynamic candidates.
"""

import json
import logging
import time
from typing import Dict, List, Optional
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor

from ml.hybrid_vision.config import DEVICE, FOOD_VOCABULARY_PATH, SIGLIP2_DIR, SIGLIP2_REPO
from ml.hybrid_vision.schemas import PredictionCandidate, Siglip2Result

logger = logging.getLogger("foodfresh.hybrid.siglip2")


class Siglip2Service:
    """
    Zero-shot food classification service powered by Google's SigLIP 2 vision-language model.
    """

    _instance: Optional["Siglip2Service"] = None

    def __init__(self, device: Optional[torch.device] = None):
        self.device = device or DEVICE
        self.processor: Optional[AutoProcessor] = None
        self.model: Optional[AutoModel] = None
        self.vocabulary: Dict[str, List[str]] = {}
        self.all_food_labels: List[str] = []
        self.label_to_category: Dict[str, str] = {}
        self.is_loaded = False
        self.load_error: Optional[str] = None

        self._load_vocabulary()
        self._load_model()

    @classmethod
    def get_instance(cls) -> "Siglip2Service":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_vocabulary(self) -> None:
        """Load curated food vocabulary and category mappings."""
        try:
            if FOOD_VOCABULARY_PATH.exists():
                with open(FOOD_VOCABULARY_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.vocabulary = data.get("categories", {})
                for cat, items in self.vocabulary.items():
                    for item in items:
                        self.all_food_labels.append(item)
                        self.label_to_category[item] = cat
                logger.info(f"Loaded {len(self.all_food_labels)} food labels across {len(self.vocabulary)} categories.")
            else:
                logger.warning(f"Vocabulary file not found at {FOOD_VOCABULARY_PATH}")
        except Exception as e:
            logger.error(f"Error loading food vocabulary: {e}")

    def _load_model(self) -> None:
        """Load SigLIP 2 model and processor."""
        try:
            # Check snapshots or local dir
            load_path = None
            if SIGLIP2_DIR.exists():
                # Check for snapshots directory structure
                snapshots = list(SIGLIP2_DIR.glob("models--*/**/snapshots/*"))
                if snapshots:
                    load_path = str(snapshots[0])
                else:
                    load_path = str(SIGLIP2_DIR)
            if not load_path:
                load_path = SIGLIP2_REPO

            logger.info(f"Loading SigLIP 2 from: {load_path} on {self.device}")
            self.processor = AutoProcessor.from_pretrained(load_path)
            self.model = AutoModel.from_pretrained(load_path).to(self.device)
            self.model.eval()
            self.is_loaded = True
            logger.info("SigLIP 2 loaded successfully.")
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load SigLIP 2: {e}")
            self.is_loaded = False

    def classify(
        self,
        image: Image.Image,
        candidate_labels: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Siglip2Result:
        """
        Classify an image against a candidate set of text labels.
        If candidate_labels is None, uses all curated food labels from the vocabulary.
        """
        if not self.is_loaded or self.model is None or self.processor is None:
            return Siglip2Result(
                status="model_not_loaded",
                top_predictions=[],
                error=self.load_error or "Model not loaded"
            )

        start_time = time.perf_counter()
        candidates = candidate_labels or self.all_food_labels
        if not candidates:
            return Siglip2Result(
                status="no_candidates",
                top_predictions=[],
                error="No candidate labels provided"
            )

        try:
            # Format candidate prompts with descriptive prefixes for zero-shot accuracy
            prompts = [f"a photo of a {label}" for label in candidates]

            inputs = self.processor(
                text=prompts,
                images=image,
                padding="max_length",
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image  # [1, num_candidates]
                # SigLIP 2 uses sigmoid / softmax for similarity
                probs = torch.softmax(logits_per_image, dim=1).squeeze(0)

            scores_list = probs.cpu().tolist()
            ranked = sorted(
                zip(candidates, scores_list),
                key=lambda x: x[1],
                reverse=True
            )

            top_predictions: List[PredictionCandidate] = []
            for label, score in ranked[:top_k]:
                category = self.label_to_category.get(label, "OTHER FOOD")
                top_predictions.append(
                    PredictionCandidate(
                        label=label,
                        confidence=round(score * 100.0, 2),
                        category=category
                    )
                )

            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return Siglip2Result(
                status="success",
                top_predictions=top_predictions,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"SigLIP 2 classification failed: {e}")
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return Siglip2Result(
                status="error",
                top_predictions=[],
                latency_ms=latency,
                error=str(e)
            )


def get_siglip2_service() -> Siglip2Service:
    return Siglip2Service.get_instance()
