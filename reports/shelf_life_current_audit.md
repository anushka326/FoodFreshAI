# Shelf-Life Current Audit

## Live implementation
**File:** `backend/app/services/shelf_life_service.py`  
**Reference data:** `data/raw/foodkeeper/FoodKeeper.json`  
**Production ML shelf-life model:** **None connected.** No XGBoost checkpoint is loaded in the inference path.

## Lookup logic
1. Normalize food name
2. `CANONICAL_PRODUCE_MAPPING` → FoodKeeper product ID
3. Fallback exact / token match on product names
4. Ambiguous multi-match → unavailable (no guess)

## Storage
- `countertop` / ambient → FoodKeeper `Pantry_*` fields
- `fridge` / crisper → `Refrigerate_*` fields

## Freshness adjustment
- `rotten` → remaining 0
- `slightly_spoiled` → 50% reduction heuristic
- Otherwise reference window minus `days_stored`

## Food form (new)
`dried`, `powdered`, `processed`, `cooked` → **unavailable** with explicit form message (no invented days).

## Unsupported
Unknown food, ambiguous FoodKeeper match, missing storage duration, unsupported form.

## Supported examples
Apple, banana, orange, tomato, mango, pomegranate, potato, bell pepper, fresh chilli (FoodKeeper hot peppers), cucumber, watermelon, cantaloupe (when JSON present).

See `reports/shelf_life_regression.md` and `tests/test_shelf_life_regression.py`.
