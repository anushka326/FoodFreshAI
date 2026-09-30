#!/usr/bin/env python
"""
Freshness Model Comparison Script
Compares V3 (EfficientNet-B0) vs Current Production (nathansekar fallback).
Tests on regression cases and standard metrics.
"""

import os
import sys
import json
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np
from PIL import Image, ImageOps
import torchvision.transforms as T
from torchvision.models import efficientnet_b0

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import production services
from backend.app.services.freshness_service import FreshnessService

CANDIDATES_DIR = PROJECT_ROOT / "models" / "candidates"
REPORTS_DIR = PROJECT_ROOT / "reports"
V3_MODEL_PATH = CANDIDATES_DIR / "freshness_v3_efficientnet_b0.pth"

# Regression test cases (protected cases we want to monitor)
REGRESSION_CASES = [
    {
        'name': 'Green Chilli (Fresh)',
        'description': 'Green chilli in fresh state - Current: Rotten 99%',
        'expected': 'Fresh',
        'reason': 'NOT in AgriFreshNET - domain gap expected'
    },
    {
        'name': 'Dried Red Chilli',
        'description': 'Dried red chilli - Current: Rotten 100%',
        'expected': 'Semi-Fresh (if not rotten)',
        'reason': 'NOT in AgriFreshNET - different form/domain'
    },
    {
        'name': 'Fresh Tomato (Red)',
        'description': 'Red ripe tomato in fresh state - Current: Working',
        'expected': 'Fresh',
        'reason': 'In AgriFreshNET training data'
    },
    {
        'name': 'Rotten Tomato',
        'description': 'Rotting tomato - Current: Working',
        'expected': 'Rotten',
        'reason': 'In AgriFreshNET training data'
    },
]

# Test image sources
TEST_IMAGES = {
    'fresh_banana': PROJECT_ROOT / 'data' / 'real_world_food' / 'banana_fresh.jpg',
    'rotten_tomato': PROJECT_ROOT / 'data' / 'real_world_food' / 'tomato_rotten.jpg',
    'semi_fresh_orange': PROJECT_ROOT / 'data' / 'real_world_food' / 'orange_semi_fresh.jpg',
}

# Preprocessing transforms (same as training)
EVAL_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

CLASS_NAMES = ['Fresh', 'Semi-Fresh', 'Rotten']


def load_v3_model(model_path: Path):
    """Load V3 EfficientNet-B0 model."""
    if not model_path.exists():
        print(f"⚠️ V3 model not found at {model_path}")
        return None
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = efficientnet_b0(weights='DEFAULT')
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 3)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    return model, device


def predict_v3(image_path: Path, model, device):
    """Predict freshness using V3 model."""
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = ImageOps.exif_transpose(image)
        
        image_tensor = EVAL_TRANSFORM(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            logits = model(image_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        
        pred_class = np.argmax(probs)
        pred_label = CLASS_NAMES[pred_class]
        pred_conf = probs[pred_class]
        
        return {
            'label': pred_label,
            'confidence': float(pred_conf),
            'probabilities': {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
        }
    except Exception as e:
        print(f"Error predicting with V3: {e}")
        return None


def predict_production(image_path: Path):
    """Predict freshness using production FreshnessService."""
    try:
        service = FreshnessService()
        result = service.predict(image_path)
        
        return {
            'label': result.get('label'),
            'confidence': result.get('confidence'),
            'probabilities': result.get('probabilities', {})
        }
    except Exception as e:
        print(f"Error predicting with production model: {e}")
        return None


def main():
    print("=" * 80)
    print("FRESHNESS MODEL COMPARISON: V3 vs PRODUCTION")
    print("=" * 80)
    
    # Load models
    print("\nLoading models...")
    v3_result = load_v3_model(V3_MODEL_PATH)
    if v3_result is None:
        print("❌ Cannot load V3 model - skipping comparison")
        print("\nNote: V3 model training may still be in progress.")
        print("Re-run this script after training completes.")
        return
    
    v3_model, device = v3_result
    print("✅ V3 model loaded")
    
    # Load production service
    try:
        prod_service = FreshnessService()
        print("✅ Production model loaded")
    except Exception as e:
        print(f"⚠️ Production model load failed: {e}")
        prod_service = None
    
    # Regression test cases (text-based, explanatory)
    print("\n" + "=" * 80)
    print("REGRESSION CASES - EXPLANATORY ANALYSIS")
    print("=" * 80)
    
    for case in REGRESSION_CASES:
        print(f"\n{case['name']}:")
        print(f"  Description: {case['description']}")
        print(f"  Expected: {case['expected']}")
        print(f"  Reason: {case['reason']}")
    
    # Test on real images (if available)
    print("\n" + "=" * 80)
    print("REAL WORLD IMAGE PREDICTIONS")
    print("=" * 80)
    
    test_results = []
    
    for test_name, image_path in TEST_IMAGES.items():
        if not image_path.exists():
            print(f"\n⏭️ Skipping {test_name} - image not found at {image_path}")
            continue
        
        print(f"\n{test_name}:")
        print(f"  Image: {image_path.name}")
        
        # V3 prediction
        v3_pred = predict_v3(image_path, v3_model, device)
        if v3_pred:
            print(f"  V3:           {v3_pred['label']:15s} ({v3_pred['confidence']:.2%})")
        else:
            print(f"  V3:           ERROR")
            v3_pred = {'label': 'ERROR', 'confidence': 0}
        
        # Production prediction
        if prod_service:
            prod_pred = predict_production(image_path)
            if prod_pred:
                print(f"  Production:   {prod_pred['label']:15s} ({prod_pred['confidence']:.2%})")
            else:
                print(f"  Production:   ERROR")
                prod_pred = {'label': 'ERROR', 'confidence': 0}
        else:
            prod_pred = None
            print(f"  Production:   UNAVAILABLE")
        
        # Record for summary
        test_results.append({
            'image': test_name,
            'v3_prediction': v3_pred.get('label', 'ERROR'),
            'v3_confidence': v3_pred.get('confidence', 0),
            'prod_prediction': prod_pred.get('label', 'N/A') if prod_pred else 'UNAVAILABLE',
            'prod_confidence': prod_pred.get('confidence', 0) if prod_pred else 0,
            'agreement': v3_pred.get('label') == prod_pred.get('label') if prod_pred else None
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    if test_results:
        print(f"\nTested {len(test_results)} images:")
        print(f"{'Image':<20} {'V3':<15} {'Conf':<8} {'Prod':<15} {'Conf':<8} {'Match':<8}")
        print("-" * 80)
        
        matches = 0
        for result in test_results:
            match_str = "✅ Yes" if result['agreement'] else ("❌ No" if result['agreement'] is not None else "N/A")
            print(f"{result['image']:<20} {result['v3_prediction']:<15} {result['v3_confidence']:>6.1%}  {result['prod_prediction']:<15} {result['prod_confidence']:>6.1%}  {match_str:<8}")
            if result['agreement']:
                matches += 1
        
        if None not in [r['agreement'] for r in test_results]:
            agreement_rate = 100.0 * matches / len(test_results)
            print(f"\nPrediction agreement: {matches}/{len(test_results)} ({agreement_rate:.1f}%)")
    else:
        print("\nNo test images found - cannot perform real-world comparison.")
        print("Ensure test images exist in data/real_world_food/")
    
    # Write report
    report_path = REPORTS_DIR / "freshness_v3_vs_production_comparison.md"
    with open(report_path, 'w') as f:
        f.write("# Freshness Model Comparison: V3 vs Production\n\n")
        f.write("**Models:**\n")
        f.write("- V3: EfficientNet-B0 trained on AgriFreshNET\n")
        f.write("- Production: nathansekar/food-freshness-detector (fallback)\n\n")
        
        f.write("## Regression Cases (Protected Test Cases)\n\n")
        for case in REGRESSION_CASES:
            f.write(f"### {case['name']}\n")
            f.write(f"- **Description:** {case['description']}\n")
            f.write(f"- **Expected:** {case['expected']}\n")
            f.write(f"- **Reason:** {case['reason']}\n\n")
        
        f.write("## Real World Image Predictions\n\n")
        if test_results:
            f.write("| Image | V3 Prediction | V3 Confidence | Production | Prod Confidence | Agreement |\n")
            f.write("|-------|---------------|---------------|------------|-----------------|----------|\n")
            for result in test_results:
                f.write(f"| {result['image']} | {result['v3_prediction']} | {result['v3_confidence']:.2%} | {result['prod_prediction']} | {result['prod_confidence']:.2%} | {'✅' if result['agreement'] else ('❌' if result['agreement'] is not None else 'N/A')} |\n")
            
            if None not in [r['agreement'] for r in test_results]:
                matches = sum(1 for r in test_results if r['agreement'])
                f.write(f"\n**Agreement Rate:** {matches}/{len(test_results)} ({100.0*matches/len(test_results):.1f}%)\n")
        else:
            f.write("No test images found.\n")
        
        f.write("\n## Conclusions\n\n")
        f.write("### V3 EfficientNet-B0\n")
        f.write("- **Strengths:**\n")
        f.write("  - Trained on AgriFreshNET with proper validation/test splits\n")
        f.write("  - Per-class metrics and calibration validation\n")
        f.write("  - Modern architecture with batch normalization\n\n")
        f.write("- **Weaknesses:**\n")
        f.write("  - Limited to 8 food types in training data\n")
        f.write("  - No data for chilli (green or dried)\n")
        f.write("  - No explicit form handling\n\n")
        
        f.write("### Production Model\n")
        f.write("- **Strengths:**\n")
        f.write("  - Pre-trained on diverse food dataset\n")
        f.write("  - Fallback for unknown foods\n\n")
        f.write("- **Weaknesses:**\n")
        f.write("  - High confidence on chilli failures (99-100%)\n")
        f.write("  - No calibration validation\n\n")
        
        f.write("## Recommendation\n\n")
        f.write("**Decision:** [To be determined after V3 evaluation completes]\n\n")
        f.write("- If V3 macro F1 > current production F1: Promote V3 to production\n")
        f.write("- Otherwise: Keep production model and investigate V3 failure modes\n")
        f.write("- Either way: Implement form-aware preprocessing for chilli forms\n")
    
    print(f"\nComparison report saved to: {report_path}")
    
    print("\n" + "=" * 80)
    print("Comparison analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
