"""
FoodFresh AI - Master Hybrid Vision Pipeline
Fuses Grounding DINO (detector), SigLIP 2 (zero-shot semantic), Raw Food ResNet-50 (specialist),
and Freshness ResNet-18 into a deterministic, auditable hybrid vision result.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image

from ml.hybrid_vision.config import (
    CROP_MARGIN_RATIO,
    HIGH_CONFIDENCE_THRESHOLD,
    MIN_VALID_CONFIDENCE,
    MODERATE_CONFIDENCE_THRESHOLD,
    UNCERTAINTY_TOP_GAP,
)
from ml.hybrid_vision.freshness_service import get_freshness_service
from ml.hybrid_vision.grounding_dino_service import get_grounding_dino_service
from ml.hybrid_vision.preprocessing import crop_bounding_box, load_image_rgb
from ml.hybrid_vision.raw_food_service import get_raw_food_service
from ml.hybrid_vision.schemas import (
    EatFirstPriorityResult,
    FoodRecognitionSources,
    FreshnessResult,
    HybridVisionResult,
    ModelVersions,
    PredictionCandidate,
    ReferenceDuration,
    RemainingDuration,
    ShelfLifeResult,
)
from ml.hybrid_vision.siglip2_service import get_siglip2_service
from ml.hybrid_vision.utils import display_name, find_agreement_candidate, labels_match, normalize_food_name
from backend.app.services.shelf_life_service import get_shelf_life_service
from backend.app.services.eat_first_service import get_eat_first_service
from backend.app.services.food_form_service import infer_food_form

logger = logging.getLogger("foodfresh.hybrid.pipeline")


class HybridVisionPipeline:
    """
    Master pipeline orchestrating:
      1. Open-vocabulary object detection (Grounding DINO)
      2. Food region selection & bounding box cropping
      3. Specialist raw food classification (ResNet-50)
      4. Open-vocabulary zero-shot classification (SigLIP 2)
      5. Cross-evidence deterministic fusion and uncertainty gate
      6. Visible freshness estimation (ResNet-18)
      7. Shelf-life estimation (USDA FoodKeeper)
      8. Eat First priority ranking (deterministic rule engine)
    """

    _instance: Optional["HybridVisionPipeline"] = None

    def __init__(self):
        logger.info("Initializing HybridVisionPipeline singleton...")
        self.detector = get_grounding_dino_service()
        self.raw_food = get_raw_food_service()
        self.siglip2 = get_siglip2_service()
        self.freshness_service = get_freshness_service()
        self.shelf_life_service = get_shelf_life_service()
        self.eat_first_service = get_eat_first_service()
        logger.info("HybridVisionPipeline initialized.")

    @classmethod
    def get_instance(cls) -> "HybridVisionPipeline":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def analyze(
        self,
        image_input: Union[bytes, str, Image.Image],
        top_k: int = 5,
        storage_type: str = "countertop",
        days_stored: int = 0
    ) -> HybridVisionResult:
        """
        Execute full end-to-end hybrid analysis on an input image.
        """
        pipeline_start = time.perf_counter()
        latencies: Dict[str, float] = {}

        try:
            image = load_image_rgb(image_input)
        except Exception as e:
            logger.error(f"Image loading error: {e}")
            return HybridVisionResult(
                success=False,
                analysisStatus="error",
                message=f"Failed to decode image: {e}"
            )

        # ----------------------------------------------------
        # Step 1 & 2: Object Detection (Grounding DINO)
        # ----------------------------------------------------
        dino_res = self.detector.detect(image)
        latencies["grounding_dino_ms"] = dino_res.latency_ms

        # Select primary food region or use full image if no distinct box found
        analysis_image = image
        primary_box = None
        if dino_res.food_objects:
            primary_obj = dino_res.food_objects[0]
            primary_box = primary_obj.box
            analysis_image = crop_bounding_box(image, primary_box, margin_ratio=CROP_MARGIN_RATIO)
            logger.info(f"Cropped primary food region: {primary_obj.label} ({primary_obj.confidence}%)")
        elif dino_res.detected_objects:
            all_non_food = all(not o.is_food for o in dino_res.detected_objects)
            if all_non_food and len(dino_res.detected_objects) > 0:
                logger.info("Only non-food objects detected by Grounding DINO.")

        # ----------------------------------------------------
        # Step 3: Raw Food ResNet-50 Specialist Classification
        # ----------------------------------------------------
        raw_res = self.raw_food.classify(analysis_image, top_k=top_k)
        latencies["raw_food_resnet_ms"] = raw_res.latency_ms

        # ----------------------------------------------------
        # Step 4: SigLIP 2 Zero-Shot Semantic Classification
        # ----------------------------------------------------
        siglip_res = self.siglip2.classify(analysis_image, top_k=top_k)
        latencies["siglip2_ms"] = siglip_res.latency_ms

        # ----------------------------------------------------
        # Step 5: Deterministic Decision Fusion & Uncertainty Gate
        # ----------------------------------------------------
        fusion_status, final_food, final_conf, top_candidates, decision_reason = self._fuse_predictions(
            dino_res=dino_res,
            raw_res=raw_res,
            siglip_res=siglip_res
        )

        # ----------------------------------------------------
        # Step 6: Visible Freshness Estimation
        # ----------------------------------------------------
        freshness_res = self.freshness_service.predict(analysis_image)
        latencies["freshness_ms"] = freshness_res.latency_ms

        # ----------------------------------------------------
        # Step 7: Grounding DINO Scene Objects
        # ----------------------------------------------------
        # Filter scene objects: exclude items duplicating the detected food, sort by confidence, take up to 5
        scene_objs = []
        for obj in dino_res.scene_objects:
            if final_food and labels_match(obj.label, final_food):
                continue
            scene_objs.append(obj)
        scene_objs = scene_objs[:5]

        # ----------------------------------------------------
        # Step 8: Shelf-Life Estimation (USDA FoodKeeper)
        # ----------------------------------------------------
        if fusion_status == "success" and final_food:
            food_form = infer_food_form(final_food, freshness_label=freshness_res.label)
            shelf_dict = self.shelf_life_service.estimate_shelf_life(
                detected_food=final_food,
                storage_type=storage_type,
                days_stored=days_stored,
                freshness_label=freshness_res.label,
                food_form=food_form,
            )

            ref_dur = None
            if shelf_dict.get("referenceDuration"):
                ref_dur = ReferenceDuration(
                    minDays=shelf_dict["referenceDuration"].get("minDays"),
                    maxDays=shelf_dict["referenceDuration"].get("maxDays")
                )
            rem_dur = None
            if shelf_dict.get("remaining"):
                rem_dur = RemainingDuration(
                    minDays=shelf_dict["remaining"].get("minDays"),
                    maxDays=shelf_dict["remaining"].get("maxDays")
                )

            shelf_life_res = ShelfLifeResult(
                status=shelf_dict.get("status", "unavailable"),
                food=shelf_dict.get("food", final_food),
                storageType=shelf_dict.get("storageType", storage_type),
                daysStored=shelf_dict.get("daysStored", days_stored),
                referenceDuration=ref_dur,
                remaining=rem_dur,
                unit=shelf_dict.get("unit", "days"),
                source=shelf_dict.get("source", "USDA FoodKeeper"),
                isEstimate=shelf_dict.get("isEstimate", True),
                heuristicApplied=shelf_dict.get("heuristicApplied", False),
                reason=shelf_dict.get("reason"),
                tips=shelf_dict.get("tips")
            )

            # ----------------------------------------------------
            # Step 9: Eat First Priority (Deterministic Rules)
            # ----------------------------------------------------
            eat_dict = self.eat_first_service.calculate_priority(
                shelf_life_result=shelf_dict,
                freshness_label=freshness_res.label,
                days_stored=days_stored,
                storage_type=storage_type
            )
            eat_first_res = EatFirstPriorityResult(
                status=eat_dict.get("status", "unavailable"),
                priority=eat_dict.get("priority"),
                score=eat_dict.get("score"),
                urgencyLabel=eat_dict.get("urgencyLabel"),
                reason=eat_dict.get("reason")
            )
        else:
            shelf_life_res = ShelfLifeResult(
                status="unavailable",
                reason="Food was not identified with sufficient certainty for FoodKeeper reference lookup."
            )
            eat_first_res = EatFirstPriorityResult(
                status="unavailable",
                reason="Eat First requires an available shelf-life estimate."
            )

        total_latency = round((time.perf_counter() - pipeline_start) * 1000.0, 2)
        latencies["total_pipeline_ms"] = total_latency

        return HybridVisionResult(
            success=True,
            analysisStatus=fusion_status,
            detectedFood=final_food,
            recognitionConfidence=final_conf,
            topPredictions=top_candidates,
            detectedObjects=scene_objs,
            foodRecognition=FoodRecognitionSources(
                groundingDino={
                    "status": dino_res.status,
                    "objects": [o.model_dump() for o in dino_res.detected_objects],
                    "sceneObjects": [o.model_dump() for o in scene_objs],
                    "foodObjectsCount": len(dino_res.food_objects),
                    "latencyMs": dino_res.latency_ms
                },
                rawFoodResNet={
                    "status": raw_res.status,
                    "topPredictions": [p.model_dump() for p in raw_res.top_predictions],
                    "latencyMs": raw_res.latency_ms
                },
                siglip2={
                    "status": siglip_res.status,
                    "topPredictions": [p.model_dump() for p in siglip_res.top_predictions],
                    "latencyMs": siglip_res.latency_ms
                }
            ),
            freshness=freshness_res,
            shelfLife=shelf_life_res,
            eatFirstPriority=eat_first_res,
            modelVersions=ModelVersions(freshness=freshness_res.modelVersion),
            latencyMs=latencies,
            message=decision_reason
        )


    def _fuse_predictions(
        self,
        dino_res,
        raw_res,
        siglip_res
    ) -> Tuple[str, Optional[str], Optional[float], List[PredictionCandidate], str]:
        """
        Deterministic, transparent fusion rules:
        Rule 1: Direct Agreement (Raw Food top-1 matches SigLIP 2 top-1)
        Rule 2: Cross-model top candidate support (top-1 in one matches top-3 in the other)
        Rule 3: Detector-supported classification
        Rule 4: Contradictory evidence -> analysisStatus = 'uncertain'
        Rule 5: Low confidence (< 30%) -> analysisStatus = 'uncertain'
        """
        raw_preds = raw_res.top_predictions
        sig_preds = siglip_res.top_predictions

        if not raw_preds and not sig_preds:
            return "uncertain", None, None, [], "No classifier predictions available."

        # Case A: Both classifiers returned predictions
        if raw_preds and sig_preds:
            top_raw = raw_preds[0]
            top_sig = sig_preds[0]

            # Rule 1: Direct top-1 agreement
            if labels_match(top_raw.label, top_sig.label):
                fused_label = display_name(top_raw.label)
                # Harmonic average of confidence
                fused_conf = round((top_raw.confidence + top_sig.confidence) / 2.0, 2)
                merged = self._merge_ranked_candidates(raw_preds, sig_preds, agreed_label=fused_label)
                return "success", fused_label, fused_conf, merged, f"Full consensus: Raw Food and SigLIP 2 both identify {fused_label}."

            # Rule 2A: Specialist (Raw Food) is high confidence, SigLIP 2 supports it in top-3
            for sp in sig_preds[:3]:
                if labels_match(top_raw.label, sp.label):
                    if top_raw.confidence >= MODERATE_CONFIDENCE_THRESHOLD:
                        fused_label = display_name(top_raw.label)
                        fused_conf = round((top_raw.confidence * 0.6) + (sp.confidence * 0.4), 2)
                        merged = self._merge_ranked_candidates(raw_preds, sig_preds, agreed_label=fused_label)
                        return "success", fused_label, fused_conf, merged, f"Specialist Raw Food prediction ({top_raw.label}) supported by SigLIP 2."

            # Rule 2B: SigLIP 2 is high confidence, Raw Food supports it in top-3
            for rp in raw_preds[:3]:
                if labels_match(top_sig.label, rp.label):
                    if top_sig.confidence >= MODERATE_CONFIDENCE_THRESHOLD:
                        fused_label = display_name(top_sig.label)
                        fused_conf = round((top_sig.confidence * 0.6) + (rp.confidence * 0.4), 2)
                        merged = self._merge_ranked_candidates(sig_preds, raw_preds, agreed_label=fused_label)
                        return "success", fused_label, fused_conf, merged, f"SigLIP 2 semantic prediction ({top_sig.label}) supported by Raw Food specialist."

            # Rule 3: Grounding DINO detector support
            if dino_res.food_objects:
                for d_obj in dino_res.food_objects[:2]:
                    if labels_match(d_obj.label, top_raw.label):
                        fused_label = display_name(top_raw.label)
                        fused_conf = round((top_raw.confidence * 0.7) + (d_obj.confidence * 0.3), 2)
                        merged = self._merge_ranked_candidates(raw_preds, sig_preds, agreed_label=fused_label)
                        return "success", fused_label, fused_conf, merged, f"Detector and Raw Food specialist agree on {fused_label}."
                    if labels_match(d_obj.label, top_sig.label):
                        fused_label = display_name(top_sig.label)
                        fused_conf = round((top_sig.confidence * 0.7) + (d_obj.confidence * 0.3), 2)
                        merged = self._merge_ranked_candidates(sig_preds, raw_preds, agreed_label=fused_label)
                        return "success", fused_label, fused_conf, merged, f"Detector and SigLIP 2 agree on {fused_label}."

            # Rule 4: Contradictory Evidence -> Do NOT force a fake prediction
            merged = self._merge_ranked_candidates(raw_preds, sig_preds)
            reason = (
                f"Conflicting model evidence: Raw Food predicts {top_raw.label} ({top_raw.confidence}%), "
                f"while SigLIP 2 predicts {top_sig.label} ({top_sig.confidence}%). Marking as uncertain."
            )
            return "uncertain", None, None, merged, reason

        # Fallback if only one model produced results
        available_preds = raw_preds or sig_preds
        if available_preds and available_preds[0].confidence >= HIGH_CONFIDENCE_THRESHOLD:
            top_p = available_preds[0]
            return "success", display_name(top_p.label), top_p.confidence, available_preds, "Single model high-confidence prediction."

        return "uncertain", None, None, available_preds, "Insufficient model confidence. Marking as uncertain."

    def _merge_ranked_candidates(
        self,
        list_a: List[PredictionCandidate],
        list_b: List[PredictionCandidate],
        agreed_label: Optional[str] = None
    ) -> List[PredictionCandidate]:
        """Combine and deduplicate candidate predictions preserving highest confidence."""
        seen: Dict[str, PredictionCandidate] = {}

        for item in list_a + list_b:
            norm = normalize_food_name(item.label)
            if norm not in seen or item.confidence > seen[norm].confidence:
                seen[norm] = PredictionCandidate(
                    label=display_name(item.label),
                    confidence=item.confidence,
                    category=item.category
                )

        ranked = sorted(seen.values(), key=lambda x: x.confidence, reverse=True)

        # If an agreed label is known, make sure it is at the front
        if agreed_label:
            norm_agreed = normalize_food_name(agreed_label)
            front = [c for c in ranked if normalize_food_name(c.label) == norm_agreed]
            rest = [c for c in ranked if normalize_food_name(c.label) != norm_agreed]
            ranked = front + rest

        return ranked[:5]


def get_hybrid_vision_pipeline() -> HybridVisionPipeline:
    return HybridVisionPipeline.get_instance()
