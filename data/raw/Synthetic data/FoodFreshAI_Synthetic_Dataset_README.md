# FoodFresh AI — Synthetic Freshness & Shelf-Life Dataset v1

## What this is

This is a **synthetic metadata/label dataset** generated for FoodFresh AI to support:

- freshness-model prototyping
- UI regression testing
- shelf-life-rule validation
- robustness experiments across lighting/background/image-quality conditions
- testing that low illumination does not automatically imply "rotten"
- testing food-domain-specific labels such as `Stale`/`Moldy` for bakery products

It contains **41,280 rows across 43 food classes**.

## Critical limitation

This is **not** a replacement for real food images or laboratory food-safety measurements.

`is_real_image=False` and `is_training_ground_truth=False` are intentionally included.

For the actual image model, combine:

1. real AgriFreshNET images and labels;
2. Fruits-360 / other real food-recognition images for identity;
3. controlled augmentation of real images;
4. real validation/test images captured under different lighting/backgrounds;
5. this synthetic table only as auxiliary metadata / regression data.

AgriFreshNET reports 14,500 RGB images across 24 fruit/vegetable classes, Fresh/Semi-Fresh/Rotten labels, real-world capture conditions, and approximate shelf-life ranges. It is therefore much more appropriate as a real freshness/shelf-life source than fabricated image labels.

## Food classes

Apple, Avocado, Banana, Beetroot, Bittermelon, Bread, Broccoli, Bun, Cabbage, Cake, Carrot, Cauliflower, Cherry, Chilli Pepper, Corn, Cucumber, Eggplant, Garlic, Ginger, Grape, Green Bean, Guava, Lemon, Lettuce, Mango, Onion, Orange, Papaya, Peach, Pear, Pepper, Pineapple, Plum, Pomegranate, Potato, Radish, Roti, Spinach, Strawberry, Sweet Potato, Toast, Tomato, Watermelon

## Core design decisions

### 1. Bakery is not labelled "Rotten"

For Bread, Toast, Roti, Bun and Cake:

- `Fresh`
- `Stale` / `Stale/Dry`
- `Moldy`

This prevents the UI from using a produce-specific "Rotten" label for bakery products.

### 2. Low light is a nuisance variable

The dataset includes:

- low
- normal
- high
- warm
- backlit
- uneven

But the synthetic generator does **not** make a food rotten merely because the image is dark.

The correct model strategy is to learn spoilage cues while becoming robust to illumination changes.

### 3. Shelf-life is capped

For this prototype's conservative product policy:

- produce on countertop: maximum 7 days
- produce refrigerated: maximum 15 days

These are **project constraints**, not universal food-safety claims. Real storage limits vary substantially by food, cut/whole state, packaging, temperature history and source guidance. FoodSafety.gov explicitly provides item-specific cold-storage limits and points users to FoodKeeper for item-specific storage guidance.

### 4. Cut food gets a shorter synthetic window

Whole, cut, sliced and diced forms have different synthetic caps. This makes the model/UI test whether the food form affects shelf-life.

## Recommended model

For the image freshness head, use **EfficientNet-B0** as the practical baseline/backbone.

Recommended architecture:

`Image -> preprocessing/color normalization -> EfficientNet-B0 -> shared embedding -> multi-task heads`

Heads:

1. Food domain / food identity
2. Food form
3. Freshness stage
4. Freshness score
5. Visual-defect scores

Do NOT train shelf-life directly from this synthetic table and then present it as measured truth.

For shelf-life:

`food identity + form + storage + temperature + days stored + freshness stage -> constrained reference/rule engine`

Then optionally train a real regression model only after enough real shelf-life observations are collected.

## Recommended image augmentation

Use real images and apply controlled augmentation:

- brightness/contrast
- gamma
- color temperature
- shadows
- mild blur
- sensor noise
- rotation
- crop/scale
- background variation

Keep the original real image as the label source.

Do not create fake "rotten" images simply by darkening a fresh image. That teaches the model that darkness equals spoilage.

## Suggested split

For real images:

- train: 70%
- validation: 15%
- test: 15%

Split by **original specimen/image group**, not by augmented copy, to prevent leakage.

Keep a dedicated stress-test set:

- low light
- backlit
- warm light
- cluttered background
- cut food
- partial occlusion
- real household images

## Important implementation rule

The model should be allowed to return:

`Unknown / Low confidence`

instead of forcing an incorrect food or freshness label.

This is especially important for cases like chilli, avocado, beetroot, bakery products and images where specialist models disagree.

