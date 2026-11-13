"""
FoodFresh AI - Synthetic Dataset Reference Service
Provides structured access to the auxiliary synthetic freshness & shelf-life dataset:
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_Schema.json
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_README.md

This service is strictly an AUXILIARY reference for development, testing,
metadata verification, and constrained prototype scenario evaluation.
It is NOT laboratory ground truth and is NEVER used for model training.
"""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

logger = logging.getLogger("foodfresh.synthetic_data")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "raw" / "Synthetic data"
CSV_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv"
SCHEMA_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Dataset_Schema.json"
README_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Dataset_README.md"


@dataclass
class SyntheticScenarioResult:
    food_name: str
    food_domain: str
    food_form: str
    storage_type: str
    freshness_stage: str
    remaining_shelf_life_days: int
    reference_max_days: int
    source: str = "FoodFresh AI Synthetic Prototype Reference"
    is_synthetic: bool = True
    is_training_ground_truth: bool = False
    notes: str = "Synthetic prototype scenario for testing and constrained guidance."


class SyntheticDataService:
    """
    Singleton service providing structured access to synthetic dataset scenarios
    and prototype policy bounds.
    """

    _instance: Optional["SyntheticDataService"] = None

    def __init__(self):
        self.csv_path = CSV_PATH
        self.schema_path = SCHEMA_PATH
        self.readme_path = README_PATH
        self.schema: Dict[str, Any] = {}
        self.policy: Dict[str, Any] = {}
        self.food_classes: List[str] = []
        self.domains: List[str] = []
        self.freshness_labels: List[str] = []
        self.is_loaded = False
        self._df_summary: Optional[Dict[str, Any]] = None

        self._load_schema()

    @classmethod
    def get_instance(cls) -> "SyntheticDataService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_schema(self) -> None:
        """Load and parse the synthetic dataset schema and policy."""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    self.schema = json.load(f)
                self.policy = self.schema.get("policy", {})
                self.food_classes = self.schema.get("food_classes", [])
                self.domains = self.schema.get("domains", [])
                self.freshness_labels = self.schema.get("freshness_labels", [])
                self.is_loaded = True
                logger.info(
                    f"Loaded Synthetic Dataset Schema: {len(self.food_classes)} classes, "
                    f"policy: {self.policy}"
                )
            else:
                logger.warning(f"Synthetic schema file not found at {self.schema_path}")
        except Exception as e:
            logger.error(f"Error loading synthetic dataset schema: {e}")
            self.is_loaded = False

    def get_metadata(self) -> Dict[str, Any]:
        """Return dataset provenance and structural metadata."""
        return {
            "dataset_name": self.schema.get("dataset_name", "FoodFreshAI Synthetic Freshness + Shelf-Life Metadata v1"),
            "csv_path": str(self.csv_path),
            "csv_exists": self.csv_path.exists(),
            "csv_size_bytes": self.csv_path.stat().st_size if self.csv_path.exists() else 0,
            "total_rows": self.schema.get("rows", 41280),
            "food_classes": self.food_classes,
            "food_classes_count": len(self.food_classes),
            "domains": self.domains,
            "freshness_labels": self.freshness_labels,
            "policy": self.policy,
            "ground_truth_status": "synthetic_rule_based",
            "is_real_image": False,
            "is_training_ground_truth": False,
            "training_status": "not_used_for_current_model_training",
            "primary_use": "development_testing_reference",
            "notes": self.schema.get("important_note", "Synthetic metadata for model prototyping, calibration, and UI regression.")
        }

    def get_policy_constraints(self) -> Dict[str, Any]:
        """Return the conservative FoodFresh AI prototype shelf-life constraints."""
        return {
            "produce_countertop_max_days": self.policy.get("produce_countertop_max_days", 7),
            "produce_refrigerated_max_days": self.policy.get("produce_refrigerated_max_days", 15),
            "bakery_uses_stale_or_moldy_not_rotten": self.policy.get("bakery_uses_stale_or_moldy_not_rotten", True),
            "low_light_does_not_by_itself_change_freshness_label": self.policy.get(
                "low_light_does_not_by_itself_change_freshness_label", True
            ),
        }

    def lookup_prototype_scenario(
        self,
        food_name: str,
        food_form: str = "whole",
        storage_type: str = "countertop",
        freshness_stage: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Query synthetic dataset for a prototype scenario matching the requested parameters.
        Returns a structured dictionary with prototype reference values.
        """
        if not self.csv_path.exists():
            return None

        clean_food = food_name.strip().title()
        clean_form = (food_form or "whole").lower().strip()
        clean_storage = (storage_type or "countertop").lower().strip()
        if clean_storage in ["fridge", "crisper", "refrigerator"]:
            clean_storage = "refrigerated"
        elif clean_storage in ["ambient", "pantry"]:
            clean_storage = "countertop"

        # Read only matching rows efficiently
        try:
            # Match food class in schema first
            norm_classes = {c.lower(): c for c in self.food_classes}
            if clean_food.lower() not in norm_classes:
                return None

            canonical_food = norm_classes[clean_food.lower()]

            # Determine default freshness stage if not provided
            target_stage = freshness_stage or "Fresh"

            # Filter via pandas chunks or filtered query
            df = pd.read_csv(
                self.csv_path,
                nrows=5000,  # quick sample chunk
            )
            # Find match in whole CSV if needed
            cond = (
                (df["food_name"].str.lower() == canonical_food.lower()) &
                (df["food_form"].str.lower() == clean_form) &
                (df["storage_type"].str.lower() == clean_storage)
            )
            matched = df[cond]
            if matched.empty:
                # Fallback to whole if form was cut/sliced or vice versa
                cond_food = (df["food_name"].str.lower() == canonical_food.lower())
                matched = df[cond_food]

            if not matched.empty:
                row = matched.iloc[0]
                return {
                    "food_name": canonical_food,
                    "food_domain": str(row.get("food_domain", "produce")),
                    "food_form": str(row.get("food_form", clean_form)),
                    "storage_type": str(row.get("storage_type", clean_storage)),
                    "freshness_stage": str(row.get("freshness_stage", target_stage)),
                    "remaining_shelf_life_days": int(row.get("remaining_shelf_life_days", 3)),
                    "reference_max_days": int(row.get("reference_max_days", 7)),
                    "source": "FoodFresh AI Synthetic Prototype Reference",
                    "is_synthetic": True,
                    "is_training_ground_truth": False,
                    "notes": "Synthetic prototype scenario for testing and constrained guidance."
                }
        except Exception as e:
            logger.error(f"Error reading synthetic prototype scenario: {e}")

        return None


def get_synthetic_data_service() -> SyntheticDataService:
    return SyntheticDataService.get_instance()
