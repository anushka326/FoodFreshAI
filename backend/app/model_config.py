"""
FoodFresh AI - Central Model Configuration
Defines active state and lifecycle configurations for the Master Hybrid Vision Pipeline.
"""

from typing import Any, Dict

MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "food_recognition": {
        "status": "ACTIVE",
        "pipeline": "hybrid_pretrained_vision",
        "version": "Hybrid Pretrained V1",
        "models": {
            "detector": "IDEA-Research/grounding-dino-base",
            "semantic": "google/siglip2-base-patch16-224",
            "specialist": "ibrahimdaud/raw-food-recognition-models (ResNet-50)",
        },
        "is_loaded": True,
        "message": "Master Hybrid Vision pipeline is active."
    },
    "freshness": {
        "status": "ACTIVE",
        "model_architecture": "ResNet-18 fastai-style head",
        "model_version": "AgriFreshNET Fine-Tuned ResNet-18 (V2)",
        "checkpoint_path": "models/trained/freshness_model_v2.pth",
        "class_mapping_path": "models/pretrained/freshness_resnet18/vocab.json",
        "classes": ["fresh", "rotten", "slightly_spoiled"],
        "calibration_temperature": 1.1118282079696655,
        "is_loaded": True,
        "message": "Fine-tuned V2 is active; V1 is the fallback."
    },
    "shelf_life": {
        "status": "ACTIVE",
        "model_architecture": "Ensemble ML Regressor + USDA FoodKeeper Safety Guardrails",
        "model_version": "Shelf-Life ML V1 (Trained Regressor)",
        "checkpoint_path": "models/trained/shelf_life_model.joblib",
        "metrics": {
            "test_mae_days": 0.0038,
            "test_rmse_days": 0.0407,
            "test_r2_score": 0.9997,
            "test_samples": 6192
        },
        "is_loaded": True,
        "message": "Trained Shelf-Life ML Regressor is active with USDA FoodKeeper safety guardrails."
    }
}

try:
    from backend.app.dataset_registry import DATASET_REGISTRY
except ImportError:
    DATASET_REGISTRY = {}

