"""
FoodFresh AI - USDA FoodKeeper Canonical Shelf-Life Service
Parses and indexes data/raw/foodkeeper/FoodKeeper.json to produce realistic,
science-backed shelf-life estimates based on canonical normalization,
storage conditions (Countertop vs Crisper Chill), days stored, and visible freshness signals.
"""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("foodfresh.shelf_life")

try:
    from backend.app.services.synthetic_data_service import get_synthetic_data_service
except ImportError:
    get_synthetic_data_service = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FOODKEEPER_PATH = PROJECT_ROOT / "data" / "raw" / "foodkeeper" / "FoodKeeper.json"

# Metric conversion factors to days
METRIC_TO_DAYS = {
    "days": 1.0,
    "day": 1.0,
    "weeks": 7.0,
    "week": 7.0,
    "months": 30.0,
    "month": 30.0,
    "years": 365.0,
    "year": 365.0,
    "hours": 1.0 / 24.0,
    "hour": 1.0 / 24.0,
}

# Strict Canonical Mapping Table:
# Maps detected food string variants to EXACT FoodKeeper Product IDs
# Prevents false conflations (e.g. Green Chilli vs Bell Pepper, Commercial Bread vs Wheat Bread)
CANONICAL_PRODUCE_MAPPING: Dict[str, Dict[str, Any]] = {
    # Hot Peppers / Green Chillies -> ID 548.0 ("Hot peppers")
    "green chilli": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "green chili": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "chilli": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "chili": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "chili pepper": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "hot pepper": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},
    "jalapeno": {"id": 548.0, "canonical_name": "Hot peppers", "category": "Vegetables"},

    # Chickoo / Sapodilla -> ID 265.0 (Tropical Fruits group, closest match)
    # Chickoo (chiku, sapota, sapodilla) is a tropical fruit with 3-5 day countertop life
    "chickoo": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "chiku": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "sapota": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "sapodilla": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},

    # Sweet / Bell Peppers -> ID 296.0 ("Peppers")
    "bell pepper": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},
    "pepper": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},
    "sweet pepper": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},
    "capsicum": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},
    "red pepper": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},
    "yellow pepper": {"id": 296.0, "canonical_name": "Peppers", "category": "Vegetables"},

    # Tomatoes -> ID 306.0 ("Tomatoes") / ID 600.0 ("Cherry tomatoes")
    "tomato": {"id": 306.0, "canonical_name": "Tomatoes", "category": "Vegetables"},
    "tomatoes": {"id": 306.0, "canonical_name": "Tomatoes", "category": "Vegetables"},
    "cherry tomato": {"id": 600.0, "canonical_name": "Cherry tomatoes", "category": "Vegetables"},
    "cherry tomatoes": {"id": 600.0, "canonical_name": "Cherry tomatoes", "category": "Vegetables"},

    # Potatoes -> ID 297.0 ("Potatoes") / ID 422.0 ("Yams/sweet potatoes")
    "potato": {"id": 297.0, "canonical_name": "Potatoes", "category": "Vegetables"},
    "potatoes": {"id": 297.0, "canonical_name": "Potatoes", "category": "Vegetables"},
    "sweet potato": {"id": 422.0, "canonical_name": "Yams/sweet potatoes", "category": "Vegetables"},
    "yam": {"id": 422.0, "canonical_name": "Yams/sweet potatoes", "category": "Vegetables"},

    # Apples -> ID 248.0 ("Apples")
    "apple": {"id": 248.0, "canonical_name": "Apples", "category": "Fruit"},
    "apples": {"id": 248.0, "canonical_name": "Apples", "category": "Fruit"},

    # Bananas -> ID 251.0 ("Bananas")
    "banana": {"id": 251.0, "canonical_name": "Bananas", "category": "Fruit"},
    "bananas": {"id": 251.0, "canonical_name": "Bananas", "category": "Fruit"},

    # Citrus -> ID 256.0 ("Citrus fruit")
    "orange": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},
    "oranges": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},
    "lemon": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},
    "lime": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},
    "grapefruit": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},
    "citrus": {"id": 256.0, "canonical_name": "Citrus fruit", "category": "Fruit"},

    # Grapes -> ID 261.0 ("Grapes") (Distinct from citrus/grapefruit)
    "grape": {"id": 261.0, "canonical_name": "Grapes", "category": "Fruit"},
    "grapes": {"id": 261.0, "canonical_name": "Grapes", "category": "Fruit"},

    # Cherries -> ID 483.0 ("Cherries") (Distinct from cherry tomatoes)
    "cherry": {"id": 483.0, "canonical_name": "Cherries", "category": "Fruit"},
    "cherries": {"id": 483.0, "canonical_name": "Cherries", "category": "Fruit"},

    # Avocados -> ID 250.0 ("Avocados") (Distinct from shelf-stable Avocado Oil)
    "avocado": {"id": 250.0, "canonical_name": "Avocados", "category": "Fruit"},
    "avocados": {"id": 250.0, "canonical_name": "Avocados", "category": "Fruit"},

    # Carrots -> ID 279.0 ("Carrots, parsnips") (Distinct from carrot juice)
    "carrot": {"id": 279.0, "canonical_name": "Carrots, parsnips", "category": "Vegetables"},
    "carrots": {"id": 279.0, "canonical_name": "Carrots, parsnips", "category": "Vegetables"},

    # Onions -> ID 294.0 ("Onions") (Distinct from onion powder)
    "onion": {"id": 294.0, "canonical_name": "Onions", "category": "Vegetables"},
    "onions": {"id": 294.0, "canonical_name": "Onions", "category": "Vegetables"},

    # Garlic -> ID 285.0 ("Garlic" in Produce)
    "garlic": {"id": 285.0, "canonical_name": "Garlic", "category": "Vegetables"},

    # Stone fruits & Pears -> ID 266.0
    "pear": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},
    "pears": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},
    "peach": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},
    "peaches": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},
    "plum": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},
    "plums": {"id": 266.0, "canonical_name": "Peaches, nectarines, plums, pears, sapote", "category": "Fruit"},

    # Beets / Beetroot -> ID 274.0 ("Beets")
    "beetroot": {"id": 274.0, "canonical_name": "Beets", "category": "Vegetables"},
    "beet": {"id": 274.0, "canonical_name": "Beets", "category": "Vegetables"},
    "beets": {"id": 274.0, "canonical_name": "Beets", "category": "Vegetables"},

    # Corn -> ID 282.0 ("Corn on the cob")
    "corn": {"id": 282.0, "canonical_name": "Corn on the cob", "category": "Vegetables"},
    "sweet corn": {"id": 282.0, "canonical_name": "Corn on the cob", "category": "Vegetables"},

    # Radish -> ID 299.0 ("Radishes")
    "radish": {"id": 299.0, "canonical_name": "Radishes", "category": "Vegetables"},
    "radishes": {"id": 299.0, "canonical_name": "Radishes", "category": "Vegetables"},

    # Brassicas & Greens
    "cabbage": {"id": 278.0, "canonical_name": "Cabbage", "category": "Vegetables"},
    "cauliflower": {"id": 280.0, "canonical_name": "Cauliflower", "category": "Vegetables"},
    "broccoli": {"id": 276.0, "canonical_name": "Broccoli and broccoli raab (rapini)", "category": "Vegetables"},
    "spinach": {"id": 287.0, "canonical_name": "Greens", "category": "Vegetables"},
    "lettuce": {"id": 290.0, "canonical_name": "Lettuce", "category": "Vegetables"},
    "green bean": {"id": 273.0, "canonical_name": "Beans and peas", "category": "Vegetables"},
    "green beans": {"id": 273.0, "canonical_name": "Beans and peas", "category": "Vegetables"},

    # Ginger & Guava
    "ginger": {"id": 286.0, "canonical_name": "Ginger root", "category": "Vegetables"},
    "guava": {"id": 262.0, "canonical_name": "Guava", "category": "Fruit"},

    # Melons
    "cantaloupe": {"id": 264.0, "canonical_name": "Melons", "category": "Fruit"},
    "melon": {"id": 264.0, "canonical_name": "Melons", "category": "Fruit"},
    "watermelon": {"id": 495.0, "canonical_name": "Watermelon", "category": "Fruit"},

    # Pomegranate -> ID 269.0 ("Pomegranate")
    "pomegranate": {"id": 269.0, "canonical_name": "Pomegranate", "category": "Fruit"},
    "pomegranates": {"id": 269.0, "canonical_name": "Pomegranate", "category": "Fruit"},

    # Tropical Fruits (Papaya, Mango) -> ID 265.0
    "mango": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "papaya": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "passion fruit": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},
    "passionfruit": {"id": 265.0, "canonical_name": "Papaya, mango, feijoa, passionfruit, casaha melon", "category": "Fruit"},

    # Pineapple -> ID 267.0 ("Pineapple")
    "pineapple": {"id": 267.0, "canonical_name": "Pineapple", "category": "Fruit"},

    # Cucumbers -> ID 283.0 ("Cucumbers")
    "cucumber": {"id": 283.0, "canonical_name": "Cucumbers", "category": "Vegetables"},
    "cucumbers": {"id": 283.0, "canonical_name": "Cucumbers", "category": "Vegetables"},

    # Eggplant -> ID 284.0 ("Eggplant")
    "eggplant": {"id": 284.0, "canonical_name": "Eggplant", "category": "Vegetables"},
    "aubergine": {"id": 284.0, "canonical_name": "Eggplant", "category": "Vegetables"},
    "brinjal": {"id": 284.0, "canonical_name": "Eggplant", "category": "Vegetables"},

    # Bakery / Bread -> ID 195.0 ("Commercial bread products") / ID 574.0 ("Bread")
    "bread": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "loaf": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "white bread": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "whole wheat bread": {"id": 460.0, "canonical_name": "Whole wheat bread", "category": "Bakery"},
    "bun": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "buns": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "toast": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "roti": {"id": 195.0, "canonical_name": "Commercial bread products", "category": "Bakery"},
    "cake": {"id": 197.0, "canonical_name": "Commercial cakes and muffins", "category": "Bakery"},
    "cakes": {"id": 197.0, "canonical_name": "Commercial cakes and muffins", "category": "Bakery"},
}


def _normalize_freshness_label(label: Optional[str]) -> str:
    """
    Extract the core freshness class from a potentially decorated label.
    Handles suffixes like '(Moderate Confidence)', 'Freshness Uncertain (...)', etc.
    Returns canonical lowercase string: 'rotten', 'slightly_spoiled', 'fresh', or 'uncertain'.
    """
    if not label:
        return "fresh"
    raw = str(label).lower().strip()
    # Strip parenthetical qualifiers like '(moderate confidence)', '(limited model coverage for beetroot)'
    raw = re.sub(r"\s*\([^)]*\)", "", raw).strip()
    # Map decorated labels to canonical freshness classes
    if "rotten" in raw:
        return "rotten"
    if "slightly" in raw or "spoiled" in raw:
        return "slightly_spoiled"
    if "stale" in raw or "mold" in raw:
        return "slightly_spoiled"
    if "uncertain" in raw or "unavailable" in raw:
        return "uncertain"
    if "fresh" in raw:
        return "fresh"
    return raw


class FoodKeeperService:
    """
    Canonical FoodKeeper Shelf-Life Service.
    Maps food items to USDA FoodKeeper reference records and computes
    transparent estimated remaining quality windows.
    """

    _instance: Optional["FoodKeeperService"] = None

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or FOODKEEPER_PATH
        self.categories: Dict[float, str] = {}
        self.products_by_id: Dict[float, Dict[str, Any]] = {}
        self.products_list: List[Dict[str, Any]] = []
        self.is_loaded = False
        self.load_error: Optional[str] = None

        self._load_database()

    @classmethod
    def get_instance(cls) -> "FoodKeeperService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_database(self) -> None:
        """Parse USDA FoodKeeper JSON database into memory."""
        if not self.data_path.exists():
            self.load_error = f"FoodKeeper file not found at: {self.data_path}"
            logger.error(self.load_error)
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            sheets = {s.get("name"): s.get("data", []) for s in data.get("sheets", [])}

            # 1. Parse categories
            for r in sheets.get("Category", []):
                rd = {k: v for item in r for k, v in item.items()}
                cid = rd.get("ID")
                cname = rd.get("Category_Name")
                if cid is not None and cname:
                    self.categories[float(cid)] = cname

            # 2. Parse products
            for r in sheets.get("Product", []):
                rd = {k: v for item in r for k, v in item.items()}
                pid = rd.get("ID")
                name = rd.get("Name")
                if pid is not None and name:
                    clean_name = str(name).strip()
                    rd["_clean_name"] = clean_name
                    cid = rd.get("Category_ID")
                    if cid is not None and float(cid) in self.categories:
                        rd["_category_name"] = self.categories[float(cid)]
                    else:
                        rd["_category_name"] = "General Produce"

                    self.products_by_id[float(pid)] = rd
                    self.products_list.append(rd)

            self.is_loaded = True
            logger.info(f"Loaded USDA FoodKeeper: {len(self.products_by_id)} products indexed.")

        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Error loading FoodKeeper database: {e}")
            self.is_loaded = False

    def normalize_food_name(self, query: str) -> str:
        """Clean and normalize food name string."""
        q = str(query or "").lower().strip()
        q = re.sub(r"[^\w\s]", " ", q)
        q = re.sub(r"\s+", " ", q).strip()
        return q

    def find_canonical_entry(self, food_name: str) -> Optional[Tuple[Dict[str, Any], str, str, float]]:
        """
        Match food against canonical mapping table or direct exact matches.
        Returns: (product_dict, canonical_name, match_type, match_confidence) or None.
        """
        if not self.is_loaded or not food_name:
            return None

        norm = self.normalize_food_name(food_name)

        # 1. Canonical lookup table match
        if norm in CANONICAL_PRODUCE_MAPPING:
            target = CANONICAL_PRODUCE_MAPPING[norm]
            pid = target["id"]
            if pid in self.products_by_id:
                return self.products_by_id[pid], target["canonical_name"], "canonical_match", 1.0

        # Check multi-word tokens against canonical table (e.g. "fresh green chilli" -> "green chilli")
        for k, target in CANONICAL_PRODUCE_MAPPING.items():
            if k in norm:
                pid = target["id"]
                if pid in self.products_by_id:
                    return self.products_by_id[pid], target["canonical_name"], "canonical_alias", 0.95

        # 2. Exact match against FoodKeeper clean names
        for p in self.products_list:
            p_norm = self.normalize_food_name(p["_clean_name"])
            if norm == p_norm:
                return p, p["_clean_name"], "exact_name", 0.90

        # 3. Check for ambiguous candidates
        matches = []
        for p in self.products_list:
            p_norm = self.normalize_food_name(p["_clean_name"])
            if norm in p_norm.split():
                matches.append(p)

        if len(matches) == 1:
            return matches[0], matches[0]["_clean_name"], "single_candidate", 0.80
        elif len(matches) > 1:
            # Multiple candidates exist -> ambiguous match, refuse to guess
            logger.info(f"Ambiguous FoodKeeper matches for '{food_name}': {[m['_clean_name'] for m in matches[:3]]}")
            return None

        return None

    def estimate_shelf_life(
        self,
        detected_food: Optional[str] = None,
        storage_type: str = "countertop",
        days_stored: int = 0,
        freshness_label: Optional[str] = None,
        food_form: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Convenience alias for get_shelf_life_guidance."""
        food_name = detected_food or kwargs.get("food_name")
        return self.get_shelf_life_guidance(
            food_name=food_name,
            storage_type=storage_type,
            days_stored=days_stored,
            freshness_label=freshness_label,
            food_form=food_form or kwargs.get("food_form"),
        )

    def get_shelf_life_guidance(
        self,
        food_name: Optional[str],
        storage_type: str = "countertop",
        days_stored: int = 0,
        freshness_label: Optional[str] = None,
        food_form: Optional[str] = "unknown",
    ) -> Dict[str, Any]:
        """
        Compute transparent estimated remaining quality window based on:
        1. detected food
        2. FoodKeeper canonical match
        3. storage environment (Countertop vs Crisper Chill)
        4. days stored
        5. reference duration
        6. visible freshness signal
        7. food form (fresh vs dried vs powdered — form-aware availability)
        """
        form_norm = (food_form or "unknown").lower().strip()
        if form_norm in ("dried", "powdered", "processed", "cooked"):
            return {
                "status": "unavailable",
                "food": food_name,
                "foodForm": form_norm,
                "canonicalFood": None,
                "matchType": "form_unsupported",
                "storageType": storage_type,
                "reason": (
                    "Remaining quality cannot currently be estimated for this food form. "
                    "USDA FoodKeeper references in this pipeline target fresh whole produce forms."
                ),
                "remaining": None,
                "referenceDuration": None,
                "source": "USDA FoodKeeper",
                "isEstimate": False,
            }

        if not food_name or str(food_name).strip().lower() in ["none", "null", "uncertain", ""]:
            return {
                "status": "unavailable",
                "food": food_name,
                "canonicalFood": None,
                "matchType": "none",
                "storageType": storage_type,
                "reason": "No food detected for shelf-life reference lookup.",
                "remaining": None,
                "referenceDuration": None,
                "source": "USDA FoodKeeper",
                "isEstimate": False
            }

        canonical_res = self.find_canonical_entry(food_name)
        freshness_norm = _normalize_freshness_label(freshness_label)

        if not canonical_res:
            # Fallback to auxiliary Synthetic Prototype Reference if available
            synth_scenario = None
            if get_synthetic_data_service and form_norm not in ("dried", "powdered", "processed", "cooked") and food_name.lower().strip() != "strawberry":
                try:
                    synth_svc = get_synthetic_data_service()
                    synth_scenario = synth_svc.lookup_prototype_scenario(
                        food_name=food_name,
                        food_form=form_norm,
                        storage_type=storage_type,
                        freshness_stage=freshness_label or "Fresh"
                    )
                except Exception as ex:
                    logger.warning(f"Synthetic prototype lookup failed: {ex}")

            if synth_scenario:
                days_past = max(0, int(days_stored))
                ref_max = float(synth_scenario["reference_max_days"])
                ref_min = 1.0 if ref_max > 1.0 else ref_max
                raw_rem = max(0.0, float(synth_scenario["remaining_shelf_life_days"]) - days_past)
                if freshness_norm == "fresh" and days_past == 0:
                    raw_rem = max(1.0, raw_rem)

                int_rem_min = int(round(raw_rem * 0.7))
                int_rem_max = int(round(raw_rem))

                return {
                    "status": "available",
                    "food": food_name,
                    "canonicalFood": synth_scenario["food_name"],
                    "category": synth_scenario["food_domain"].title(),
                    "matchType": "synthetic_reference",
                    "matchConfidence": 0.85,
                    "storageType": storage_type,
                    "daysStored": days_past,
                    "referenceDuration": {
                        "minDays": int(round(ref_min)),
                        "maxDays": int(round(ref_max))
                    },
                    "remaining": {
                        "minDays": int_rem_min,
                        "maxDays": int_rem_max
                    },
                    "unit": "days",
                    "source": "FoodFresh AI Synthetic Prototype Reference",
                    "tips": "Prototype scenario estimate from synthetic reference (auxiliary development data).",
                    "isEstimate": True,
                    "heuristicAdjustment": "Reference derived from synthetic prototype scenarios; not USDA laboratory measurement.",
                    "zeroDayReason": "Estimated remaining quality has reached 0 days." if int_rem_max <= 0 else None
                }

            return {
                "status": "unavailable",
                "food": food_name,
                "canonicalFood": None,
                "matchType": "unmatched",
                "storageType": storage_type,
                "reason": f"No matching FoodKeeper reference guideline found for '{food_name}'.",
                "remaining": None,
                "referenceDuration": None,
                "source": "USDA FoodKeeper",
                "isEstimate": False
            }

        product, canonical_name, match_type, match_conf = canonical_res

        # Phase 9: Storage Mapping Logic
        # UI Options:
        # - 'countertop' / 'ambient' -> FoodKeeper Pantry
        # - 'fridge' / 'crisper' / 'refrigerate' -> FoodKeeper Refrigerate
        norm_storage = storage_type.lower().strip()
        is_crisper = norm_storage in ["fridge", "crisper", "refrigerate", "refrigerator"]
        storage_label = "Crisper Chill" if is_crisper else "Countertop"

        ref_min_days, ref_max_days, tips, source_key = self._extract_duration(product, is_crisper)

        # Check if the requested storage environment has no reference duration
        if ref_min_days is None and ref_max_days is None:
            # Check if alternate storage mode has a recommendation
            alt_storage = not is_crisper
            alt_min, alt_max, alt_tips, alt_key = self._extract_duration(product, alt_storage)
            alt_label = "Crisper Chill (Refrigerated)" if alt_storage else "Countertop (Ambient)"

            if alt_min is not None or alt_max is not None:
                explanation = (
                    f"USDA FoodKeeper does not specify a {storage_label} quality window for {canonical_name}. "
                    f"Recommended storage is {alt_label} ({alt_tips or 'for optimal produce longevity'})."
                )
            else:
                explanation = f"No numerical duration guideline in USDA FoodKeeper for {canonical_name} under {storage_label} storage."

            return {
                "status": "unavailable",
                "food": food_name,
                "canonicalFood": canonical_name,
                "matchType": match_type,
                "storageType": storage_type,
                "reason": explanation,
                "referenceDuration": None,
                "remaining": None,
                "source": "USDA FoodKeeper",
                "isEstimate": False
            }

        # Normalize reference bounds
        ref_min = float(ref_min_days if ref_min_days is not None else ref_max_days)
        ref_max = float(ref_max_days if ref_max_days is not None else ref_min_days)
        if ref_min > ref_max:
            ref_min, ref_max = ref_max, ref_min

        # -------------------------------------------------------------
        # Form-Aware Capping (prevents unrealistic cut apple = 19 days)
        # -------------------------------------------------------------
        form_note = None
        source_label_form = None
        if form_norm in ("cut", "sliced", "diced"):
            if is_crisper:
                # Refrigerated cut produce: quality window is constrained to 3–5 days
                ref_min = min(ref_min, 3.0)
                ref_max = min(ref_max, 5.0)
                form_note = "Form-adjusted estimate: cut/sliced refrigerated produce has an accelerated 3–5 day window."
            else:
                # Ambient countertop cut produce: quality window is constrained to 1–2 days
                ref_min = min(ref_min, 1.0)
                ref_max = min(ref_max, 2.0)
                form_note = "Form-adjusted estimate: ambient fresh-cut produce must be used rapidly (1–2 day window)."
            source_label_form = "USDA FoodKeeper (form-adjusted)"

        # -------------------------------------------------------------
        # FoodFresh AI Prototype Constraints
        # - Produce countertop prototype policy window: up to ~7 days
        # - Produce refrigerated prototype policy window: up to ~15 days
        # -------------------------------------------------------------
        prototype_note = None
        if form_norm not in ("cut", "sliced", "diced"):
            if not is_crisper and ref_max > 7.0:
                ref_max = 7.0
                ref_min = min(ref_min, 7.0)
                prototype_note = "Constrained by FoodFresh AI countertop prototype policy (up to 7 days ambient window)."
            elif is_crisper and ref_max > 15.0:
                ref_max = 15.0
                ref_min = min(ref_min, 15.0)
                prototype_note = "Constrained by FoodFresh AI refrigerated prototype policy (up to 15 days crisper window)."

        # -------------------------------------------------------------
        # Synthetic Dataset Floor Corrections
        # Some FoodKeeper entries use DOP (Date of Purchase) which gives
        # very conservative countertop numbers. Apply a minimum floor for
        # foods where this is known to be too low, sourced from the
        # FoodFreshAI Synthetic Dataset (auxiliary reference).
        # -------------------------------------------------------------
        SYNTHETIC_FLOOR_CORRECTIONS = {
            "grape": {"countertop_min": 2.0, "countertop_max": 3.0, "fridge_min": 5.0, "fridge_max": 7.0},
            "grapes": {"countertop_min": 2.0, "countertop_max": 3.0, "fridge_min": 5.0, "fridge_max": 7.0},
            "chickoo": {"countertop_min": 3.0, "countertop_max": 5.0, "fridge_min": 7.0, "fridge_max": 10.0},
            "chiku": {"countertop_min": 3.0, "countertop_max": 5.0, "fridge_min": 7.0, "fridge_max": 10.0},
            "sapota": {"countertop_min": 3.0, "countertop_max": 5.0, "fridge_min": 7.0, "fridge_max": 10.0},
            "sapodilla": {"countertop_min": 3.0, "countertop_max": 5.0, "fridge_min": 7.0, "fridge_max": 10.0},
        }
        food_norm_for_floor = self.normalize_food_name(food_name)
        if food_norm_for_floor in SYNTHETIC_FLOOR_CORRECTIONS and form_norm not in ("cut", "sliced", "diced"):
            floors = SYNTHETIC_FLOOR_CORRECTIONS[food_norm_for_floor]
            floor_min = floors["countertop_min"] if not is_crisper else floors["fridge_min"]
            floor_max = floors["countertop_max"] if not is_crisper else floors["fridge_max"]
            if ref_max < floor_min:
                ref_min = floor_min
                ref_max = floor_max
                note = "Reference window adjusted with FoodFreshAI Synthetic Dataset floor (FoodKeeper DOP estimate too conservative)."
                prototype_note = (prototype_note + " " + note) if prototype_note else note

        # Phase 10 & 11: Calculate remaining duration and handle zero/negative days
        days_past = max(0, int(days_stored))
        raw_rem_min = ref_min - days_past
        raw_rem_max = ref_max - days_past

        # Apply conservative visible freshness signal
        adjustment_applied = False
        heuristic_note = None

        if freshness_norm == "rotten":
            rem_min = 0.0
            rem_max = 0.0
            adjustment_applied = True
            heuristic_note = "Visible signs of decomposition indicate that the quality window has expired."
        elif freshness_norm in ["slightly_spoiled", "slightly spoiled"]:
            # Conservative reduction: cut remaining quality window by 50%
            rem_min = max(0.0, raw_rem_min * 0.5)
            rem_max = max(1.0 if raw_rem_max >= 1.0 else 0.0, raw_rem_max * 0.5)
            adjustment_applied = True
            heuristic_note = "Remaining quality window reduced due to visible surface wear."
        else:
            rem_min = max(0.0, raw_rem_min)
            rem_max = max(0.0, raw_rem_max)

        # Zero-day Protection for Fresh Produce (e.g. freshly purchased whole watermelon)
        if freshness_norm == "fresh":
            if days_past == 0:
                rem_min = max(1.0, rem_min)
                rem_max = max(1.0, rem_max)
            elif days_past < ref_max:
                rem_max = max(1.0, rem_max)

        int_rem_min = int(round(rem_min))
        int_rem_max = int(round(rem_max))

        # Phase 11: Explanatory Reason for 0-day or Negative Remaining Quality Cases
        zero_day_reason = None
        if int_rem_max <= 0 or raw_rem_max <= 0:
            int_rem_min = 0
            int_rem_max = 0
            if freshness_norm == "rotten":
                zero_day_reason = "Visible deterioration indicates that this item is past its consumable quality window."
            elif days_past >= ref_max:
                zero_day_reason = (
                    f"Stored for {days_past} days, exceeding the USDA FoodKeeper reference window of "
                    f"{int(ref_min)}–{int(ref_max)} days under {storage_label} storage."
                )
            else:
                zero_day_reason = "Estimated remaining quality has reached 0 days."

        # Compile explanatory notes
        notes_list = [n for n in (heuristic_note, form_note, prototype_note) if n]
        final_heuristic_note = " ".join(notes_list) if notes_list else None

        source_label = source_label_form or (
            "USDA FoodKeeper + freshness observation" if adjustment_applied else "USDA FoodKeeper"
        )

        return {
            "status": "available",
            "food": food_name,
            "canonicalFood": canonical_name,
            "category": product.get("_category_name"),
            "matchType": match_type,
            "matchConfidence": match_conf,
            "storageType": storage_type,
            "daysStored": days_past,
            "referenceDuration": {
                "minDays": int(round(ref_min)),
                "maxDays": int(round(ref_max))
            },
            "remaining": {
                "minDays": int_rem_min,
                "maxDays": int_rem_max
            },
            "unit": "days",
            "source": source_label,
            "tips": tips,
            "isEstimate": True,
            "heuristicAdjustment": final_heuristic_note,
            "zeroDayReason": zero_day_reason
        }

    def _extract_duration(
        self,
        product: Dict[str, Any],
        is_refrigerated: bool
    ) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
        """Extract numerical duration range in days from product dictionary."""
        prefix = "Refrigerate" if is_refrigerated else "Pantry"
        candidates = [
            f"DOP_{prefix}",
            prefix,
            f"{prefix}_After_Opening"
        ]

        for cand in candidates:
            min_val = product.get(f"{cand}_Min")
            max_val = product.get(f"{cand}_Max")
            metric = product.get(f"{cand}_Metric")
            tips = product.get(f"{cand}_tips")

            if metric:
                norm_metric = str(metric).lower().strip()

                # Handle "When Ripe" entries (Bananas, Tomatoes, Pineapples)
                if norm_metric == "when ripe":
                    if tips:
                        day_match = re.search(r"then\s+(\d+)\s*(?:-|to)?\s*(\d+)?\s*days?", tips, re.IGNORECASE)
                        if day_match:
                            d1 = float(day_match.group(1))
                            d2 = float(day_match.group(2)) if day_match.group(2) else d1
                            return d1, d2, tips, cand
                        elif "7 days" in tips:
                            return 2.0, 7.0, tips, cand
                        elif "1-2 days" in tips:
                            return 1.0, 2.0, tips, cand
                    return 2.0, 5.0, tips or "Ripe produce guideline", cand

                # Unit conversion to days
                factor = METRIC_TO_DAYS.get(norm_metric)
                if factor is not None:
                    c_min = float(min_val) * factor if min_val is not None else None
                    c_max = float(max_val) * factor if max_val is not None else None
                    if c_min is not None or c_max is not None:
                        return c_min, c_max, tips, cand

        return None, None, None, None


def get_shelf_life_service() -> FoodKeeperService:
    return FoodKeeperService.get_instance()


def get_foodkeeper_service() -> FoodKeeperService:
    return FoodKeeperService.get_instance()
