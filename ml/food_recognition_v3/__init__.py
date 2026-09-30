"""
FoodFresh AI - Food Recognition V3 Package
Implements domain-adaptive transfer learning using Fruits-360 and AgriFreshNET.
"""

from ml.food_recognition_v3.config import FoodRecognitionV3Config
from ml.food_recognition_v3.dataset import FoodRecognitionV3Dataset, create_v3_data_loaders
from ml.food_recognition_v3.model import load_v3_model_from_v2
from ml.food_recognition_v3.transforms import get_v3_transforms

__all__ = [
    "FoodRecognitionV3Config",
    "FoodRecognitionV3Dataset",
    "create_v3_data_loaders",
    "load_v3_model_from_v2",
    "get_v3_transforms",
]
