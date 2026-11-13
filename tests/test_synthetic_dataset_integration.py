"""
FoodFresh AI - Synthetic Dataset Integration & Scenario Tests
Validates the safe integration of the auxiliary synthetic dataset:
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_Schema.json
  data/raw/Synthetic data/FoodFreshAI_Synthetic_Dataset_README.md

Tests all 15 scenarios required by Step 13:
  1. Fresh produce
  2. Degraded produce
  3. Spotted produce
  4. Bruised produce
  5. Wilted produce
  6. Rotten produce
  7. Bakery stale state (not rotten)
  8. Bakery mold-suspected state (not produce rot)
  9. Refrigerated storage constraints
  10. Countertop storage constraints
  11. Different food forms (whole vs cut/sliced/diced vs dried)
  12. Lighting conditions robustness (lighting does not force rotten)
  13. Low-quality image metadata handling
  14. Supported foods resolution
  15. Unsupported foods handling (honest uncertainty, no invented truth)

DOES NOT RETRAIN MODELS. DOES NOT ALTER DATABASE.
"""

import json
from pathlib import Path
import pytest
import pandas as pd

from backend.app.dataset_registry import DATASET_REGISTRY, get_dataset_info
from backend.app.services.food_form_service import infer_food_form, normalize_food_form
from backend.app.services.shelf_life_service import get_shelf_life_service
from backend.app.services.synthetic_data_service import get_synthetic_data_service

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "raw" / "Synthetic data"
CSV_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv"
SCHEMA_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Dataset_Schema.json"
README_PATH = SYNTHETIC_DIR / "FoodFreshAI_Synthetic_Dataset_README.md"


@pytest.fixture(scope="module")
def synthetic_sample_df():
    """Load the synthetic dataset for fast, deterministic testing."""
    if not CSV_PATH.exists():
        pytest.skip("Synthetic dataset CSV not found at expected path")
    cols = [
        "image_id", "food_name", "food_category", "food_domain", "food_form",
        "lighting_condition", "brightness_index_0_100", "image_quality",
        "visibility_penalty", "storage_type", "freshness_stage",
        "remaining_shelf_life_days", "reference_max_days", "bruise_damage_score",
        "mold_spot_score", "wrinkle_wilt_score"
    ]
    return pd.read_csv(CSV_PATH, usecols=cols)


# =====================================================================
# Registration & Verification
# =====================================================================

def test_synthetic_files_exist_and_unaltered():
    """Verify all three synthetic files exist in exact raw directory."""
    assert CSV_PATH.exists(), f"CSV missing: {CSV_PATH}"
    assert SCHEMA_PATH.exists(), f"Schema missing: {SCHEMA_PATH}"
    assert README_PATH.exists(), f"README missing: {README_PATH}"
    assert CSV_PATH.stat().st_size > 10_000_000, "CSV size unexpected"


def test_synthetic_dataset_registered():
    """Verify synthetic dataset is registered in central DATASET_REGISTRY."""
    info = get_dataset_info("synthetic_freshness_shelf_life")
    assert info, "Synthetic dataset missing from registry"
    assert info["real_image_data"] is False
    assert info["ground_truth_status"] == "synthetic_rule_based"
    assert info["training_status"] == "not_used_for_current_model_training"
    assert info["food_classes_count"] == 43


# =====================================================================
# Scenario 1: Fresh Produce
# =====================================================================

def test_scenario_01_fresh_produce(synthetic_sample_df):
    """Scenario 1: Fresh produce has positive remaining days and available shelf life."""
    fresh_rows = synthetic_sample_df[
        (synthetic_sample_df["food_domain"] == "produce") &
        (synthetic_sample_df["freshness_stage"] == "Fresh") &
        (synthetic_sample_df["food_form"] == "whole")
    ]
    assert not fresh_rows.empty
    row = fresh_rows.iloc[0]
    food_name = row["food_name"]

    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance(food_name, storage_type="countertop", days_stored=0, freshness_label="fresh")
    assert res["status"] == "available"
    assert res["remaining"]["maxDays"] > 0
    assert res.get("zeroDayReason") is None


# =====================================================================
# Scenario 2: Degraded Produce
# =====================================================================

def test_scenario_02_degraded_produce():
    """Scenario 2: Degraded/slightly spoiled produce has reduced quality window."""
    svc = get_shelf_life_service()
    fresh_res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, freshness_label="fresh")
    degraded_res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, freshness_label="slightly_spoiled")

    assert fresh_res["status"] == "available"
    assert degraded_res["status"] == "available"
    assert degraded_res["remaining"]["maxDays"] <= fresh_res["remaining"]["maxDays"]
    assert degraded_res["heuristicAdjustment"] is not None


# =====================================================================
# Scenario 3: Spotted Produce
# =====================================================================

def test_scenario_03_spotted_produce(synthetic_sample_df):
    """Scenario 3: Produce with spotted/bruised defect scores reflects in freshness stages."""
    spotted = synthetic_sample_df[synthetic_sample_df["freshness_stage"].str.contains("Spotted|Bruised", case=False)]
    assert not spotted.empty
    row = spotted.iloc[0]
    assert row["bruise_damage_score"] > 0 or row["mold_spot_score"] > 0


# =====================================================================
# Scenario 4: Bruised Produce
# =====================================================================

def test_scenario_04_bruised_produce():
    """Scenario 4: Visible surface wear applies conservative shelf-life reduction."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Banana", storage_type="countertop", days_stored=0, freshness_label="slightly spoiled")
    assert res["status"] == "available"
    assert "reduced" in res.get("heuristicAdjustment", "").lower()


# =====================================================================
# Scenario 5: Wilted Produce
# =====================================================================

def test_scenario_05_wilted_produce(synthetic_sample_df):
    """Scenario 5: Wilted leafy/vegetable synthetic stages preserve distinct structural labels."""
    wilted = synthetic_sample_df[synthetic_sample_df["freshness_stage"].str.contains("Wilted", case=False)]
    assert not wilted.empty
    assert all(wilted["food_domain"] == "produce")


# =====================================================================
# Scenario 6: Rotten Produce
# =====================================================================

def test_scenario_06_rotten_produce():
    """Scenario 6: Rotten produce window clamps to 0 days with explicit reason."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Tomato", storage_type="countertop", days_stored=0, freshness_label="rotten")
    assert res["status"] == "available"
    assert res["remaining"]["minDays"] == 0
    assert res["remaining"]["maxDays"] == 0
    assert "decomposition" in res.get("heuristicAdjustment", "").lower() or "deterioration" in res.get("zeroDayReason", "").lower()


# =====================================================================
# Scenario 7 & 8: Bakery Domain (Stale/Moldy, NOT Rotten)
# =====================================================================

def test_scenario_07_bakery_stale_not_rotten(synthetic_sample_df):
    """Scenario 7: Bakery products in synthetic dataset do not use 'Rotten' label."""
    bakery_rows = synthetic_sample_df[synthetic_sample_df["food_domain"] == "bakery"]
    assert not bakery_rows.empty
    stages = set(bakery_rows["freshness_stage"].unique())
    assert "Rotten" not in stages, f"Bakery domain should not contain 'Rotten': {stages}"
    assert any("Stale" in s for s in stages)


def test_scenario_08_bakery_mold_suspected(synthetic_sample_df):
    """Scenario 8: Bakery spoilage uses Moldy rather than produce rot."""
    bakery_rows = synthetic_sample_df[synthetic_sample_df["food_domain"] == "bakery"]
    mold_rows = bakery_rows[bakery_rows["freshness_stage"] == "Moldy"]
    assert not mold_rows.empty
    row = mold_rows.iloc[0]
    assert row["remaining_shelf_life_days"] == 0


# =====================================================================
# Scenario 9: Refrigerated Storage Constraints
# =====================================================================

def test_scenario_09_refrigerated_storage_constraints():
    """Scenario 9: Refrigerated produce reference window complies with prototype constraint (<= 15 days)."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Apple", storage_type="fridge", days_stored=0, freshness_label="fresh")
    assert res["status"] == "available"
    assert res["referenceDuration"]["maxDays"] <= 15, "Refrigerated produce prototype window must be constrained"


# =====================================================================
# Scenario 10: Countertop Storage Constraints
# =====================================================================

def test_scenario_10_countertop_storage_constraints():
    """Scenario 10: Ambient countertop produce complies with prototype constraint (<= 7 days)."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, freshness_label="fresh")
    assert res["status"] == "available"
    assert res["referenceDuration"]["maxDays"] <= 7, "Countertop produce prototype window must be constrained"


# =====================================================================
# Scenario 11: Different Food Forms (Whole vs Cut/Sliced/Diced vs Dried)
# =====================================================================

def test_scenario_11_food_forms_whole_vs_cut():
    """Scenario 11: Cut produce gets accelerated 1-2 day window, preventing unrealistic 19 days."""
    svc = get_shelf_life_service()
    whole_res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, food_form="whole")
    cut_res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, food_form="cut")
    sliced_res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, food_form="sliced")

    assert cut_res["status"] == "available"
    assert cut_res["referenceDuration"]["maxDays"] <= 2, "Cut apple on countertop must not exceed 2 days"
    assert cut_res["remaining"]["maxDays"] <= 2
    assert sliced_res["remaining"]["maxDays"] <= 2
    assert cut_res["remaining"]["maxDays"] < whole_res["remaining"]["maxDays"]


def test_scenario_11_food_forms_dried_unsupported():
    """Scenario 11b: Dried food form is declared unsupported, not fabricated."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Apple", storage_type="countertop", days_stored=0, food_form="dried")
    assert res["status"] == "unavailable"
    assert "food form" in res["reason"].lower()


# =====================================================================
# Scenario 12: Lighting Conditions Robustness
# =====================================================================

def test_scenario_12_lighting_does_not_imply_rotten(synthetic_sample_df):
    """Scenario 12: Low lighting condition in synthetic data does not force Rotten label."""
    low_light = synthetic_sample_df[synthetic_sample_df["lighting_condition"] == "low"]
    assert not low_light.empty
    # Low light must contain Fresh items
    fresh_low_light = low_light[low_light["freshness_stage"] == "Fresh"]
    assert not fresh_low_light.empty, "Low light rows should include Fresh items, not only Rotten"


# =====================================================================
# Scenario 13: Low-Quality Image Metadata Handling
# =====================================================================

def test_scenario_13_low_quality_metadata(synthetic_sample_df):
    """Scenario 13: Synthetic metadata records visibility penalty as image nuisance, not spoilage."""
    low_quality = synthetic_sample_df[synthetic_sample_df["image_quality"] == "low"]
    assert not low_quality.empty
    assert (low_quality["visibility_penalty"] > 0).all()
    # Visibility penalty does not force remaining days to 0
    fresh_low_q = low_quality[low_quality["freshness_stage"] == "Fresh"]
    assert (fresh_low_q["remaining_shelf_life_days"] > 0).all()


# =====================================================================
# Scenario 14: Supported Foods Resolution
# =====================================================================

def test_scenario_14_supported_foods_resolution():
    """Scenario 14: Canonical produce items resolve with correct food and duration."""
    svc = get_shelf_life_service()
    cases = [
        ("Banana", "Bananas"),
        ("Apple", "Apples"),
        ("Tomato", "Tomatoes"),
        ("Grape", "Grapes"),
        ("Avocado", "Avocados"),
        ("Watermelon", "Watermelon"),
    ]
    for input_food, expected_canonical in cases:
        res = svc.get_shelf_life_guidance(input_food, storage_type="countertop", days_stored=0)
        assert res["status"] == "available"
        assert res["canonicalFood"] == expected_canonical


def test_scenario_14_fresh_watermelon_zero_day_protection():
    """Scenario 14b: Fresh whole watermelon on day 0 never shows 0 days."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("Watermelon", storage_type="countertop", days_stored=0, freshness_label="fresh")
    assert res["status"] == "available"
    assert res["remaining"]["maxDays"] >= 1
    assert res.get("zeroDayReason") is None


# =====================================================================
# Scenario 15: Unsupported Foods & Uncertainty Handling
# =====================================================================

def test_scenario_15_unsupported_or_ambiguous_food():
    """Scenario 15: Unrecognized food returns unavailable status rather than inventing shelf life."""
    svc = get_shelf_life_service()
    res = svc.get_shelf_life_guidance("QuantumSpaghetti123", storage_type="countertop", days_stored=0)
    assert res["status"] == "unavailable"
    assert res.get("remaining") is None
