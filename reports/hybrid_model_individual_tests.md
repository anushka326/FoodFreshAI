# FoodFresh AI — Individual Hybrid Vision Model Tests

Evaluation of each individual model in the hybrid vision stack on canonical project images.

| Image | Model | Prediction | Confidence / Score (%) | Top Predictions | Latency (ms) | Error |
|-------|-------|------------|------------------------|-----------------|--------------|-------|
| Pomegranate | Grounding DINO (base) | **pomegranate** | 65.87% | pomegranate (65.87%) | 2514.7 | None |
| Pomegranate | SigLIP 2 (base-patch16-224) | **pomegranate** | 98.35% | pomegranate (98.35%); apple (0.68%); passion fruit (0.13%) | 389.8 | None |
| Pomegranate | Raw Food ResNet-50 | **Pomegranate** | 98.60% | Pomegranate (98.6%); Beetroot (0.58%); Apple (0.3%) | 143.8 | None |
| Pomegranate | Freshness ResNet-18 | **Fresh** | 50.98% | Fresh: 50.98%; Rotten: 11.35%; Slightly Spoiled: 37.68% | 88.6 | None |
| Tomato | Grounding DINO (base) | **tomato pepper** | 58.57% | tomato pepper (58.57%); tomato (44.15%) | 523.7 | None |
| Tomato | SigLIP 2 (base-patch16-224) | **tomato** | 96.68% | tomato (96.68%); lemon (0.53%); bell pepper (0.52%) | 296.9 | None |
| Tomato | Raw Food ResNet-50 | **Bell Pepper** | 72.71% | Bell Pepper (72.71%); Tomato (25.04%); Apple (0.82%) | 35.4 | None |
| Tomato | Freshness ResNet-18 | **Slightly Spoiled** | 77.41% | Fresh: 1.06%; Rotten: 21.53%; Slightly Spoiled: 77.41% | 14.4 | None |
| Apple | Grounding DINO (base) | **apple** | 65.41% | apple (65.41%) | 513.3 | None |
| Apple | SigLIP 2 (base-patch16-224) | **peach** | 56.92% | peach (56.92%); apple (21.77%); plum (8.55%) | 277.7 | None |
| Apple | Raw Food ResNet-50 | **Apple** | 96.44% | Apple (96.44%); Mango (1.51%); Radish (0.65%) | 27.5 | None |
| Apple | Freshness ResNet-18 | **Fresh** | 56.35% | Fresh: 56.35%; Rotten: 12.64%; Slightly Spoiled: 31.01% | 14.3 | None |
| Banana | Grounding DINO (base) | **banana** | 82.18% | banana (82.18%) | 529.7 | None |
| Banana | SigLIP 2 (base-patch16-224) | **banana** | 99.50% | banana (99.5%); lemon (0.1%); mango (0.08%) | 278.1 | None |
| Banana | Raw Food ResNet-50 | **Sweet Potato** | 62.10% | Sweet Potato (62.1%); Pumpkin (20.03%); Pineapple (7.5%) | 35.0 | None |
| Banana | Freshness ResNet-18 | **Slightly Spoiled** | 93.23% | Fresh: 0.92%; Rotten: 5.86%; Slightly Spoiled: 93.23% | 17.4 | None |
| Orange | Grounding DINO (base) | **pear** | 27.40% | pear (27.4%); mango (25.97%) | 529.4 | None |
| Orange | SigLIP 2 (base-patch16-224) | **orange** | 76.71% | orange (76.71%); lime (10.41%); lemon (9.37%) | 279.8 | None |
| Orange | Raw Food ResNet-50 | **Pear** | 44.94% | Pear (44.94%); Pumpkin (19.03%); Bell Pepper (8.95%) | 24.0 | None |
| Orange | Freshness ResNet-18 | **Slightly Spoiled** | 53.44% | Fresh: 0.16%; Rotten: 46.4%; Slightly Spoiled: 53.44% | 16.6 | None |

## Summary & Observations

- **Grounding DINO** operates as an open-vocabulary bounding box detector with prompt-based localization.
- **SigLIP 2** classifies against the open food vocabulary without fixed-class retraining.
- **Raw Food ResNet-50** acts as a domain-specific classifier across 90 raw agricultural classes.
- **Freshness ResNet-18** predicts visible surface quality states ('Fresh', 'Slightly Spoiled', 'Rotten').
