"""
FoodFresh AI - Unit / Smoke Tests for Food Recognition Pipeline
Tests dataset loading, transforms, label maps, and model construction WITHOUT pretrained weights.
"""

import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
from ml.food_recognition.config import FoodRecognitionConfig
from ml.food_recognition.dataset import FoodRecognitionDataset
from ml.food_recognition.model import create_food_recognition_model
from ml.food_recognition.transforms import get_transforms
from ml.food_recognition.utils import load_label_map, set_seed


class TestFoodRecognitionPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_seed(42)
        cls.config = FoodRecognitionConfig()
        cls.train_transform, cls.eval_transform = get_transforms(image_size=cls.config.image_size)

    def test_01_label_map_loads_correctly(self):
        """Verify label_map.json loads with expected class count and bijection."""
        self.assertTrue(self.config.label_map_path.exists(), "label_map.json does not exist")
        food_to_id, id_to_food, num_classes = load_label_map(self.config.label_map_path)

        self.assertEqual(num_classes, 12, "Expected exactly 12 classes in label_map.json")
        self.assertEqual(len(food_to_id), 12)
        self.assertEqual(len(id_to_food), 12)

        # Check bidirectional consistency
        for food, idx in food_to_id.items():
            self.assertEqual(id_to_food[str(idx)], food, f"Mismatch in bidirectional mapping for {food}")

    def test_02_train_manifest_loads(self):
        """Verify train manifest exists and has expected minimum rows."""
        self.assertTrue(self.config.train_manifest_path.exists(), "Train manifest CSV missing")
        dataset = FoodRecognitionDataset(self.config.train_manifest_path, transform=self.eval_transform)
        self.assertGreater(len(dataset), 60000, "Train dataset should contain over 60,000 samples")

    def test_03_test_manifest_loads(self):
        """Verify test manifest exists and has expected minimum rows."""
        self.assertTrue(self.config.test_manifest_path.exists(), "Test manifest CSV missing")
        dataset = FoodRecognitionDataset(self.config.test_manifest_path, transform=self.eval_transform)
        self.assertGreater(len(dataset), 20000, "Test dataset should contain over 20,000 samples")

    def test_04_dataset_returns_tensor_and_int_label(self):
        """Verify __getitem__ returns (torch.Tensor, int)."""
        dataset = FoodRecognitionDataset(self.config.train_manifest_path, transform=self.eval_transform)
        img_tensor, label_id = dataset[0]

        self.assertIsInstance(img_tensor, torch.Tensor, "Dataset item[0] must be torch.Tensor")
        self.assertIsInstance(label_id, int, "Dataset item[1] must be integer label")

    def test_05_tensor_channels_and_shape(self):
        """Verify image tensor has 3 channels and expected shape (3, 224, 224)."""
        dataset = FoodRecognitionDataset(self.config.train_manifest_path, transform=self.eval_transform)
        img_tensor, _ = dataset[0]

        self.assertEqual(img_tensor.ndim, 3, "Tensor should be 3-dimensional (C, H, W)")
        self.assertEqual(img_tensor.shape[0], 3, "Tensor must have 3 channels (RGB)")
        self.assertEqual(img_tensor.shape[1], 224, "Tensor height must be 224")
        self.assertEqual(img_tensor.shape[2], 224, "Tensor width must be 224")

    def test_06_labels_within_expected_range(self):
        """Verify sampled labels are within [0, num_classes - 1]."""
        dataset = FoodRecognitionDataset(self.config.train_manifest_path, transform=None)
        # Sample first 100 samples
        for i in range(min(100, len(dataset))):
            _, label_id = dataset[i]
            self.assertTrue(0 <= label_id < self.config.num_classes, f"Label {label_id} out of range [0, {self.config.num_classes - 1}]")

    def test_07_model_factory_constructs_without_pretrained_weights(self):
        """Verify create_food_recognition_model(pretrained=False) constructs architecture without downloads."""
        model = create_food_recognition_model(num_classes=12, pretrained=False)

        self.assertIsInstance(model, nn.Module)
        self.assertEqual(model.classifier[1].out_features, 12, "Model output classes must equal 12")

        # Test forward pass with dummy batch
        dummy_input = torch.randn(2, 3, 224, 224)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 12), "Forward pass output shape must be (2, 12)")

    def test_08_trained_checkpoint_exists_and_is_valid(self):
        """Verify food_classifier.pth exists and contains valid metadata and state dict."""
        ckpt_path = self.config.checkpoint_path
        self.assertTrue(ckpt_path.exists(), f"Expected trained checkpoint at {ckpt_path}")
        checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        self.assertIn("model_state_dict", checkpoint)
        self.assertIn("food_to_id", checkpoint)
        self.assertEqual(checkpoint["num_classes"], 12)
        self.assertGreater(checkpoint.get("best_val_accuracy", 0.0), 90.0)


if __name__ == "__main__":
    unittest.main()
