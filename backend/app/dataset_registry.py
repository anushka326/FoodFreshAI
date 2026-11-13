"""
FoodFresh AI - Dataset Registry
Central registry of all data sources utilized by the FoodFresh AI platform.
Maintains strict separation between Real Datasets, Authoritative Reference Knowledge,
and Synthetic Auxiliary Datasets.
"""

from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATASET_REGISTRY: Dict[str, Dict[str, Any]] = {
    "synthetic_freshness_shelf_life": {
        "dataset_name": "FoodFreshAI Synthetic Freshness & Shelf-Life Dataset",
        "dataset_type": "synthetic_structured_reference",
        "path": "data/raw/Synthetic data/FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv",
        "readme": "data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_README.md",
        "schema": "data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_Schema.json",
        "absolute_csv_path": str(PROJECT_ROOT / "data" / "raw" / "Synthetic data" / "FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv"),
        "real_image_data": False,
        "ground_truth_status": "synthetic_rule_based",
        "primary_use": "development_testing_reference",
        "training_status": "not_used_for_current_model_training",
        "rows_count": 41280,
        "food_classes_count": 43,
        "domains": ["produce", "bakery"],
        "policy": {
            "produce_countertop_max_days": 7,
            "produce_refrigerated_max_days": 15,
            "bakery_uses_stale_or_moldy_not_rotten": True,
            "low_light_does_not_by_itself_change_freshness_label": True,
        },
        "notes": (
            "Synthetic metadata for model prototyping, calibration, UI regression, "
            "edge-case coverage, and augmentation planning. "
            "It is NOT a food-safety ground truth dataset and MUST NOT be used to retrain current models."
        ),
    },
    "agrifreshnet": {
        "dataset_name": "AgriFreshNET Produce Freshness and Shelf-Life Image Dataset",
        "dataset_type": "real_image_dataset",
        "path": "data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase",
        "class_path": "data/raw/AgriFreshNET Freshness and Shelf-Life Image Datase/Processed Data/Processed Data",
        "total_images": 14160,
        "classes_count": 24,
        "commodities": ["banana", "bittermelon", "cucumber", "eggplant", "orange", "papaya", "pineapple", "tomato"],
        "real_image_data": True,
        "ground_truth_status": "real_world_laboratory_captured",
        "primary_use": "freshness_model_training_and_validation",
        "training_status": "active_in_freshness_resnet18_v2",
        "notes": "Primary real-world condition and visible degradation dataset.",
    },
    "fruits_360": {
        "dataset_name": "Fruits-360 Produce Recognition Dataset",
        "dataset_type": "real_image_dataset",
        "path": "data/raw/fruits-360-100x100-main",
        "training_path": "data/raw/fruits-360-100x100-main/Training",
        "test_path": "data/raw/fruits-360-100x100-main/Test",
        "real_image_data": True,
        "ground_truth_status": "real_world_studio_captured",
        "primary_use": "recognition_benchmarking",
        "training_status": "reference_benchmark",
        "notes": "Multi-angle produce images across cultivars.",
    },
    "foodkeeper": {
        "dataset_name": "USDA FoodKeeper Food Storage Guidelines",
        "dataset_type": "authoritative_reference_data",
        "path": "data/raw/foodkeeper/FoodKeeper.json",
        "products_count": 661,
        "categories_count": 25,
        "real_image_data": False,
        "ground_truth_status": "official_usda_guidance",
        "primary_use": "canonical_shelf_life_reference",
        "training_status": "not_applicable",
        "notes": "Authoritative empirical storage guidelines from USDA FoodKeeper.",
    },
}


def get_dataset_info(dataset_key: str) -> Dict[str, Any]:
    """Retrieve metadata entry for a registered dataset."""
    return DATASET_REGISTRY.get(dataset_key, {})


def list_registered_datasets() -> Dict[str, Dict[str, Any]]:
    """List all registered datasets in FoodFresh AI."""
    return DATASET_REGISTRY
