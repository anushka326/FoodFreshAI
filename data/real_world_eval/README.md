# Real-World Food Evaluation Dataset

This directory is designated for evaluating FoodFresh AI Food Recognition V2 against real-world consumer photographs (e.g. photos captured on mobile phone cameras, kitchen lighting, countertop settings, supermarket produce aisles, or refrigerators).

## Purpose
While Fruits-360 provides clean, white-background, high-volume rotary training data, real-world generalization requires validation against diverse natural illumination, backgrounds, and angles.

## Directory Structure
Place test photographs into their corresponding food category folder:

```text
data/real_world_eval/
├── Apple/
├── Banana/
├── Orange/
├── Pomegranate/
├── Tomato/
├── Mango/
... (additional supported V2 classes)
```

## Supported V2 Food Classes (24 Classes)
- Apple, Avocado, Banana, Cherry, Corn, Cucumber
- Eggplant, Grape, Guava, Lemon, Mango, Onion
- Orange, Papaya, Peach, Pear, Pepper, Pineapple
- Plum, Pomegranate, Potato, Strawberry, Tomato, Watermelon

## Image Guidelines
1. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`
2. Keep one dominant food type per image corresponding to the directory name.
3. Natural kitchen lighting, household countertops, and natural backgrounds are encouraged.
4. Do not download synthetic or automated web crawl images; use authentic consumer photos.

## Running Real-World Evaluation
Execute:
```bash
python scripts/evaluate_real_world_food.py
```
This script will:
- Scan `data/real_world_eval/`
- Infer ground truth food names from parent folder names
- Run Food Recognition V2 inference
- Generate `reports/food_recognition_v2_real_world_predictions.csv`
- Compile `reports/food_recognition_v2_real_world_report.md`
