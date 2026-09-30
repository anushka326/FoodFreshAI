"""
FoodFresh AI - Food Recognition Service (Master Hybrid Vision)
Coordinates between the FastAPI endpoint and the Master Hybrid Vision Pipeline.
"""

from io import BytesIO
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, UnidentifiedImageError

from backend.app.model_config import MODEL_CONFIG
from backend.app.services.food_form_service import infer_food_form
from ml.hybrid_vision.hybrid_pipeline import get_hybrid_vision_pipeline

logger = logging.getLogger("foodfresh.food_recognition")


class FoodRecognitionService:
    """
    Singleton service managing the Hybrid Vision Pipeline lifecycle and inference.
    Replaces obsolete closed-set models with open-vocabulary detector, zero-shot classifier,
    raw food specialist, and visible freshness detector.
    """

    _instance: Optional["FoodRecognitionService"] = None

    def __init__(self):
        logger.info("Initializing FoodRecognitionService with Hybrid Vision Pipeline...")
        self.pipeline = get_hybrid_vision_pipeline()
        self.status = "ready"
        self.is_loaded = True
        logger.info("FoodRecognitionService initialized.")

    @classmethod
    def get_instance(cls) -> "FoodRecognitionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict_image(
        self,
        image_bytes: bytes,
        top_k: int = 5,
        storage_type: str = "countertop",
        days_stored: int = 0
    ) -> Dict[str, Any]:
        """
        Execute full end-to-end hybrid analysis on uploaded image bytes.
        """
        # Validate uploaded image bytes
        try:
            img = Image.open(BytesIO(image_bytes))
            img.verify()
        except (UnidentifiedImageError, OSError, ValueError) as e:
            logger.warning(f"Invalid or unreadable image uploaded: {e}")
            return {
                "success": False,
                "analysisStatus": "error",
                "detectedFood": None,
                "recognitionConfidence": None,
                "topPredictions": [],
                "detectedObjects": [],
                "foodRecognition": {},
                "freshness": {"status": "unavailable", "label": None, "confidence": None, "score": None, "source": "nathansekar/food-freshness-detector"},
                "shelfLife": {"status": "unavailable", "reason": "No food detected in invalid image."},
                "eatFirstPriority": {"status": "unavailable", "reason": "Eat First requires an available shelf-life estimate."},
                "modelVersions": {},
                "status": "invalid_image",
                "message": "Please upload a valid food image (JPG, JPEG, PNG, or WEBP)."
            }

        try:
            # Reopen fresh PIL stream since verify() invalidates the image handle
            pil_img = Image.open(BytesIO(image_bytes))
            res = self.pipeline.analyze(
                pil_img,
                top_k=top_k,
                storage_type=storage_type,
                days_stored=days_stored
            )

            # Format top predictions ensuring compatibility with frontend (food + confidence)
            formatted_top_preds = [
                {
                    "food": p.label,
                    "confidence": p.confidence,
                    "percentage": f"{p.confidence:.1f}%",
                    "category": p.category
                }
                for p in res.topPredictions
            ]

            sl = res.shelfLife.model_dump() if res.shelfLife else {}
            rem = (sl.get("remaining") or {}) if isinstance(sl.get("remaining"), dict) else {}
            food_form = infer_food_form(
                res.detectedFood,
                freshness_label=res.freshness.label if res.freshness else None,
            )
            freshness_uncertain = res.freshness.status in ("uncertain", "not_available") if res.freshness else True
            shelf_available = sl.get("status") == "available"

            return {
                "success": True,
                "analysisStatus": res.analysisStatus,
                "detectedFood": res.detectedFood,
                "foodForm": food_form,
                "recognitionConfidence": res.recognitionConfidence,
                "topPredictions": formatted_top_preds,
                "detectedObjects": [
                    {
                        "label": o.label,
                        "confidence": o.confidence,
                        "box": o.box.model_dump() if o.box else None
                    }
                    for o in res.detectedObjects
                ],
                "foodRecognition": {
                    "groundingDino": res.foodRecognition.groundingDino,
                    "rawFoodResNet": res.foodRecognition.rawFoodResNet,
                    "siglip2": res.foodRecognition.siglip2,
                },
                "freshness": {
                    "status": res.freshness.status,
                    "label": res.freshness.label,
                    "confidence": res.freshness.score,
                    "score": res.freshness.score,
                    "freshnessUncertain": freshness_uncertain,
                    "source": res.freshness.modelVersion,
                    "allScores": res.freshness.all_scores,
                    "modelVersion": res.freshness.modelVersion,
                },
                "shelfLife": res.shelfLife.model_dump(),
                "shelfLifeAvailable": shelf_available,
                "shelfLifeSource": sl.get("source") or "USDA FoodKeeper",
                "shelfLifeModelVersion": "foodkeeper_rules_v1",
                "estimatedQualityDays": rem.get("maxDays") if rem.get("maxDays") is not None else rem.get("minDays"),
                "eatFirstPriority": res.eatFirstPriority.model_dump(),
                "modelVersions": {
                    "detector": res.modelVersions.detector,
                    "semantic": res.modelVersions.semantic,
                    "foodSpecialist": res.modelVersions.foodSpecialist,
                    "freshness": MODEL_CONFIG["freshness"]["model_version"],
                    "shelfLife": "foodkeeper_rules_v1",
                    "food": MODEL_CONFIG["food_recognition"]["version"],
                },
                "source": "ml",
                "model": "Master Hybrid Vision",
                "modelVersion": MODEL_CONFIG["food_recognition"]["version"],
                "status": res.analysisStatus,
                "latencyMs": res.latencyMs,
                "message": res.message
            }

        except Exception as e:
            logger.error(f"Inference error during hybrid pipeline execution: {e}", exc_info=True)
            return {
                "success": False,
                "analysisStatus": "error",
                "detectedFood": None,
                "recognitionConfidence": None,
                "topPredictions": [],
                "detectedObjects": [],
                "foodRecognition": {},
                "freshness": {"status": "unavailable", "label": None, "confidence": None, "score": None, "source": "nathansekar/food-freshness-detector"},
                "shelfLife": {"status": "unavailable", "reason": str(e)},
                "eatFirstPriority": {"status": "unavailable", "reason": "Eat First requires an available shelf-life estimate."},
                "modelVersions": {},
                "status": "pipeline_error",
                "message": f"Inference pipeline encountered an error: {e}"
            }


def get_food_recognition_service() -> FoodRecognitionService:
    return FoodRecognitionService.get_instance()

