# FoodFresh AI — Real-World Food Recognition V2 Evaluation Report

## Status
**No real-world evaluation images were available.**

The `data/real_world_eval/` folder structure has been prepared with subfolders for:
- `Apple/`
- `Banana/`
- `Orange/`
- `Pomegranate/`
- `Tomato/`
- `Mango/`

## Confidence Threshold & Calibration Note
- **Confidence threshold requires additional calibration data.**
- Softmax confidence outputs do not represent calibrated true probabilities on out-of-distribution real-world images.
- When real-world user photos are added to `data/real_world_eval/`, re-run `python scripts/evaluate_real_world_food.py` to calculate accuracy and establish an empirically grounded confidence threshold.
