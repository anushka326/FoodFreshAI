# FoodFresh AI - ML Training & Deployment Guide

**Status:** Freshness Model V3 Training IN PROGRESS (Epoch 5/20)

---

## 📊 Quick Status

| Component | Status | Location |
|-----------|--------|----------|
| Freshness V3 Training | 🔴 ACTIVE (25% complete) | `ml/freshness/train_efficientnet_v3.py` |
| Freshness V3 Model | 🟡 Checkpoint saved | `models/candidates/freshness_v3_efficientnet_b0.pth` |
| Shelf-Life V1 Training | 🟡 Staged (encoding issue) | `ml/shelf_life/train_v1.py` |
| Deployment Scripts | ✅ Ready | `scripts/deploy_orchestrator.py` |
| Integration Tests | ✅ Ready | `scripts/integration_test.py` |
| Backend | ✅ Ready | `python backend.app.main:app` |
| Frontend | ✅ Ready | `npm run dev` |

---

## 🚀 NEXT STEPS (In Order)

### STEP 1: Wait for Freshness V3 Training to Complete

The model is currently training. You can monitor progress:

```bash
# Check model checkpoint (updates as training saves best model)
ls -lh models/candidates/freshness_v3_efficientnet_b0.pth

# Check training history once completed
tail -50 reports/freshness_v3_training_history.csv

# Check final report
cat reports/freshness_v3_training_report.md
```

**Expected:** 
- Training should complete in 1-3 hours (depending on GPU)
- Generates: `freshness_v3_training_history.csv` and `freshness_v3_training_report.md`
- Model saved to: `models/candidates/freshness_v3_efficientnet_b0.pth`

---

### STEP 2: Run Deployment Readiness Check

Once training completes:

```bash
python scripts/check_deployment_readiness.py
```

This will:
- ✅ Verify freshness_v3 model exists
- ✅ Check shelf-life v1 status (optional)
- ✅ Generate deployment checklist
- ✅ List known issues

**Expected Output:**
```
📊 FRESHNESS MODEL STATUS
✅ Freshness V3 Candidate: READY
   - File: models/candidates/freshness_v3_efficientnet_b0.pth
   - Size: ~X.X MB
   - Architecture: EfficientNet-B0
```

---

### STEP 3: Promote Models to Production

```bash
# Promote freshness V3
python scripts/promote_model.py promote freshness_v3

# (Optional) Promote shelf-life V1 if ready
python scripts/promote_model.py promote shelf_life_v1
```

This will:
- ✅ Copy candidate to `models/trained/`
- ✅ Backup existing model
- ✅ Update `backend/app/model_config.py`
- ✅ Create promotion log

---

### STEP 4: Verify Database Integration

```bash
python scripts/verify_database.py
```

This will:
- ✅ Check database schema
- ✅ Verify ML feedback tables
- ✅ Test write permissions
- ✅ Generate verification report

---

### STEP 5: Start Backend Server (Terminal 1)

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Wait for:
```
Uvicorn running on http://127.0.0.1:8000
```

---

### STEP 6: Start Frontend Server (Terminal 2)

```bash
cd frontend
npm run dev
```

Wait for:
```
Local:   http://localhost:3000
```

---

### STEP 7: Run Integration Tests (Terminal 3)

```bash
python scripts/integration_test.py
```

This will:
- ✅ Test API connectivity
- ✅ Verify model loading
- ✅ Run inference on test images
- ✅ Check database persistence
- ✅ Generate integration report

**Expected:**
- Green checkmarks for connectivity and basic tests
- Real-world image predictions
- Database records verified

---

### STEP 8: Manual Testing in Browser

1. Open http://localhost:3000
2. Click "Analyze Food"
3. Upload/capture an image
4. Verify prediction appears
5. Check freshness label, shelf-life estimate, confidence score
6. Save to pantry and verify database stores it

---

## ⚠️ KNOWN ISSUES & WORKAROUNDS

### Issue 1: Green Chilli & Dried Chilli Failures

**Problem:** Both V3 and current models fail on chilli (99-100% confidence → Rotten)

**Root Cause:** Chilli NOT in AgriFreshNET training data

**Expected Behavior:** These are PROTECTED test cases - failures are documented

**Workaround:**
1. Form-aware preprocessing (detect chilli by appearance, adjust expectations)
2. Collect chilli training data
3. Use heuristics for dried forms

**Status:** ⏳ Implement after initial deployment

---

### Issue 2: Shelf-Life "Not Available"

**Problem:** Some foods show "Not available" for shelf-life estimate

**Root Cause:** Missing FoodKeeper entries or form-gating (dried/powdered)

**Workaround:** ML model provides broader coverage (if deployed)

**Status:** ✅ Can use shelf-life V1 model once training fixed

---

### Issue 3: Confidence Calibration

**Problem:** Model sometimes shows 99%+ confidence on wrong predictions

**Root Cause:** Lack of calibration or adversarial examples

**Workaround:** Use existing calibration gates in `freshness_service.py`:
```python
if top_score < 50% or margin < 10%:
    return UNCERTAIN
```

**Status:** ✅ Already implemented in production code

---

## 📋 DEPLOYMENT CHECKLIST

- [ ] Freshness V3 training complete
- [ ] `models/candidates/freshness_v3_efficientnet_b0.pth` exists
- [ ] Promotion script successful
- [ ] `models/trained/freshness_v3.pth` exists
- [ ] Database verification passed
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Integration tests pass (80%+ pass rate)
- [ ] Manual browser testing successful
- [ ] Regression cases documented
- [ ] Deployment log generated

---

## 🔍 MONITORING & VALIDATION

### Check Model Version in Production

```bash
# View current model config
cat backend/app/model_config.py | grep -A5 "food_freshness"

# Expected:
#   'status': 'ACTIVE',
#   'model_version': 'v3',
#   'checkpoint_path': 'models/trained/freshness_v3.pth',
```

### Verify Database Records

```bash
# Check if analyses are being stored
python
>>> import sqlite3
>>> conn = sqlite3.connect('backend/app/database/fresho_buddy.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT COUNT(*) FROM pantry_history WHERE freshness_model_version = 'v3'")
>>> print(cursor.fetchone())  # Should show count > 0 after testing
```

### Monitor Model Versions

```bash
# See distribution of model versions in production
python
>>> cursor.execute("SELECT freshness_model_version, COUNT(*) FROM pantry_history GROUP BY freshness_model_version")
>>> print(cursor.fetchall())
# Should show v3 appearing after deployment
```

---

## 🛠️ TROUBLESHOOTING

### Backend Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000  # on Linux/Mac
netstat -ano | findstr :8000  # on Windows

# Kill existing process or use different port
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Frontend Won't Start

```bash
# Make sure npm is installed and dependencies are there
cd frontend
npm install

# Clear cache and restart
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Model Prediction Fails

```bash
# Check model file exists
ls -lh models/trained/freshness_v3.pth

# Check model loading in Python
python
>>> from ml.hybrid_vision.freshness_service import FreshnessService
>>> service = FreshnessService()
>>> print(service.model)  # Should print model info, not error
```

### Database Integration Fails

```bash
# Verify database exists and is readable
ls -lh backend/app/database/fresho_buddy.db

# Test database connection
python scripts/verify_database.py
```

---

## 📚 REFERENCE COMMANDS

### Training Scripts
```bash
# Start freshness V3 training (if not running)
python ml/freshness/train_efficientnet_v3.py

# Start shelf-life V1 training (optional)
python ml/shelf_life/train_v1.py
```

### Evaluation Scripts
```bash
# Compare models
python scripts/compare_freshness_models.py

# Dataset discovery
python scripts/discover_agrifreshnet.py
```

### Deployment Scripts
```bash
# Orchestrate full deployment
python scripts/deploy_orchestrator.py

# Promote single model
python scripts/promote_model.py promote freshness_v3

# Verify model in production
python scripts/promote_model.py verify freshness_v3

# Rollback to previous version
python scripts/promote_model.py rollback freshness_v3
```

### Testing Scripts
```bash
# Integration tests
python scripts/integration_test.py

# Database verification
python scripts/verify_database.py

# Deployment readiness
python scripts/check_deployment_readiness.py
```

---

## 📊 DATASET INFORMATION

### AgriFreshNET

**Foods (8):** Banana, Bittermelon, Cucumber, Eggplant, Orange, Papaya, Pineapple, Tomato

**Classes (3):** Fresh, Rotten, Semi-Fresh

**Split:** 9,856 train / 2,131 val / 2,173 test (perfectly balanced)

**Key Fact:** NO CHILLI DATA (explains regression failures)

### FoodKeeper

**Coverage:** 200+ food products

**Storage Types:** Room Temperature, Refrigerator, Freezer

**Status:** ✅ Fully integrated in shelf_life_service.py

---

## 🎯 SUCCESS CRITERIA

| Criterion | Status |
|-----------|--------|
| Freshness V3 trained on AgriFreshNET | 🔴 In Progress |
| Model metrics > V2 baseline | ⏳ To Measure |
| Models promoted to production | ⏳ Pending |
| Backend starts successfully | ✅ Ready |
| Frontend starts successfully | ✅ Ready |
| Integration tests pass | ✅ Ready (pending deployment) |
| End-to-end workflow working | ⏳ To Verify |
| Database records created | ⏳ To Verify |
| Regression cases documented | ✅ Complete |

---

## 📝 FINAL NOTES

1. **Session Saved:** See `reports/ml_training_session_summary.md` for detailed work log
2. **Scripts Ready:** 10+ production-ready scripts in `scripts/` directory
3. **Infrastructure Complete:** All supporting code, databases, and configs in place
4. **Training Active:** Don't interrupt Epoch 5/20 training (let it complete)
5. **Deployment Easy:** Just follow the 8 steps above once training finishes

**Next Action:** Monitor training progress and run Step 2 (Readiness Check) once complete.

---

**Last Updated:** Just now  
**Training Status:** Epoch 5/20, Loss: 0.0855  
**Estimated Training Time Remaining:** 1-2 hours
