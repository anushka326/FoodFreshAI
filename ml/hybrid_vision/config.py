"""
FoodFresh AI - Hybrid Vision Configuration
Defines model paths, hugging face identifiers, device settings, and fusion thresholds.
"""

from pathlib import Path
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ML_DIR = PROJECT_ROOT / "ml"
HYBRID_VISION_DIR = ML_DIR / "hybrid_vision"
MODELS_DIR = PROJECT_ROOT / "models" / "pretrained"

# Device selection: Use CUDA if available, fallback to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model Repositories and Local Paths
GROUNDING_DINO_REPO = "IDEA-Research/grounding-dino-base"
GROUNDING_DINO_DIR = MODELS_DIR / "grounding_dino"

SIGLIP2_REPO = "google/siglip2-base-patch16-224"
SIGLIP2_DIR = MODELS_DIR / "siglip2"

RAW_FOOD_REPO = "ibrahimdaud/raw-food-recognition-models"
RAW_FOOD_DIR = MODELS_DIR / "raw_food_resnet50"
RAW_FOOD_WEIGHTS = RAW_FOOD_DIR / "resnet50_pytorch_model.bin"
RAW_FOOD_CLASSES = RAW_FOOD_DIR / "classes.json"

FRESHNESS_REPO = "nathansekar/food-freshness-detector"
FRESHNESS_DIR = MODELS_DIR / "freshness_resnet18"
FRESHNESS_WEIGHTS = FRESHNESS_DIR / "model_weights.pth"
FRESHNESS_CONFIG = FRESHNESS_DIR / "config.json"
FRESHNESS_VOCAB = FRESHNESS_DIR / "vocab.json"

FOOD_VOCABULARY_PATH = HYBRID_VISION_DIR / "food_vocabulary.json"

# Grounding DINO detection queries and thresholds
# Combines controlled scene objects (Phase 7) with primary food queries
GROUNDING_DINO_TEXT_PROMPT = (
    "table. countertop. plate. bowl. spoon. fork. knife. glass. cup. tray. container. "
    "basket. cutting board. bag. apple. banana. pomegranate. tomato. orange. mango. "
    "carrot. potato. onion. cucumber. pepper. bread. food. grape. chickoo. sapodilla. "
    "papaya. pineapple. watermelon. guava. lemon. avocado. kiwi. strawberry. peach."
)
GROUNDING_DINO_BOX_THRESHOLD = 0.22
GROUNDING_DINO_TEXT_THRESHOLD = 0.22

# Food crop expansion margin (expand bounding box slightly for context)
CROP_MARGIN_RATIO = 0.08

# Uncertainty & Fusion thresholds
HIGH_CONFIDENCE_THRESHOLD = 70.0  # Percentage
MODERATE_CONFIDENCE_THRESHOLD = 45.0  # Percentage
UNCERTAINTY_TOP_GAP = 15.0  # If top 1 and top 2 are within 15% and disagree -> uncertain
MIN_VALID_CONFIDENCE = 30.0  # Below this, label marked uncertain
