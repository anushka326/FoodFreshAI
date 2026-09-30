# Shelf life interval classifier training

- Candidate: `models/candidates/shelf_life_interval_efficientnet_b0.pth`
- Architecture: EfficientNet-B0 initialized from the completed Freshness V3 candidate; 24 food × freshness-stage interval classes.
- Device: CUDA; 9,856 training and 2,131 validation samples; best checkpoint selected at epoch 7 of 8.
- Best validation interval accuracy: 95.07%.
- Training history and reproducible held-out results: `shelf_life_interval_training_metrics.json`.

The target is the taxonomy interval attached to each AgriFreshNET food/stage label. There are no image-specific elapsed-day, storage, temperature, humidity, or harvest-date observations. This model therefore predicts an interval class from an RGB image; it is not a remaining-life regressor. The FoodKeeper rules remain the production baseline, and this research candidate is not integrated or promoted.
