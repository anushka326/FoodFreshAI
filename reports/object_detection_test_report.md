# FoodFresh AI — Grounding DINO Object Detection Evaluation Report
**Date:** September 2026  
**Model:** IDEA-Research/grounding-dino-base  
**Task:** Open-vocabulary scene context and kitchen object detection  
**Controlled Vocabulary:** `table`, `countertop`, `plate`, `bowl`, `spoon`, `fork`, `knife`, `glass`, `cup`, `tray`, `container`, `basket`, `cutting board`, `bag`, `food`, `fruit`, `vegetable`

## 1. Executive Summary
Grounding DINO is utilized as an open-vocabulary object detector operating in dual mode: first isolating candidate food regions for high-resolution specialist classification, and second identifying ambient kitchen objects (e.g., plates, countertops, cutting boards, bowls) to contextualize produce storage and consumption environments.

## 2. Real-World Test Results

| Image | Primary Detected Food | Scene Objects Detected | Confidences | Count | Status |
|---|---|---|---|:---:|:---:|
| `pomegranate.jpg` | **Pomegranate** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `apple.jpg` | **Apple** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `orange.jpg` | **Uncertain / None** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `banana.jpg` | **Banana** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `tomato.jpg` | **Tomato** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `mango.jpg` | **Mango** | *No additional scene objects* | - | 0 | `SUCCESS` |
| `bread.jpg` | **Bread** | cutting board | knife | bowl | spoon | tray | 58.3% | 57.0% | 51.7% | 44.0% | 26.3% | 5 | `SUCCESS` |
| `multi_apple_banana_tomato.jpg` | **Banana** | *No additional scene objects* | - | 0 | `SUCCESS` |

## 3. Detailed Per-Image Analysis

### `pomegranate.jpg`
- **Primary Food Recognized:** Pomegranate
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** pomegranate (68.4%)
- **Pipeline Execution Time:** 2626.1 ms

### `apple.jpg`
- **Primary Food Recognized:** Apple
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** apple (69.2%)
- **Pipeline Execution Time:** 1051.7 ms

### `orange.jpg`
- **Primary Food Recognized:** Uncertain / None
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** mango food (28.2%), mango (23.7%)
- **Pipeline Execution Time:** 905.7 ms

### `banana.jpg`
- **Primary Food Recognized:** Banana
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** banana (82.7%)
- **Pipeline Execution Time:** 1036.8 ms

### `tomato.jpg`
- **Primary Food Recognized:** Tomato
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** tomato pepper (61.3%), tomato (42.4%)
- **Pipeline Execution Time:** 971.6 ms

### `mango.jpg`
- **Primary Food Recognized:** Mango
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** mango (52.0%)
- **Pipeline Execution Time:** 855.5 ms

### `bread.jpg`
- **Primary Food Recognized:** Bread
- **Scene Objects Isolated:** cutting board | knife | bowl | spoon | tray
- **Scene Confidences:** 58.3% | 57.0% | 51.7% | 44.0% | 26.3%
- **All Raw DINO Detections:** cutting board (58.3%), knife (57.0%), bowl (51.7%), bread (46.0%), spoon (44.0%), bread (39.6%), bread (37.7%), bread (36.5%), tabletop (35.4%), plate bowl (34.1%), bread (34.0%), bread (32.5%), tray (26.3%), bread (24.9%), glass (24.9%), bowl (24.9%), food (23.6%), ##top (23.0%)
- **Pipeline Execution Time:** 1487.0 ms

### `multi_apple_banana_tomato.jpg`
- **Primary Food Recognized:** Banana
- **Scene Objects Isolated:** none
- **Scene Confidences:** none
- **All Raw DINO Detections:** banana (77.1%), pepper (71.5%), apple (52.5%), tomato (24.0%)
- **Pipeline Execution Time:** 990.6 ms

## 4. Key Findings and Methodology
1. **Food Deduplication:** When a food item (e.g. Apple) is identified as the primary produce, duplicate food labels are suppressed from the secondary scene object caption.
2. **Confidence-Sorted Presentation:** Scene objects are ranked strictly by model confidence, ensuring the most prominent context elements appear first (e.g., Plate · Table · Countertop).
3. **Maximum Limit Enforcement:** At most 5 useful scene objects are presented to keep the user interface uncluttered.
4. **No-Object Graceful Fallback:** Images featuring isolated produce without background containers correctly report `No additional scene objects detected.` without throwing errors or breaking UI cards.
