"""
FoodFresh AI - Food Recognition Package
Exports model architecture, dataset loader, transform pipelines, and prediction wrappers.
"""

from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import FoodRecognitionDataset, create_data_loaders
from ml.food_recognition.evaluate import evaluate_food_recognition_model
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.predict import FoodPredictor, predict_food
from ml.food_recognition.train import run_training
from ml.food_recognition.transforms import get_transforms
from ml.food_recognition.utils import count_parameters, get_device, load_label_map, set_seed

__all__ = [
    "FoodRecognitionConfig",
    "FoodRecognitionDataset",
    "create_data_loaders",
    "get_transforms",
    "create_food_recognition_model",
    "run_training",
    "evaluate_food_recognition_model",
    "FoodPredictor",
    "predict_food",
    "set_seed",
    "get_device",
    "load_label_map",
    "count_parameters"
]
