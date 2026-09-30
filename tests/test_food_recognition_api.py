"""
FoodFresh AI - Backend Integration Tests for Master Hybrid Vision API
Verifies:
1. Health check endpoint (/api/health)
2. Hybrid vision prediction endpoint (/api/food-recognition/predict)
3. Error handling for empty or invalid images
4. Real-world inference on Pomegranate, Apple, Orange
5. Schema compliance: detectedFood, recognitionConfidence, topPredictions, detectedObjects,
   foodRecognition (groundingDino, rawFoodResNet, siglip2), freshness, shelfLife, modelVersions.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app


class TestHybridVisionAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.eval_dir = PROJECT_ROOT / "data" / "real_world_eval"
        cls.pom_img_path = cls.eval_dir / "pomegranate.jpg"
        cls.apple_img_path = cls.eval_dir / "apple.jpg"
        cls.orange_img_path = cls.eval_dir / "orange.jpg"

    def test_01_health_check(self):
        """GET /api/health must return 200 OK."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")

    def test_02_predict_endpoint_rejects_empty_file(self):
        """POST /api/food-recognition/predict with empty file returns 400."""
        files = {"file": ("empty.jpg", b"", "image/jpeg")}
        response = self.client.post("/api/food-recognition/predict", files=files)
        self.assertEqual(response.status_code, 400)

    def test_03_predict_endpoint_rejects_corrupted_image(self):
        """POST /api/food-recognition/predict with non-image bytes returns 400 invalid_image."""
        files = {"file": ("fake.jpg", b"not-a-real-jpeg-image-bytes", "image/jpeg")}
        response = self.client.post("/api/food-recognition/predict", files=files)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("status"), "invalid_image")

    def test_04_predict_real_pomegranate_image(self):
        """POST /api/food-recognition/predict with real pomegranate image runs hybrid inference."""
        if not self.pom_img_path.exists():
            self.skipTest("No pomegranate test image found")

        with open(self.pom_img_path, "rb") as f:
            img_bytes = f.read()

        files = {"file": (self.pom_img_path.name, img_bytes, "image/jpeg")}
        response = self.client.post("/api/food-recognition/predict", files=files)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data.get("success"), "Expected success: True")
        self.assertEqual(data.get("analysisStatus"), "success")
        self.assertEqual(data.get("detectedFood"), "Pomegranate")
        self.assertGreater(data.get("recognitionConfidence", 0), 80.0)

        # Schema keys verification
        self.assertIn("topPredictions", data)
        self.assertIn("detectedObjects", data)
        self.assertIn("foodRecognition", data)
        self.assertIn("freshness", data)
        self.assertIn("shelfLife", data)
        self.assertIn("modelVersions", data)

        # Freshness verification
        freshness = data["freshness"]
        self.assertEqual(freshness.get("status"), "success")
        self.assertIn(freshness.get("label"), ["Fresh", "Slightly Spoiled", "Rotten"])
        self.assertIsInstance(freshness.get("score"), (int, float))

        # Shelf life verification
        shelf_life = data["shelfLife"]
        self.assertEqual(shelf_life.get("status"), "not_available")

        # Model versions verification
        versions = data["modelVersions"]
        self.assertIn("grounding-dino-base", versions.get("detector", ""))
        self.assertIn("siglip2", versions.get("foodSemantic", ""))
        self.assertIn("raw-food-recognition-models", versions.get("foodSpecialist", ""))
        self.assertIn("food-freshness-detector", versions.get("freshness", ""))

        print(f"\n[API TEST] Real Pomegranate Inference Result:")
        print(f"  Detected Food: {data.get('detectedFood')} ({data.get('recognitionConfidence')}%)")
        print(f"  Freshness:     {freshness.get('label')} ({freshness.get('score')}%)")
        print(f"  Shelf-Life:    {shelf_life.get('status')}")

    def test_05_predict_real_apple_image(self):
        """POST /api/food-recognition/predict with real apple image runs hybrid inference."""
        if not self.apple_img_path.exists():
            self.skipTest("No apple test image found")

        with open(self.apple_img_path, "rb") as f:
            img_bytes = f.read()

        files = {"file": (self.apple_img_path.name, img_bytes, "image/jpeg")}
        response = self.client.post("/api/food-recognition/predict", files=files)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data.get("success"), "Expected success: True")
        self.assertEqual(data.get("analysisStatus"), "success")
        self.assertEqual(data.get("detectedFood"), "Apple")
        self.assertGreater(data.get("recognitionConfidence", 0), 50.0)

        print(f"\n[API TEST] Real Apple Inference Result:")
        print(f"  Detected Food: {data.get('detectedFood')} ({data.get('recognitionConfidence')}%)")
        print(f"  Freshness:     {data.get('freshness', {}).get('label')}")


if __name__ == "__main__":
    unittest.main()
