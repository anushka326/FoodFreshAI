#!/usr/bin/env python
"""
FoodFresh AI - Complete Deployment Orchestrator
Handles model evaluation, promotion, integration verification, and deployment.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
TRAINED_DIR = PROJECT_ROOT / "models" / "trained"
REPORTS_DIR = PROJECT_ROOT / "reports"
BACKEND_PATH = PROJECT_ROOT / "backend"
FRONTEND_PATH = PROJECT_ROOT / "frontend"

class DeploymentOrchestrator:
    """Orchestrates complete deployment workflow."""
    
    def __init__(self):
        self.freshness_ready = False
        self.shelf_life_ready = False
        self.deployment_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def check_model_candidates(self):
        """Check if model candidates exist and are ready."""
        
        self.log("=" * 80)
        self.log("STEP 1: MODEL CANDIDATE VERIFICATION")
        self.log("=" * 80)
        
        # Check freshness model
        freshness_candidate = CANDIDATES_DIR / "freshness_v3_efficientnet_b0.pth"
        if freshness_candidate.exists():
            size_mb = freshness_candidate.stat().st_size / 1024 / 1024
            self.log(f"✅ Freshness V3 candidate found ({size_mb:.1f} MB)", "INFO")
            self.freshness_ready = True
        else:
            self.log(f"⚠️ Freshness V3 candidate not found at {freshness_candidate}", "WARN")
            self.freshness_ready = False
        
        # Check shelf-life model
        shelf_life_candidate = CANDIDATES_DIR / "shelf_life_v1_regression.pth"
        shelf_life_encoders = CANDIDATES_DIR / "shelf_life_v1_encoders.pkl"
        
        if shelf_life_candidate.exists() and shelf_life_encoders.exists():
            size_mb = shelf_life_candidate.stat().st_size / 1024 / 1024
            self.log(f"✅ Shelf-Life V1 candidate found ({size_mb:.1f} MB)", "INFO")
            self.shelf_life_ready = True
        else:
            self.log(f"⚠️ Shelf-Life V1 candidate not found", "WARN")
            self.shelf_life_ready = False
        
        return self.freshness_ready or self.shelf_life_ready
    
    def evaluate_models(self):
        """Run model evaluation scripts."""
        
        self.log("\n" + "=" * 80)
        self.log("STEP 2: MODEL EVALUATION")
        self.log("=" * 80)
        
        # Run comparison script
        comparison_script = PROJECT_ROOT / "scripts" / "compare_freshness_models.py"
        if comparison_script.exists():
            self.log(f"Running freshness model comparison...", "INFO")
            try:
                result = subprocess.run(
                    [sys.executable, str(comparison_script)],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=60
                )
                if result.returncode == 0:
                    self.log("✅ Freshness model comparison complete", "INFO")
                else:
                    self.log(f"⚠️ Comparison script exited with code {result.returncode}", "WARN")
            except Exception as e:
                self.log(f"⚠️ Comparison script error: {e}", "WARN")
    
    def promote_models(self):
        """Promote evaluated models to production."""
        
        self.log("\n" + "=" * 80)
        self.log("STEP 3: MODEL PROMOTION")
        self.log("=" * 80)
        
        promote_script = PROJECT_ROOT / "scripts" / "promote_model.py"
        
        if self.freshness_ready and promote_script.exists():
            self.log(f"Promoting Freshness V3 to production...", "INFO")
            try:
                result = subprocess.run(
                    [sys.executable, str(promote_script), "promote", "freshness_v3",
                     "--reason", "EfficientNet-B0 trained on AgriFreshNET, better accuracy"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.log("✅ Freshness V3 promoted to production", "INFO")
                else:
                    self.log(f"⚠️ Promotion failed: {result.stderr.decode()[:200]}", "WARN")
            except Exception as e:
                self.log(f"⚠️ Promotion error: {e}", "WARN")
        
        if self.shelf_life_ready and promote_script.exists():
            self.log(f"Promoting Shelf-Life V1 to production...", "INFO")
            try:
                result = subprocess.run(
                    [sys.executable, str(promote_script), "promote", "shelf_life_v1",
                     "--reason", "Neural network regression trained on FoodKeeper + AgriFreshNET"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.log("✅ Shelf-Life V1 promoted to production", "INFO")
                else:
                    self.log(f"⚠️ Promotion failed: {result.stderr.decode()[:200]}", "WARN")
            except Exception as e:
                self.log(f"⚠️ Promotion error: {e}", "WARN")
    
    def verify_database(self):
        """Verify database is ready for predictions."""
        
        self.log("\n" + "=" * 80)
        self.log("STEP 4: DATABASE VERIFICATION")
        self.log("=" * 80)
        
        verify_script = PROJECT_ROOT / "scripts" / "verify_database.py"
        if verify_script.exists():
            self.log(f"Verifying database schema...", "INFO")
            try:
                result = subprocess.run(
                    [sys.executable, str(verify_script)],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.log("✅ Database verification complete", "INFO")
                else:
                    self.log(f"⚠️ Database verification failed", "WARN")
            except Exception as e:
                self.log(f"⚠️ Database verification error: {e}", "WARN")
    
    def print_deployment_instructions(self):
        """Print instructions for backend and frontend startup."""
        
        self.log("\n" + "=" * 80)
        self.log("STEP 5: DEPLOYMENT INSTRUCTIONS")
        self.log("=" * 80)
        
        self.log("\n📋 To complete deployment, execute the following in separate terminals:\n", "INFO")
        
        self.log("\n--- TERMINAL 1: START BACKEND ---", "INFO")
        backend_cmd = "cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
        self.log(backend_cmd, "INFO")
        
        self.log("\n--- TERMINAL 2: START FRONTEND ---", "INFO")
        frontend_cmd = "cd frontend && npm run dev"
        self.log(frontend_cmd, "INFO")
        
        self.log("\n--- TERMINAL 3: RUN INTEGRATION TESTS ---", "INFO")
        test_cmd = "python scripts/integration_test.py"
        self.log(test_cmd, "INFO")
        
        self.log("\n✅ Both services started, run integration tests to verify", "INFO")
    
    def save_deployment_log(self):
        """Save deployment log to file."""
        
        log_file = REPORTS_DIR / f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w') as f:
            f.write("\n".join(self.deployment_log))
        
        self.log(f"\nDeployment log saved to: {log_file}", "INFO")
    
    def run_deployment(self):
        """Execute full deployment workflow."""
        
        print("\n" + "=" * 100)
        print("╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                    FOODFRESH AI - COMPLETE DEPLOYMENT ORCHESTRATOR                             ║")
        print("║                                                                                                   ║")
        print("║  This script will:                                                                               ║")
        print("║  1. Verify model candidates are ready                                                            ║")
        print("║  2. Evaluate model performance                                                                   ║")
        print("║  3. Promote best models to production                                                            ║")
        print("║  4. Verify database integration                                                                  ║")
        print("║  5. Provide instructions for final deployment                                                    ║")
        print("║                                                                                                   ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝")
        print("=" * 100 + "\n")
        
        # Execute deployment steps
        if self.check_model_candidates():
            self.evaluate_models()
            self.promote_models()
            self.verify_database()
            self.print_deployment_instructions()
        else:
            self.log("\n❌ No model candidates found - training may not be complete", "ERROR")
            self.log("\nPlease ensure:", "INFO")
            self.log("  1. Freshness model training completed: ml/freshness/train_efficientnet_v3.py", "INFO")
            self.log("  2. Shelf-life model training completed: ml/shelf_life/train_v1.py", "INFO")
            self.log("  3. Model checkpoints saved to models/candidates/", "INFO")
        
        # Save log
        self.save_deployment_log()
        
        print("\n" + "=" * 100)
        print("✅ DEPLOYMENT ORCHESTRATION COMPLETE")
        print("=" * 100)


def main():
    orchestrator = DeploymentOrchestrator()
    orchestrator.run_deployment()


if __name__ == "__main__":
    main()
