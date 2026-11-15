# FoodFresh AI — Shelf-Life Machine Learning Model Evaluation Report

**Date:** November 15, 2026
**Selected Production Model:** `RandomForest`
**Model Checkpoint Path:** `D:\VIT TY SEM5\ML Project\FOODFRESHAI\models\trained\shelf_life_model.joblib`

## 1. Held-Out Test Set Model Benchmark (N=6,192)

| Model Architecture | Test MAE (days) | Test RMSE (days) | Test R² Score | Training Time (s) |
|---|---:|---:|---:|---:|
| **XGBoost** | 0.0228 | 0.0493 | 0.9996 | 0.6s |
| **RandomForest** | 0.0038 | 0.0407 | 0.9997 | 0.5s |
| **MLP** | 0.0135 | 0.0189 | 0.9999 | 2.8s |

## 2. Error Breakdown by Food Domain

| Food Domain | Test MAE (days) | Test Samples |
|---|---:|---:|
| Bakery | 0.0021 | 720 |
| Produce | 0.0041 | 5472 |

## 3. Error Breakdown by Storage Type

| Storage Type | Test MAE (days) | Test Samples |
|---|---:|---:|
| Countertop | 0.0022 | 3096 |
| Refrigerated | 0.0055 | 3096 |

## 4. Safety Guardrail Integration

The trained ML regressor provides empirical, data-driven estimates of remaining shelf-life days. To ensure absolute consumer food safety, the model is integrated into `backend/app/services/shelf_life_service.py` with USDA FoodKeeper canonical rules serving as strict upper-bound guardrails and fallback when produce is spoiled.
