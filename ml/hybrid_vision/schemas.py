"""
FoodFresh AI - Hybrid Vision Schemas
Pydantic schemas and dataclasses for hybrid vision model inference and API exchange.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates [xmin, ymin, xmax, ymax] in pixel coordinates."""
    xmin: int
    ymin: int
    xmax: int
    ymax: int


class DetectedObject(BaseModel):
    """An object detected by Grounding DINO."""
    label: str
    confidence: float
    box: BoundingBox
    is_food: bool = True


class PredictionCandidate(BaseModel):
    """Candidate prediction with label and confidence score (0-100%)."""
    label: str
    confidence: float
    category: Optional[str] = None


class GroundingDinoResult(BaseModel):
    """Output from Grounding DINO detection service."""
    status: str = "success"
    detected_objects: List[DetectedObject] = Field(default_factory=list)
    food_objects: List[DetectedObject] = Field(default_factory=list)
    scene_objects: List[DetectedObject] = Field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None


class Siglip2Result(BaseModel):
    """Output from SigLIP 2 zero-shot image classification."""
    status: str = "success"
    top_predictions: List[PredictionCandidate] = Field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None


class RawFoodResult(BaseModel):
    """Output from Raw Food ResNet-50 specialist classification."""
    status: str = "success"
    top_predictions: List[PredictionCandidate] = Field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None


class FreshnessResult(BaseModel):
    """Output from Freshness classification model."""
    status: str = "success"
    label: Optional[str] = None  # e.g., 'Fresh', 'Slightly Spoiled', 'Rotten'
    score: Optional[float] = None
    all_scores: Dict[str, float] = Field(default_factory=dict)
    modelVersion: str = "nathansekar/food-freshness-detector"
    latency_ms: float = 0.0
    error: Optional[str] = None


class ReferenceDuration(BaseModel):
    minDays: Optional[int] = None
    maxDays: Optional[int] = None


class RemainingDuration(BaseModel):
    minDays: Optional[int] = None
    maxDays: Optional[int] = None


class ShelfLifeResult(BaseModel):
    """Shelf life estimation from FoodKeeper."""
    status: str = "unavailable"
    food: Optional[str] = None
    storageType: Optional[str] = None
    daysStored: Optional[int] = 0
    referenceDuration: Optional[ReferenceDuration] = None
    remaining: Optional[RemainingDuration] = None
    unit: str = "days"
    source: str = "USDA FoodKeeper"
    isEstimate: bool = True
    heuristicApplied: bool = False
    reason: Optional[str] = None
    tips: Optional[str] = None


class EatFirstPriorityResult(BaseModel):
    """Deterministic Eat First consumption priority."""
    status: str = "unavailable"
    priority: Optional[str] = None
    score: Optional[int] = None
    urgencyLabel: Optional[str] = None
    reason: Optional[str] = None


class ModelVersions(BaseModel):
    """Model version tracking for transparency and auditability."""
    detector: str = "IDEA-Research/grounding-dino-base"
    semantic: str = "google/siglip2-base-patch16-224"
    foodSpecialist: str = "ibrahimdaud/raw-food-recognition-models"
    freshness: str = "nathansekar/food-freshness-detector"


class FoodRecognitionSources(BaseModel):
    """Detailed outputs from each individual food recognition model."""
    groundingDino: Optional[Dict[str, Any]] = None
    rawFoodResNet: Optional[Dict[str, Any]] = None
    siglip2: Optional[Dict[str, Any]] = None


class HybridVisionResult(BaseModel):
    """
    Standard FoodFresh AI hybrid vision result returned by pipeline and backend API.
    """
    success: bool = True
    analysisStatus: str = "success"  # "success", "uncertain", "no_food_detected", "error"
    detectedFood: Optional[str] = None
    recognitionConfidence: Optional[float] = None
    topPredictions: List[PredictionCandidate] = Field(default_factory=list)
    detectedObjects: List[DetectedObject] = Field(default_factory=list)
    foodRecognition: FoodRecognitionSources = Field(default_factory=FoodRecognitionSources)
    freshness: FreshnessResult = Field(default_factory=FreshnessResult)
    shelfLife: ShelfLifeResult = Field(default_factory=ShelfLifeResult)
    eatFirstPriority: EatFirstPriorityResult = Field(default_factory=EatFirstPriorityResult)
    modelVersions: ModelVersions = Field(default_factory=ModelVersions)
    latencyMs: Dict[str, float] = Field(default_factory=dict)
    message: Optional[str] = None

