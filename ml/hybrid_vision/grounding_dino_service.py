"""
FoodFresh AI - Grounding DINO Object Detection Service
Open-vocabulary / zero-shot object detector using IDEA-Research/grounding-dino-base.
"""

import logging
import time
from typing import List, Optional
from PIL import Image
import torch
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

from ml.hybrid_vision.config import (
    DEVICE,
    GROUNDING_DINO_BOX_THRESHOLD,
    GROUNDING_DINO_DIR,
    GROUNDING_DINO_REPO,
    GROUNDING_DINO_TEXT_PROMPT,
    GROUNDING_DINO_TEXT_THRESHOLD,
)
from ml.hybrid_vision.schemas import BoundingBox, DetectedObject, GroundingDinoResult

logger = logging.getLogger("foodfresh.hybrid.grounding_dino")

SCENE_OBJECT_LABELS = {
    "table", "countertop", "plate", "bowl", "spoon", "fork", "knife",
    "glass", "cup", "tray", "container", "basket", "cutting board", "bag",
    "hand", "person", "bottle", "refrigerator", "box", "napkin"
}
NON_FOOD_LABELS = SCENE_OBJECT_LABELS


class GroundingDinoService:
    """
    Service wrapper for IDEA-Research/grounding-dino-base zero-shot object detection.
    Detects candidate food items and context objects with open vocabulary prompts.
    """

    _instance: Optional["GroundingDinoService"] = None

    def __init__(self, device: Optional[torch.device] = None):
        self.device = device or DEVICE
        self.processor: Optional[AutoProcessor] = None
        self.model: Optional[AutoModelForZeroShotObjectDetection] = None
        self.is_loaded = False
        self.load_error: Optional[str] = None
        self._load_model()

    @classmethod
    def get_instance(cls) -> "GroundingDinoService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self) -> None:
        """Load processor and model weights from local path or Hugging Face cache."""
        try:
            load_path = str(GROUNDING_DINO_DIR) if GROUNDING_DINO_DIR.exists() else GROUNDING_DINO_REPO
            logger.info(f"Loading Grounding DINO from: {load_path} on {self.device}")
            self.processor = AutoProcessor.from_pretrained(load_path)
            self.model = AutoModelForZeroShotObjectDetection.from_pretrained(load_path).to(self.device)
            self.model.eval()
            self.is_loaded = True
            logger.info("Grounding DINO loaded successfully.")
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load Grounding DINO: {e}")
            self.is_loaded = False

    def detect(
        self,
        image: Image.Image,
        text_prompt: Optional[str] = None,
        box_threshold: float = GROUNDING_DINO_BOX_THRESHOLD,
        text_threshold: float = GROUNDING_DINO_TEXT_THRESHOLD
    ) -> GroundingDinoResult:
        """
        Run zero-shot object detection on an input PIL image.
        Returns detected objects, categorized into food and scene objects, along with latency.
        """
        if not self.is_loaded or self.model is None or self.processor is None:
            return GroundingDinoResult(
                status="model_not_loaded",
                detected_objects=[],
                food_objects=[],
                scene_objects=[],
                error=self.load_error or "Model not loaded"
            )

        start_time = time.perf_counter()
        prompt = text_prompt or GROUNDING_DINO_TEXT_PROMPT
        # Grounding DINO expects text queries ending with a period and separated by periods
        if not prompt.strip().endswith("."):
            prompt = prompt.strip() + "."

        try:
            inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Post-process results into absolute pixel coordinates
            width, height = image.size
            results = self.processor.post_process_grounded_object_detection(
                outputs=outputs,
                input_ids=inputs.input_ids,
                threshold=box_threshold,
                text_threshold=text_threshold,
                target_sizes=[(height, width)]
            )[0]

            detected_objects: List[DetectedObject] = []
            food_objects: List[DetectedObject] = []

            boxes = results.get("boxes", [])
            scores = results.get("scores", [])
            labels = results.get("text_labels") if "text_labels" in results else results.get("labels", [])

            for box, score, label in zip(boxes, scores, labels):
                coords = [round(float(c)) for c in box.tolist()]
                # Ensure coordinates are within image boundaries
                xmin = max(0, min(width, coords[0]))
                ymin = max(0, min(height, coords[1]))
                xmax = max(0, min(width, coords[2]))
                ymax = max(0, min(height, coords[3]))

                clean_label = label.strip().lower()
                is_food = clean_label not in NON_FOOD_LABELS
                conf = round(float(score) * 100.0, 2)

                obj = DetectedObject(
                    label=clean_label,
                    confidence=conf,
                    box=BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax),
                    is_food=is_food
                )
                detected_objects.append(obj)
                if is_food:
                    food_objects.append(obj)

            # Sort detected objects descending by confidence score
            detected_objects.sort(key=lambda o: o.confidence, reverse=True)
            food_objects.sort(key=lambda o: o.confidence, reverse=True)

            # Extract deduplicated scene objects (non-food)
            scene_objects: List[DetectedObject] = []
            seen_scene_labels = set()
            for obj in detected_objects:
                if not obj.is_food and obj.label not in seen_scene_labels:
                    seen_scene_labels.add(obj.label)
                    scene_objects.append(obj)
            scene_objects.sort(key=lambda o: o.confidence, reverse=True)

            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return GroundingDinoResult(
                status="success",
                detected_objects=detected_objects,
                food_objects=food_objects,
                scene_objects=scene_objects,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"Grounding DINO detection failed: {e}")
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            return GroundingDinoResult(
                status="error",
                detected_objects=[],
                food_objects=[],
                scene_objects=[],
                latency_ms=latency,
                error=str(e)
            )



def get_grounding_dino_service() -> GroundingDinoService:
    return GroundingDinoService.get_instance()
