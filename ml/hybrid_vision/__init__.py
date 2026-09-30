"""
FoodFresh AI - Hybrid Pretrained Vision Module
Exports the HybridVisionPipeline and individual service classes.
"""

from ml.hybrid_vision.schemas import HybridVisionResult, PredictionCandidate, DetectedObject
from ml.hybrid_vision.grounding_dino_service import GroundingDinoService, get_grounding_dino_service
from ml.hybrid_vision.siglip2_service import Siglip2Service, get_siglip2_service
from ml.hybrid_vision.raw_food_service import RawFoodService, get_raw_food_service
from ml.hybrid_vision.freshness_service import FreshnessService, get_freshness_service
from ml.hybrid_vision.hybrid_pipeline import HybridVisionPipeline, get_hybrid_vision_pipeline

__all__ = [
    "HybridVisionResult",
    "PredictionCandidate",
    "DetectedObject",
    "GroundingDinoService",
    "get_grounding_dino_service",
    "Siglip2Service",
    "get_siglip2_service",
    "RawFoodService",
    "get_raw_food_service",
    "FreshnessService",
    "get_freshness_service",
    "HybridVisionPipeline",
    "get_hybrid_vision_pipeline",
]
