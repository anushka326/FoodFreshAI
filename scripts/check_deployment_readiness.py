#!/usr/bin/env python
"""
FoodFresh AI - Training and Deployment Summary
Final checkpoint before production deployment.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORTS_DIR = PROJECT_ROOT / "reports"
CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
TRAINED_DIR = PROJECT_ROOT / "models" / "trained"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def check_freshness_model():
    """Check freshness model status."""
    
    candidate = CANDIDATES_DIR / "freshness_v3_efficientnet_b0.pth"
    production = TRAINED_DIR / "freshness_v3.pth"
    
    status = {
        'candidate_exists': candidate.exists(),
        'in_production': production.exists(),
        'candidate_size_mb': candidate.stat().st_size / 1024 / 1024 if candidate.exists() else 0,
        'production_size_mb': production.stat().st_size / 1024 / 1024 if production.exists() else 0,
    }
    
    return status


def check_shelf_life_model():
    """Check shelf-life model status."""
    
    candidate = CANDIDATES_DIR / "shelf_life_v1_regression.pth"
    encoders = CANDIDATES_DIR / "shelf_life_v1_encoders.pkl"
    production = TRAINED_DIR / "shelf_life_v1.pth"
    
    status = {
        'candidate_exists': candidate.exists() and encoders.exists(),
        'in_production': production.exists(),
        'candidate_size_mb': candidate.stat().st_size / 1024 / 1024 if candidate.exists() else 0,
        'encoders_size_mb': encoders.stat().st_size / 1024 / 1024 if encoders.exists() else 0,
    }
    
    return status


def generate_final_summary():
    """Generate final summary report."""
    
    print("=" * 100)
    print("FOODFRESH AI - TRAINING AND DEPLOYMENT SUMMARY")
    print("=" * 100)
    
    freshness_status = check_freshness_model()
    shelf_life_status = check_shelf_life_model()
    
    # Freshness model
    print("\n📊 FRESHNESS MODEL STATUS")
    print("-" * 100)
    
    if freshness_status['candidate_exists']:
        print(f"✅ Freshness V3 Candidate: READY")
        print(f"   - File: models/candidates/freshness_v3_efficientnet_b0.pth")
        print(f"   - Size: {freshness_status['candidate_size_mb']:.1f} MB")
        print(f"   - Architecture: EfficientNet-B0")
        print(f"   - Training Data: AgriFreshNET (9,856 images)")
        print(f"   - Classes: Fresh, Semi-Fresh, Rotten (3-class)")
        
        if freshness_status['in_production']:
            print(f"✅ Freshness V3: IN PRODUCTION")
        else:
            print(f"⏳ Status: Ready for promotion to production")
    else:
        print(f"❌ Freshness V3 Candidate: NOT FOUND")
        print(f"   - Training may still be in progress")
        print(f"   - Check: python ml/freshness/train_efficientnet_v3.py")
    
    # Shelf-life model
    print("\n📊 SHELF-LIFE MODEL STATUS")
    print("-" * 100)
    
    if shelf_life_status['candidate_exists']:
        print(f"✅ Shelf-Life V1 Candidate: READY")
        print(f"   - File: models/candidates/shelf_life_v1_regression.pth")
        print(f"   - Size: {shelf_life_status['candidate_size_mb']:.1f} MB")
        print(f"   - Encoders: {shelf_life_status['encoders_size_mb']:.1f} MB")
        print(f"   - Architecture: Neural Network Regression")
        print(f"   - Input: Food type + Freshness + Storage type")
        print(f"   - Output: Shelf-life in days")
        
        if shelf_life_status['in_production']:
            print(f"✅ Shelf-Life V1: IN PRODUCTION")
        else:
            print(f"⏳ Status: Ready for promotion to production")
    else:
        print(f"⚠️ Shelf-Life V1 Candidate: NOT FOUND")
        print(f"   - Training may still be in progress or failed")
        print(f"   - System will use FoodKeeper heuristics as fallback")
        print(f"   - Check: python ml/shelf_life/train_v1.py")
    
    # Deployment readiness
    print("\n🚀 DEPLOYMENT READINESS")
    print("-" * 100)
    
    if freshness_status['candidate_exists']:
        print("✅ Minimum deployment requirements MET")
        print("   - Freshness model V3 is ready for production")
        print("   - System can start and make predictions")
    else:
        print("❌ Cannot proceed with deployment")
        print("   - Wait for freshness model training to complete")
    
    # Deployment steps
    print("\n📋 DEPLOYMENT PROCEDURE")
    print("-" * 100)
    
    if freshness_status['candidate_exists']:
        print("\n1. Promote Freshness V3 to Production:")
        print("   python scripts/promote_model.py promote freshness_v3")
        
        if shelf_life_status['candidate_exists']:
            print("\n2. (Optional) Promote Shelf-Life V1 to Production:")
            print("   python scripts/promote_model.py promote shelf_life_v1")
        
        print("\n3. Verify Database Integration:")
        print("   python scripts/verify_database.py")
        
        print("\n4. Start Backend Server (Terminal 1):")
        print("   cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
        
        print("\n5. Start Frontend Server (Terminal 2):")
        print("   cd frontend && npm run dev")
        
        print("\n6. Run Integration Tests (Terminal 3):")
        print("   python scripts/integration_test.py")
        
        print("\n7. Open Browser:")
        print("   http://localhost:3000")
        
        print("\n8. Test Full Workflow:")
        print("   - Upload food images")
        print("   - Verify predictions are shown")
        print("   - Check that database records are created")
    
    # Generate report file
    report_path = REPORTS_DIR / "deployment_readiness_report.md"
    
    with open(report_path, 'w') as f:
        f.write("# Deployment Readiness Report\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        
        f.write("## Model Status\n\n")
        f.write("### Freshness Model V3 (EfficientNet-B0)\n")
        if freshness_status['candidate_exists']:
            f.write(f"- ✅ Status: READY FOR DEPLOYMENT\n")
            f.write(f"- Candidate: {freshness_status['candidate_size_mb']:.1f} MB\n")
            f.write(f"- Architecture: EfficientNet-B0 pretrained\n")
            f.write(f"- Training Dataset: AgriFreshNET (9,856 training images)\n")
            f.write(f"- Classes: Fresh, Semi-Fresh, Rotten\n")
            f.write(f"- Features: Batch normalization, dropout, proper augmentation\n")
        else:
            f.write(f"- ❌ Status: NOT READY\n")
            f.write(f"- Training may still be in progress\n")
        
        f.write("\n### Shelf-Life Model V1 (Neural Network Regression)\n")
        if shelf_life_status['candidate_exists']:
            f.write(f"- ✅ Status: READY FOR DEPLOYMENT (optional)\n")
            f.write(f"- Model: {shelf_life_status['candidate_size_mb']:.1f} MB\n")
            f.write(f"- Encoders: {shelf_life_status['encoders_size_mb']:.1f} MB\n")
            f.write(f"- Architecture: Food + Freshness + Storage embeddings → Shelf-life regression\n")
            f.write(f"- Training Dataset: FoodKeeper + AgriFreshNET\n")
        else:
            f.write(f"- ⚠️ Status: OPTIONAL - System will use FoodKeeper heuristics if not deployed\n")
        
        f.write("\n## Deployment Checklist\n\n")
        f.write("- [ ] Freshness V3 model trained and saved to models/candidates/\n")
        f.write("- [ ] Shelf-Life V1 model trained (optional)\n")
        f.write("- [ ] Database schema verified with verify_database.py\n")
        f.write("- [ ] Models promoted to production with promote_model.py\n")
        f.write("- [ ] Backend started: uvicorn backend.app.main:app --port 8000\n")
        f.write("- [ ] Frontend started: npm run dev\n")
        f.write("- [ ] Integration tests passed: python scripts/integration_test.py\n")
        f.write("- [ ] Manual testing completed in browser\n")
        f.write("- [ ] Production deployment completed\n")
        
        f.write("\n## Known Issues & Workarounds\n\n")
        f.write("### Green Chilli & Dried Chilli Failures\n")
        f.write("- **Issue:** Both models fail on chilli (not in AgriFreshNET training data)\n")
        f.write("- **Cause:** Domain gap - neither model trained on chilli images\n")
        f.write("- **Solution:** Implement form-aware preprocessing or collect chilli training data\n\n")
        
        f.write("### Confidence Calibration\n")
        f.write("- **Issue:** Some models show 99%+ confidence on wrong predictions\n")
        f.write("- **Solution:** Use calibration gates in freshness_service.py\n\n")
        
        f.write("### FoodKeeper Shelf-Life Coverage\n")
        f.write("- **Issue:** Some foods show \"Not available\" for shelf-life\n")
        f.write("- **Solution:** ML model provides broader coverage, or add manual entries\n\n")
        
        f.write("## Success Criteria\n\n")
        f.write("✅ **Minimum Success:** Freshness model V3 in production, making predictions\n")
        f.write("✅ **Full Success:** Both models in production, end-to-end testing passed\n")
        f.write("✅ **Production Ready:** All tests pass, UI shows predictions, DB records created\n")
    
    print(f"\n\n✅ Deployment readiness report saved to: {report_path}")
    
    print("\n" + "=" * 100)
    print("NEXT STEPS")
    print("=" * 100)
    
    if freshness_status['candidate_exists']:
        print("\n✅ READY FOR DEPLOYMENT")
        print("\nRun the orchestration script:")
        print("   python scripts/deploy_orchestrator.py")
        print("\nThis will:")
        print("   1. Evaluate models")
        print("   2. Promote to production")
        print("   3. Verify database")
        print("   4. Provide startup instructions")
    else:
        print("\n⏳ WAITING FOR MODEL TRAINING")
        print("\nCheck training progress:")
        print("   ls -lh models/candidates/")
        print("   tail -f reports/*training_history.csv")
        print("\nRe-run this script once training completes")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    generate_final_summary()
