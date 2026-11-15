# FoodFresh AI — Individual Hybrid Vision Model Tests

Evaluation of each individual model in the hybrid vision stack on canonical project images.

| Image | Model | Prediction | Confidence / Score (%) | Top Predictions | Latency (ms) | Error |
|-------|-------|------------|------------------------|-----------------|--------------|-------|
| Pomegranate | Grounding DINO (base) | **pomegranate** | 59.32% | pomegranate (59.32%); papaya (31.83%) | 2552.9 | None |
| Pomegranate | SigLIP 2 (base-patch16-224) | **pomegranate** | 98.31% | pomegranate (98.31%); apple (0.68%); passion fruit (0.13%) | 391.4 | None |
| Pomegranate | Raw Food ResNet-50 | **Pomegranate** | 98.60% | Pomegranate (98.6%); Beetroot (0.58%); Apple (0.3%) | 122.4 | None |
| Pomegranate | Freshness ResNet-18 | **Rotten** | 99.58% | Fresh: 0.39%; Rotten: 99.58%; Slightly Spoiled: 0.03% | 80.2 | None |
| Tomato | Grounding DINO (base) | **tomato pepper** | 62.85% | tomato pepper (62.85%); tomato (37.11%) | 497.7 | None |
| Tomato | SigLIP 2 (base-patch16-224) | **tomato** | 96.68% | tomato (96.68%); lemon (0.53%); bell pepper (0.52%) | 322.8 | None |
| Tomato | Raw Food ResNet-50 | **Bell Pepper** | 72.71% | Bell Pepper (72.71%); Tomato (25.04%); Apple (0.82%) | 24.9 | None |
| Tomato | Freshness ResNet-18 | **Fresh** | 99.94% | Fresh: 99.94%; Rotten: 0.0%; Slightly Spoiled: 0.06% | 14.1 | None |
| Apple | Grounding DINO (base) | **apple** | 68.04% | apple (68.04%) | 508.5 | None |
| Apple | SigLIP 2 (base-patch16-224) | **peach** | 56.05% | peach (56.05%); apple (21.44%); plum (8.42%) | 307.6 | None |
| Apple | Raw Food ResNet-50 | **Apple** | 96.44% | Apple (96.44%); Mango (1.51%); Radish (0.65%) | 25.9 | None |
| Apple | Freshness ResNet-18 | **Rotten** | 82.42% | Fresh: 11.66%; Rotten: 82.42%; Slightly Spoiled: 5.92% | 12.5 | None |
| Banana | Grounding DINO (base) | **banana** | 81.57% | banana (81.57%) | 531.4 | None |
| Banana | SigLIP 2 (base-patch16-224) | **banana** | 99.44% | banana (99.44%); lemon (0.1%); mango (0.08%) | 304.5 | None |
| Banana | Raw Food ResNet-50 | **Sweet Potato** | 62.10% | Sweet Potato (62.1%); Pumpkin (20.03%); Pineapple (7.5%) | 21.9 | None |
| Banana | Freshness ResNet-18 | **Fresh** | 99.88% | Fresh: 99.88%; Rotten: 0.1%; Slightly Spoiled: 0.02% | 15.3 | None |
| Orange | Grounding DINO (base) | **avocado** | 33.16% | avocado (33.16%); papaya (27.1%) | 563.4 | None |
| Orange | SigLIP 2 (base-patch16-224) | **orange** | 76.17% | orange (76.17%); lime (10.34%); lemon (9.3%) | 315.1 | None |
| Orange | Raw Food ResNet-50 | **Pear** | 44.94% | Pear (44.94%); Pumpkin (19.03%); Bell Pepper (8.95%) | 22.0 | None |
| Orange | Freshness ResNet-18 | **Freshness Uncertain** | 53.36% | Fresh: 53.36%; Rotten: 0.18%; Slightly Spoiled: 46.46% | 15.1 | None |

## Summary & Observations

- **Grounding DINO** operates as an open-vocabulary bounding box detector with prompt-based localization.
- **SigLIP 2** classifies against the open food vocabulary without fixed-class retraining.
- **Raw Food ResNet-50** acts as a domain-specific classifier across 90 raw agricultural classes.
- **Freshness ResNet-18** predicts visible surface quality states ('Fresh', 'Slightly Spoiled', 'Rotten').
