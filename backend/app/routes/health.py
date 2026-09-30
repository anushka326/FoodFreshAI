from fastapi import APIRouter
from backend.app.model_config import MODEL_CONFIG

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    fr_cfg = MODEL_CONFIG.get("food_recognition", {})
    fresh_cfg = MODEL_CONFIG.get("freshness", {})
    shelf_cfg = MODEL_CONFIG.get("shelf_life", {})

    return {
        "status": "ok",
        "service": "FoodFresh AI backend",
        "pipeline": "Master Hybrid Vision",
        "models": {
            "foodRecognition": {
                "status": fr_cfg.get("status", "ACTIVE"),
                "loaded": fr_cfg.get("is_loaded", True),
                "pipeline": fr_cfg.get("pipeline", "hybrid_pretrained_vision"),
                "detector": "IDEA-Research/grounding-dino-base",
                "foodSemantic": "google/siglip2-base-patch16-224",
                "foodSpecialist": "ibrahimdaud/raw-food-recognition-models",
            },
            "freshness": {
                "status": fresh_cfg.get("status", "ACTIVE"),
                "loaded": fresh_cfg.get("is_loaded", True),
                "version": fresh_cfg.get("model_version", "nathansekar/food-freshness-detector"),
                "checkpoint": fresh_cfg.get("checkpoint_path"),
                "calibrationTemperature": fresh_cfg.get("calibration_temperature", 1.0),
            },
            "shelfLife": {
                "status": shelf_cfg.get("status", "UNKNOWN"),
                "loaded": shelf_cfg.get("is_loaded", False),
                "source": shelf_cfg.get("model_version", "USDA FoodKeeper"),
                "checkpoint": shelf_cfg.get("checkpoint_path"),
            },
            "eatFirstPriority": {
                "status": "ACTIVE",
                "loaded": True,
                "engine": "Deterministic Priority Rules",
            },
        },
        "foodRecognitionModel": {
            "version": "Hybrid Pretrained V1",
            "detector": "grounding-dino-base",
            "semantic": "siglip2-base-patch16-224",
            "specialist": "raw-food-resnet50",
            "loaded": True,
            "status": "ACTIVE",
        },
    }
