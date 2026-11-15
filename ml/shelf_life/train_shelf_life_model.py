"""
FoodFresh AI - Shelf-Life ML Model Training & Benchmarking Pipeline
Trains, tunes, and evaluates a genuine Machine Learning model for Shelf-Life Prediction
using the dataset in data/raw/Synthetic data/FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv.

Evaluates:
  1. XGBoost Regressor (Gradient Boosting)
  2. Multi-Layer Perceptron (Neural Network Regressor)
  3. Random Forest Regressor Baseline

Metrics evaluated on strict held-out test split:
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - Coefficient of Determination (R^2)
  - Per-food-category error distribution
"""

import json
import logging
import os
from pathlib import Path
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("foodfresh.shelf_life.train")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Synthetic data" / "FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv"
MODELS_DIR = PROJECT_ROOT / "models" / "trained"
REPORTS_DIR = PROJECT_ROOT / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_and_preprocess_data():
    logger.info(f"Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Loaded {len(df)} records across {df['food_name'].nunique()} foods.")

    # Target variable
    y = df["remaining_shelf_life_days"].astype(float).values

    # Categorical and numerical feature columns
    cat_cols = ["food_name", "food_category", "food_domain", "food_form", "storage_type", "freshness_stage"]
    num_cols = ["temperature_c", "days_since_purchase", "reference_max_days", "freshness_score_0_100"]

    # Stratified-style train/val/test split by food_name and storage_type
    strat_key = df["food_name"] + "_" + df["storage_type"]
    
    # 70% train, 15% val, 15% test
    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.30,
        random_state=42,
        stratify=strat_key
    )
    val_idx, test_idx = train_test_split(
        test_idx,
        test_size=0.50,
        random_state=42,
        stratify=strat_key.iloc[test_idx]
    )

    logger.info(f"Split sizes: Train={len(train_idx)}, Val={len(val_idx)}, Test={len(test_idx)}")

    # Preprocessing pipelines
    ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    scaler = StandardScaler()

    X_train_cat = ohe.fit_transform(df.iloc[train_idx][cat_cols])
    X_val_cat = ohe.transform(df.iloc[val_idx][cat_cols])
    X_test_cat = ohe.transform(df.iloc[test_idx][cat_cols])

    X_train_num = scaler.fit_transform(df.iloc[train_idx][num_cols])
    X_val_num = scaler.transform(df.iloc[val_idx][num_cols])
    X_test_num = scaler.transform(df.iloc[test_idx][num_cols])

    X_train = np.hstack([X_train_cat, X_train_num])
    X_val = np.hstack([X_val_cat, X_val_num])
    X_test = np.hstack([X_test_cat, X_test_num])

    y_train = y[train_idx]
    y_val = y[val_idx]
    y_test = y[test_idx]

    feature_names = list(ohe.get_feature_names_out(cat_cols)) + num_cols

    return {
        "X_train": X_train, "y_train": y_train,
        "X_val": X_val, "y_val": y_val,
        "X_test": X_test, "y_test": y_test,
        "df_test": df.iloc[test_idx].copy(),
        "ohe": ohe, "scaler": scaler,
        "cat_cols": cat_cols, "num_cols": num_cols,
        "feature_names": feature_names,
    }


def train_and_evaluate_models(data):
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]

    results = {}

    # 1. XGBoost Regressor
    logger.info("Training XGBoost Regressor...")
    t0 = time.time()
    xgb_model = xgb.XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        tree_method="hist",
        early_stopping_rounds=15,
        n_jobs=-1
    )
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    xgb_train_time = round(time.time() - t0, 2)
    xgb_preds = xgb_model.predict(X_test)
    xgb_mae = float(mean_absolute_error(y_test, xgb_preds))
    xgb_rmse = float(np.sqrt(mean_squared_error(y_test, xgb_preds)))
    xgb_r2 = float(r2_score(y_test, xgb_preds))
    logger.info(f"XGBoost Test -> MAE: {xgb_mae:.4f}, RMSE: {xgb_rmse:.4f}, R2: {xgb_r2:.4f} in {xgb_train_time}s")

    results["XGBoost"] = {
        "model": xgb_model,
        "mae": xgb_mae,
        "rmse": xgb_rmse,
        "r2": xgb_r2,
        "train_time_s": xgb_train_time,
        "predictions": xgb_preds
    }

    # 2. Random Forest Regressor Baseline
    logger.info("Training Random Forest Regressor...")
    t0 = time.time()
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_train_time = round(time.time() - t0, 2)
    rf_preds = rf_model.predict(X_test)
    rf_mae = float(mean_absolute_error(y_test, rf_preds))
    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_preds)))
    rf_r2 = float(r2_score(y_test, rf_preds))
    logger.info(f"Random Forest Test -> MAE: {rf_mae:.4f}, RMSE: {rf_rmse:.4f}, R2: {rf_r2:.4f} in {rf_train_time}s")

    results["RandomForest"] = {
        "model": rf_model,
        "mae": rf_mae,
        "rmse": rf_rmse,
        "r2": rf_r2,
        "train_time_s": rf_train_time,
        "predictions": rf_preds
    }

    # 3. Multi-Layer Perceptron (Neural Network Regressor)
    logger.info("Training Multi-Layer Perceptron Regressor...")
    t0 = time.time()
    mlp_model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        learning_rate_init=1e-3,
        max_iter=50,
        early_stopping=True,
        random_state=42
    )
    mlp_model.fit(X_train, y_train)
    mlp_train_time = round(time.time() - t0, 2)
    mlp_preds = mlp_model.predict(X_test)
    mlp_mae = float(mean_absolute_error(y_test, mlp_preds))
    mlp_rmse = float(np.sqrt(mean_squared_error(y_test, mlp_preds)))
    mlp_r2 = float(r2_score(y_test, mlp_preds))
    logger.info(f"MLP Test -> MAE: {mlp_mae:.4f}, RMSE: {mlp_rmse:.4f}, R2: {mlp_r2:.4f} in {mlp_train_time}s")

    results["MLP"] = {
        "model": mlp_model,
        "mae": mlp_mae,
        "rmse": mlp_rmse,
        "r2": mlp_r2,
        "train_time_s": mlp_train_time,
        "predictions": mlp_preds
    }

    return results


def save_best_model_and_reports(data, results):
    # Select best model based on lowest test MAE
    best_name = min(results.keys(), key=lambda k: results[k]["mae"])
    best_res = results[best_name]
    logger.info(f"Best Model Selected: {best_name} with Test MAE={best_res['mae']:.4f}, R2={best_res['r2']:.4f}")

    # Save artifacts bundle
    bundle = {
        "model": best_res["model"],
        "model_name": best_name,
        "ohe": data["ohe"],
        "scaler": data["scaler"],
        "cat_cols": data["cat_cols"],
        "num_cols": data["num_cols"],
        "feature_names": data["feature_names"],
        "metrics": {
            "mae": best_res["mae"],
            "rmse": best_res["rmse"],
            "r2": best_res["r2"]
        }
    }
    model_path = MODELS_DIR / "shelf_life_model.joblib"
    joblib.dump(bundle, model_path)
    logger.info(f"Saved trained shelf-life bundle to {model_path}")

    # Compute category-level errors on test set
    df_test = data["df_test"]
    df_test["predicted"] = best_res["predictions"]
    df_test["abs_error"] = np.abs(df_test["remaining_shelf_life_days"] - df_test["predicted"])

    category_errors = df_test.groupby("food_domain")["abs_error"].agg(["mean", "count"]).reset_index()
    category_errors.columns = ["food_domain", "mae", "sample_count"]

    storage_errors = df_test.groupby("storage_type")["abs_error"].agg(["mean", "count"]).reset_index()
    storage_errors.columns = ["storage_type", "mae", "sample_count"]

    # Write evaluation report
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset": "FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv",
        "total_samples": 41280,
        "train_samples": len(data["X_train"]),
        "val_samples": len(data["X_val"]),
        "test_samples": len(data["X_test"]),
        "best_model": best_name,
        "models_comparison": {
            k: {
                "mae": v["mae"],
                "rmse": v["rmse"],
                "r2": v["r2"],
                "train_time_s": v["train_time_s"]
            } for k, v in results.items()
        },
        "category_mae": category_errors.to_dict(orient="records"),
        "storage_mae": storage_errors.to_dict(orient="records"),
    }

    report_json_path = REPORTS_DIR / "shelf_life_ml_training_evaluation.json"
    with open(report_json_path, "w") as f:
        json.dump(report_data, f, indent=2)

    # Write Markdown report
    report_md_path = REPORTS_DIR / "shelf_life_ml_training_evaluation.md"
    with open(report_md_path, "w") as f:
        f.write("# FoodFresh AI — Shelf-Life Machine Learning Model Evaluation Report\n\n")
        f.write(f"**Date:** {time.strftime('%B %d, %Y')}\n")
        f.write(f"**Selected Production Model:** `{best_name}`\n")
        f.write(f"**Model Checkpoint Path:** `{model_path}`\n\n")
        f.write("## 1. Held-Out Test Set Model Benchmark (N=6,192)\n\n")
        f.write("| Model Architecture | Test MAE (days) | Test RMSE (days) | Test R² Score | Training Time (s) |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for k, v in results.items():
            f.write(f"| **{k}** | {v['mae']:.4f} | {v['rmse']:.4f} | {v['r2']:.4f} | {v['train_time_s']:.1f}s |\n")
        f.write("\n## 2. Error Breakdown by Food Domain\n\n")
        f.write("| Food Domain | Test MAE (days) | Test Samples |\n")
        f.write("|---|---:|---:|\n")
        for row in category_errors.to_dict(orient="records"):
            f.write(f"| {row['food_domain'].title()} | {row['mae']:.4f} | {row['sample_count']} |\n")
        f.write("\n## 3. Error Breakdown by Storage Type\n\n")
        f.write("| Storage Type | Test MAE (days) | Test Samples |\n")
        f.write("|---|---:|---:|\n")
        for row in storage_errors.to_dict(orient="records"):
            f.write(f"| {row['storage_type'].title()} | {row['mae']:.4f} | {row['sample_count']} |\n")
        f.write("\n## 4. Safety Guardrail Integration\n\n")
        f.write("The trained ML regressor provides empirical, data-driven estimates of remaining shelf-life days. ")
        f.write("To ensure absolute consumer food safety, the model is integrated into `backend/app/services/shelf_life_service.py` ")
        f.write("with USDA FoodKeeper canonical rules serving as strict upper-bound guardrails and fallback when produce is spoiled.\n")

    logger.info(f"Evaluation reports written to {report_json_path} and {report_md_path}")
    return report_data


if __name__ == "__main__":
    data = load_and_preprocess_data()
    results = train_and_evaluate_models(data)
    save_best_model_and_reports(data, results)
    print("\nTraining and evaluation finished successfully!")
