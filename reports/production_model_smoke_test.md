# Freshness model real-image smoke test

Local images from `data/real_world_eval` were run through the production V2 `FreshnessService` after loading the configured validation-fitted temperature (T=1.111828). The V3 outputs are from its earlier candidate run. These 11 selected fixtures are regression checks, not a representative benchmark.

| Local image / expected condition | Production V2 calibrated result | V3 candidate result |
|---|---|---|
| `green_chilli.jpg` / fresh green chilli | Fresh, 91.95% | Fresh, 78.28% |
| `rotten_tomato.jpg` / rotten tomato | Rotten, 100.00% | Rotten, 100.00% |
| `rotten_orange.jpg` / rotten orange | Rotten, 100.00% | Rotten, 100.00% |
| `bell_pepper.jpg` / fresh bell pepper | Fresh (Moderate Confidence), 57.80% | Fresh, 62.05% |
| `potato.jpg` / fresh potato | Rotten (Moderate Confidence), 64.11% | Fresh, 97.97% |
| `mango.jpg` / fresh mango | Fresh, 83.33% | Rotten, 59.61% |
| `apple.jpg` / fresh apple | Rotten, 82.50% | Fresh, 48.23% |
| `pomegranate.jpg` / fresh pomegranate | Rotten, 99.58% | Fresh, 89.53% |
| `tomato.jpg` / fresh tomato | Fresh, 99.94% | Fresh, 99.48% |
| `banana.jpg` / fresh banana | Fresh, 99.88% | Fresh, 100.00% |
| `bread.jpg` / fresh bread | Rotten, 100.00% | Rotten, 99.74% |
| dried red chilli | Not evaluated; no local image | Not evaluated; no local image |

V2 was correct on 7/11 and V3 on 9/11 selected labelled fixtures. Green chilli is absent from AgriFreshNET training; a single fixture does not establish general chilli support. Bread is outside the AgriFreshNET classes. V3 remains unpromoted because its held-out metrics do not reconcile with the trainer's reported metrics. V2 remains active with the validation-fitted temperature. This smoke test does not replace broader external evaluation.
