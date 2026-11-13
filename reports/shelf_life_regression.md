# Shelf-Life Regression Summary

Automated: `tests/test_shelf_life_regression.py`

| Food | Form | Expect availability |
|------|------|---------------------|
| Apple, Banana, Orange, Tomato, Mango, Pomegranate, Potato, Bell Pepper, green chilli, Cucumber, Watermelon, Cantaloupe | fresh | available (if FoodKeeper loaded) |
| dried red chilli | dried | unavailable (form) |
| Grape | fresh | available (fridge) when FoodKeeper loaded |
| Strawberry | fresh | **unavailable** — no canonical FoodKeeper match in current mapping (honest, not invented) |

Run: `python -m pytest tests/test_shelf_life_regression.py -q`
