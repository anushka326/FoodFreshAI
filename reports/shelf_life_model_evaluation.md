# Shelf life interval classifier evaluation

Held-out AgriFreshNET test split, evaluated once after selecting the checkpoint by validation accuracy:

- Test samples: 2,173
- 24-class interval accuracy: 94.29%
- Macro F1: 0.9430
- Weighted F1: 0.9424
- Best validation epoch: 7/8; validation accuracy: 95.07%

Per-class precision, recall, F1, support, and the full confusion matrix are in `shelf_life_interval_training_metrics.json`.

These scores measure agreement with the dataset's categorical food/stage labels and the taxonomy-level interval mapped to each label. They do not measure error in days, interval coverage against observed shelf life, or performance under storage conditions. The dataset contains no per-image observed remaining days or storage/age covariates. MAE, RMSE, and R² are therefore not applicable. FoodKeeper remains the production reference; the model checkpoint is an unintegrated candidate and is not promoted.
