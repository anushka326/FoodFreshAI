#!/usr/bin/env python
"""
Model Promotion Utility
Promotes trained model candidates to production after evaluation.
Updates model_config.py and backend configuration.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
TRAINED_DIR = PROJECT_ROOT / "models" / "trained"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODEL_CONFIG_PATH = PROJECT_ROOT / "backend" / "app" / "model_config.py"

# Model definitions
MODELS = {
    'freshness_v3': {
        'candidate_file': CANDIDATES_DIR / "freshness_v3_efficientnet_b0.pth",
        'trained_file': TRAINED_DIR / "freshness_v3.pth",
        'config_key': 'food_freshness',
        'version': 'v3',
        'description': 'EfficientNet-B0 trained on AgriFreshNET (9,856 train images)'
    },
    'shelf_life_v1': {
        'candidate_file': CANDIDATES_DIR / "shelf_life_v1_regression.pth",
        'trained_file': TRAINED_DIR / "shelf_life_v1.pth",
        'config_key': 'shelf_life',
        'version': 'v1',
        'description': 'Neural network regression on FoodKeeper + AgriFreshNET'
    }
}


def promote_model(model_name: str, reason: str = ""):
    """Promote a model candidate to production."""
    
    print("=" * 80)
    print(f"MODEL PROMOTION: {model_name}")
    print("=" * 80)
    
    if model_name not in MODELS:
        print(f"❌ Unknown model: {model_name}")
        print(f"Available models: {list(MODELS.keys())}")
        return False
    
    model_config = MODELS[model_name]
    candidate_file = model_config['candidate_file']
    trained_file = model_config['trained_file']
    
    # Verify candidate exists
    if not candidate_file.exists():
        print(f"❌ Candidate model not found: {candidate_file}")
        return False
    
    print(f"\n📋 Model Config:")
    print(f"  Candidate: {candidate_file.name}")
    print(f"  Target:    {trained_file.name}")
    print(f"  Version:   {model_config['version']}")
    print(f"  Description: {model_config['description']}")
    if reason:
        print(f"  Reason:    {reason}")
    
    # Backup existing model if it exists
    if trained_file.exists():
        backup_file = trained_file.with_stem(f"{trained_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        print(f"\n🔄 Backing up current model...")
        shutil.copy2(trained_file, backup_file)
        print(f"  Backed up to: {backup_file.name}")
    
    # Copy candidate to trained directory
    print(f"\n📂 Copying candidate to trained directory...")
    trained_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate_file, trained_file)
    print(f"  ✅ Copied to: {trained_file}")
    
    # Update model_config.py
    print(f"\n⚙️ Updating model_config.py...")
    update_model_config(model_name, model_config)
    
    # Create promotion log
    log_file = REPORTS_DIR / f"{model_name}_promotion_log.md"
    with open(log_file, 'w') as f:
        f.write(f"# {model_name.upper()} Promotion Log\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"## Promotion Details\n\n")
        f.write(f"- **Model:** {model_name}\n")
        f.write(f"- **Version:** {model_config['version']}\n")
        f.write(f"- **Description:** {model_config['description']}\n")
        if reason:
            f.write(f"- **Reason:** {reason}\n")
        f.write(f"\n## Files Updated\n\n")
        f.write(f"- Copied: {candidate_file} → {trained_file}\n")
        if trained_file.with_stem(f"{trained_file.stem}_backup_*").exists():
            f.write(f"- Backed up: Current model to backup file\n")
        f.write(f"- Updated: {MODEL_CONFIG_PATH}\n")
    
    print(f"  Promotion log: {log_file}")
    
    print("\n" + "=" * 80)
    print("✅ Model promotion complete!")
    print("=" * 80)
    
    return True


def update_model_config(model_name: str, model_config: dict):
    """Update model_config.py with new model version."""
    
    # Read current config
    with open(MODEL_CONFIG_PATH) as f:
        config_content = f.read()
    
    # Create config update
    if model_name == 'freshness_v3':
        old_line = "    'model_version': 'v2',"
        new_line = "    'model_version': 'v3',"
        config_content = config_content.replace(old_line, new_line)
        
        old_path = "    'checkpoint_path': 'models/trained/freshness_model_v2.pth',"
        new_path = "    'checkpoint_path': 'models/trained/freshness_v3.pth',"
        config_content = config_content.replace(old_path, new_path)
        
        print(f"  Updated freshness model version to v3")
    
    elif model_name == 'shelf_life_v1':
        old_line = "'status': 'AWAITING_INTEGRATION',"
        new_line = "'status': 'ACTIVE',"
        config_content = config_content.replace(old_line, new_line)
        
        old_version = "    'model_version': 'v0_heuristic',"
        new_version = "    'model_version': 'v1',"
        config_content = config_content.replace(old_version, new_version)
        
        old_path = "    'checkpoint_path': None,"
        new_path = "    'checkpoint_path': 'models/trained/shelf_life_v1.pth',"
        config_content = config_content.replace(old_path, new_path)
        
        print(f"  Updated shelf_life model to v1 and set status to ACTIVE")
    
    # Write updated config
    with open(MODEL_CONFIG_PATH, 'w') as f:
        f.write(config_content)
    
    print(f"  ✅ Updated {MODEL_CONFIG_PATH}")


def verify_promotion(model_name: str):
    """Verify a model was successfully promoted."""
    
    if model_name not in MODELS:
        return False
    
    model_config = MODELS[model_name]
    trained_file = model_config['trained_file']
    
    if not trained_file.exists():
        print(f"❌ Trained model not found: {trained_file}")
        return False
    
    print(f"✅ {model_name} is in production at: {trained_file}")
    return True


def rollback_model(model_name: str):
    """Rollback a model to the previous backup."""
    
    print("=" * 80)
    print(f"MODEL ROLLBACK: {model_name}")
    print("=" * 80)
    
    if model_name not in MODELS:
        print(f"❌ Unknown model: {model_name}")
        return False
    
    model_config = MODELS[model_name]
    trained_file = model_config['trained_file']
    
    # Find most recent backup
    parent_dir = trained_file.parent
    backups = sorted(parent_dir.glob(f"{trained_file.stem}_backup_*.pth"), reverse=True)
    
    if not backups:
        print(f"❌ No backup found for {model_name}")
        return False
    
    latest_backup = backups[0]
    print(f"\n🔄 Restoring from backup: {latest_backup.name}")
    
    shutil.copy2(latest_backup, trained_file)
    print(f"✅ Restored: {trained_file}")
    
    # Note: In production, would need to also revert model_config.py
    print("\n⚠️ Note: model_config.py was not automatically reverted")
    print("       Manual review may be needed for config rollback")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Promotion Utility")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote a model candidate to production')
    promote_parser.add_argument('model', choices=list(MODELS.keys()), help='Model to promote')
    promote_parser.add_argument('--reason', default='', help='Reason for promotion')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a model is in production')
    verify_parser.add_argument('model', choices=list(MODELS.keys()), help='Model to verify')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback a model to previous version')
    rollback_parser.add_argument('model', choices=list(MODELS.keys()), help='Model to rollback')
    
    # List command
    subparsers.add_parser('list', help='List available models')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'promote':
        promote_model(args.model, args.reason)
    elif args.command == 'verify':
        verify_promotion(args.model)
    elif args.command == 'rollback':
        rollback_model(args.model)
    elif args.command == 'list':
        print("\nAvailable Models:")
        print("=" * 80)
        for model_name, config in MODELS.items():
            print(f"\n{model_name}:")
            print(f"  Version: {config['version']}")
            print(f"  Description: {config['description']}")
            print(f"  Candidate: {config['candidate_file']}")
            print(f"  Production: {config['trained_file']}")


if __name__ == "__main__":
    main()
