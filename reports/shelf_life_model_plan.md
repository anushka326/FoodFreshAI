# Shelf-life model plan and data audit

## Findings from local annotations

The AgriFreshNET train/validation/test manifests contain 14,160 images across eight foods and three freshness stages. The source class folder names and `reports/agrifreshnet_shelf_life_summary.csv` encode one interval for each food/stage pair (24 interval classes). For example, Fresh Banana is labelled 1–4 days and Rotten Tomato 24–35 days. The labels are interval categories, not observed per-image remaining-life measurements. The class summary reports 590 images per food/stage category.

The manifests contain image path, food type, freshness label/id, original class, and a base image stem. They contain no storage type, temperature, humidity, elapsed days, harvest date, or per-image quality trajectory. The data therefore cannot support a defensible model of remaining days conditional on storage age/environment.

## Candidate formulation

- **Task:** 24-way interval classification: food identity × freshness stage.
- **Model:** EfficientNet-B0 image classifier initialized from the verified Freshness V3 candidate.
- **Input:** Image only. No absent covariates will be imputed.
- **Target:** Original annotated interval endpoints remain categorical ranges. Do not convert to midpoint regression.
- **Split:** Existing leakage-checked AgriFreshNET train/validation/test manifests.
- **Output:** Predicted annotated range and class confidence. Remaining days cannot be claimed without a validated storage-age model.
- **Limit:** Since interval targets are derived from the same food/stage taxonomy, this is a candidate interval classifier, not a measured shelf-life experiment.

The candidate training script is `ml/shelf_life/train_interval_classifier.py`. It was not run to completion because the pre-existing Freshness V3 training process was found active; parallel model training was stopped to avoid resource contention. No candidate checkpoint exists yet.

## Production relationship

The current production reference remains the USDA FoodKeeper service (`backend/app/services/shelf_life_service.py`). Keep it as a domain baseline and sanity check. Do not promote the interval candidate until its held-out interval metrics and food-wise performance are measured. Unsupported forms (including dried chilli) remain explicitly unsupported. FoodKeeper availability is not evidence that an ML estimate exists, and an ML interval candidate must not be presented as an exact remaining-day count.
