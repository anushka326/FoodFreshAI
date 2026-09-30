# Freshness V3 training status and result

- **Status:** Complete; the previously active process exited and wrote its final report.
- **Script:** `ml/freshness/train_efficientnet_v3.py`
- **Architecture:** EfficientNet-B0, 3 classes: Fresh / Semi-Fresh / Rotten
- **Data:** AgriFreshNET (9,856 train / 2,131 validation / 2,173 test)
- **Device:** CUDA
- **Epochs completed:** 20
- **Best validation macro F1:** 0.9384 at epoch 17; the candidate checkpoint was saved when validation F1 improved.
- **Final candidate checkpoint:** `models/candidates/freshness_v3_efficientnet_b0.pth` (checkpoint timestamp 2026-09-30 13:06 local; training final report timestamp 13:39 local)
- **Training history:** `reports/freshness_v3_training_history.csv`
- **Training report:** `reports/freshness_v3_training_report.md`

The trainer-generated report claims held-out accuracy 0.9365, balanced accuracy 0.9361, macro F1 0.9357, and weighted F1 0.9360. That result did not reproduce: the saved checkpoint, evaluated twice on the same manifest (including once with the trainer's own model and evaluator functions), scored accuracy 0.8260, balanced accuracy 0.8250, and macro F1 0.8212. The saved checkpoint is intact and loads, but the discrepancy is unresolved. Use the independently reproduced result for decisions; the candidate was not promoted. See `freshness_model_v3_evaluation.md`.
