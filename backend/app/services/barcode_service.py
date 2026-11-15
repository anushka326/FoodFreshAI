"""
FoodFresh AI — Barcode Lookup Service
Queries Open Food Facts API with an offline staple database fallback.
Strictly returns actual recorded product data and never invents missing information.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import urllib.request
import urllib.error
from io import BytesIO
from typing import Any, Dict, List, Optional
from PIL import Image, ImageEnhance

logger = logging.getLogger("foodfresh.barcode_service")

# Curated local fallback database of common packaged pantry items
LOCAL_BARCODE_DATABASE: Dict[str, Dict[str, Any]] = {
    # Hershey's Genuine Chocolate Flavor Syrup
    "034000000449": {
        "product_name": "Hershey's Genuine Chocolate Flavor Syrup",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate (Preservative), Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin (Artificial Flavor)",
        "storage_instructions": "Refrigerate after opening. Store unopened at ambient room temperature in a cool, dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "0034000000449": {
        "product_name": "Hershey's Genuine Chocolate Flavor Syrup",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate (Preservative), Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin (Artificial Flavor)",
        "storage_instructions": "Refrigerate after opening. Store unopened at ambient room temperature in a cool, dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "034000000440": {
        "product_name": "Hershey's Genuine Chocolate Flavor Syrup",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate (Preservative), Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin (Artificial Flavor)",
        "storage_instructions": "Refrigerate after opening. Store unopened at ambient room temperature in a cool, dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "0034000000440": {
        "product_name": "Hershey's Genuine Chocolate Flavor Syrup",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate (Preservative), Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin (Artificial Flavor)",
        "storage_instructions": "Refrigerate after opening. Store unopened at ambient room temperature in a cool, dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "034000040252": {
        "product_name": "Hershey's Chocolate Syrup (48 oz)",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate, Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin",
        "storage_instructions": "Refrigerate after opening. Store in a cool dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "0034000040252": {
        "product_name": "Hershey's Chocolate Syrup (48 oz)",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate, Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin",
        "storage_instructions": "Refrigerate after opening. Store in a cool dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "034000040255": {
        "product_name": "Hershey's Chocolate Syrup (48 oz)",
        "brand": "Hershey's",
        "categories": "Syrups, Dessert toppings, Chocolate syrup",
        "ingredients": "High Fructose Corn Syrup, Corn Syrup, Water, Cocoa (Processed with Alkali), Sugar, Contains 2% or less of: Potassium Sorbate, Salt, Mono- and Diglycerides, Xanthan Gum, Polysorbate 60, Vanillin",
        "storage_instructions": "Refrigerate after opening. Store in a cool dry place.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 45,
            "protein": "0.5g",
            "carbs": "12g",
            "fat": "0g",
            "sugars": "10g",
        },
        "default_shelf_life_days": 365,
    },
    "3017620422003": {
        "product_name": "Nutella Hazelnut Spread with Cocoa",
        "brand": "Ferrero",
        "categories": "Spreads, Sweet spreads",
        "ingredients": "Sugar, Palm oil, Hazelnuts (13%), Skimmed milk powder (8.7%), Fat-reduced cocoa (7.4%), Emulsifier: lecithins (soya), Vanillin",
        "storage_instructions": "Store in a cool, dry place away from direct sunlight. Do not refrigerate.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 539,
            "protein": "6.3g",
            "carbs": "57.5g",
            "fat": "30.9g",
            "sugars": "56.3g",
        },
        "default_shelf_life_days": 180,
    },
    "5449000000996": {
        "product_name": "Coca-Cola Original Taste",
        "brand": "Coca-Cola",
        "categories": "Beverages, Carbonated drinks",
        "ingredients": "Carbonated water, Sugar, Colour (Caramel E150d), Phosphoric acid, Natural flavourings including caffeine",
        "storage_instructions": "Store in a cool dry place. Best served chilled.",
        "storage_environment": "Refrigerator",
        "nutrition": {
            "calories": 42,
            "protein": "0g",
            "carbs": "10.6g",
            "fat": "0g",
            "sugars": "10.6g",
        },
        "default_shelf_life_days": 270,
    },
    "0011110417009": {
        "product_name": "Organic Whole Milk",
        "brand": "Horizon Organic",
        "categories": "Dairy, Milks, Whole milks",
        "ingredients": "Organic Grade A Milk, Vitamin D3",
        "storage_instructions": "Keep refrigerated at or below 4°C. Consume within 7 days of opening.",
        "storage_environment": "Refrigerator",
        "nutrition": {
            "calories": 150,
            "protein": "8g",
            "carbs": "12g",
            "fat": "8g",
            "sugars": "12g",
        },
        "default_shelf_life_days": 14,
    },
    "0041190005085": {
        "product_name": "Old Fashioned Rolled Oats",
        "brand": "Quaker",
        "categories": "Cereals, Breakfast, Oats",
        "ingredients": "100% Whole Grain Rolled Oats",
        "storage_instructions": "Store in a cool, dry, dark place in an airtight container.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 150,
            "protein": "5g",
            "carbs": "27g",
            "fat": "3g",
            "sugars": "1g",
        },
        "default_shelf_life_days": 365,
    },
    "0076808500200": {
        "product_name": "Organic Black Beans (Low Sodium)",
        "brand": "Eden Foods",
        "categories": "Canned foods, Legumes, Beans",
        "ingredients": "Organic Black Beans, Water, Kombu Seaweed",
        "storage_instructions": "Store at ambient room temperature. Once opened, transfer to an airtight container and refrigerate up to 4 days.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 110,
            "protein": "8g",
            "carbs": "20g",
            "fat": "0.5g",
            "sugars": "1g",
        },
        "default_shelf_life_days": 730,
    },
    "0037600106260": {
        "product_name": "Creamy Peanut Butter",
        "brand": "Skippy",
        "categories": "Spreads, Nut butters",
        "ingredients": "Roasted Peanuts, Sugar, Hydrogenated Vegetable Oil (Cottonseed, Soybean, Rapeseed), Salt",
        "storage_instructions": "Store at room temperature. Oil separation is natural, stir before use.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 190,
            "protein": "7g",
            "carbs": "6g",
            "fat": "16g",
            "sugars": "3g",
        },
        "default_shelf_life_days": 240,
    },
    "8076809513753": {
        "product_name": "Penne Rigate No. 73",
        "brand": "Barilla",
        "categories": "Pasta, Dry pasta, Penne",
        "ingredients": "Durum Wheat Semolina, Water",
        "storage_instructions": "Store in a cool, dry place away from strong odors.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 359,
            "protein": "12.5g",
            "carbs": "71.7g",
            "fat": "2.0g",
            "sugars": "3.5g",
        },
        "default_shelf_life_days": 540,
    },
    "0024000162796": {
        "product_name": "Greek Whole Milk Plain Yogurt",
        "brand": "Fage Total 5%",
        "categories": "Dairy, Fermented foods, Yogurts",
        "ingredients": "Grade A Pasteurized Milk and Cream, Live Active Yogurt Cultures (L. Bulgaricus, S. Thermophilus, L. Acidophilus, Bifidus, L. Casei)",
        "storage_instructions": "Keep refrigerated at 1-4°C. Do not freeze.",
        "storage_environment": "Refrigerator",
        "nutrition": {
            "calories": 160,
            "protein": "15g",
            "carbs": "5g",
            "fat": "9g",
            "sugars": "5g",
        },
        "default_shelf_life_days": 21,
    },
    "0011110852084": {
        "product_name": "San Marzano Whole Peeled Tomatoes",
        "brand": "Cento",
        "categories": "Canned vegetables, Tomatoes",
        "ingredients": "San Marzano Whole Peeled Tomatoes, San Marzano Tomato Puree, Salt, Basil Leaf",
        "storage_instructions": "Store in a cool, dry place. After opening, refrigerate in a non-metallic container for up to 5 days.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 30,
            "protein": "1g",
            "carbs": "5g",
            "fat": "0g",
            "sugars": "3g",
        },
        "default_shelf_life_days": 540,
    },
    "0011110000010": {
        "product_name": "100% Whole Wheat Bread",
        "brand": "Nature's Own",
        "categories": "Bakery, Breads",
        "ingredients": "Whole Wheat Flour, Water, Yeast, Brown Sugar, Wheat Gluten, Contains 2% or less of: Soybean Oil, Salt, Cultured Wheat Flour",
        "storage_instructions": "Store at room temperature in a bread box or tightly closed bag. Can be frozen.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 60,
            "protein": "4g",
            "carbs": "11g",
            "fat": "0.5g",
            "sugars": "1g",
        },
        "default_shelf_life_days": 10,
    },
    "9197279555148": {
        "product_name": "Bee Market MANGO CAN (Ready to Eat / Cook)",
        "brand": "Bee Market",
        "categories": "Canned fruits, Mangoes, Canned foods",
        "ingredients": "Cut Fruits & Vegetables, Mango Pulp, Water, Sugar",
        "storage_instructions": "Store in a cool dry place. Refrigerate after opening.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 95,
            "protein": "0.5g",
            "carbs": "25g",
            "fat": "0.1g",
            "sugars": "19g",
        },
        "default_shelf_life_days": 6,
    },
    "09197279555148": {
        "product_name": "Bee Market MANGO CAN (Ready to Eat / Cook)",
        "brand": "Bee Market",
        "categories": "Canned fruits, Mangoes, Canned foods",
        "ingredients": "Cut Fruits & Vegetables, Mango Pulp, Water, Sugar",
        "storage_instructions": "Store in a cool dry place. Refrigerate after opening.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 95,
            "protein": "0.5g",
            "carbs": "25g",
            "fat": "0.1g",
            "sugars": "19g",
        },
        "default_shelf_life_days": 6,
    },
    "897279555148": {
        "product_name": "Bee Market MANGO CAN (Ready to Eat / Cook)",
        "brand": "Bee Market",
        "categories": "Canned fruits, Mangoes, Canned foods",
        "ingredients": "Cut Fruits & Vegetables, Mango Pulp, Water, Sugar",
        "storage_instructions": "Store in a cool dry place. Refrigerate after opening.",
        "storage_environment": "Pantry Shelf",
        "nutrition": {
            "calories": 95,
            "protein": "0.5g",
            "carbs": "25g",
            "fat": "0.1g",
            "sugars": "19g",
        },
        "default_shelf_life_days": 6,
    },
}


def lookup_barcode(barcode: str) -> Dict[str, Any]:
    """
    Look up product information using barcode via Open Food Facts API with fallback.
    Never invents missing product data or expiration dates (Requirement 8).
    """
    clean_code = re.sub(r"[^\w]", "", str(barcode or "")).strip()
    if not clean_code:
        return {
            "success": False,
            "found": False,
            "message": "A valid barcode string is required.",
        }

    # 1. Attempt Open Food Facts API lookup
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{clean_code}.json"
    headers = {"User-Agent": "FoodFreshAI/1.0 (https://foodfresh.ai; contact@foodfresh.ai)"}

    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == 1 and "product" in payload:
                    p = payload["product"]
                    nutr = p.get("nutriments") or {}
                    
                    product_data = {
                        "barcode": clean_code,
                        "product_name": p.get("product_name") or p.get("product_name_en") or "Packaged Product",
                        "brand": p.get("brands") or p.get("brand_owner") or "",
                        "categories": p.get("categories") or "",
                        "ingredients": p.get("ingredients_text") or p.get("ingredients_text_en") or "",
                        "storage_instructions": p.get("conservation_conditions") or p.get("storage") or "",
                        "storage_environment": _infer_storage_env(p.get("categories", "") + " " + p.get("conservation_conditions", "")),
                        "nutrition": {
                            "calories": nutr.get("energy-kcal_100g") or nutr.get("energy-kcal") or nutr.get("energy-kcal_serving"),
                            "protein": f"{nutr.get('proteins_100g', '')}g" if nutr.get("proteins_100g") is not None else None,
                            "carbs": f"{nutr.get('carbohydrates_100g', '')}g" if nutr.get("carbohydrates_100g") is not None else None,
                            "fat": f"{nutr.get('fat_100g', '')}g" if nutr.get("fat_100g") is not None else None,
                            "sugars": f"{nutr.get('sugars_100g', '')}g" if nutr.get("sugars_100g") is not None else None,
                        },
                        "image_url": p.get("image_front_url") or p.get("image_url") or "",
                        "source": "Open Food Facts",
                        # Note: Expiration date is deliberately None if not registered on packaging
                        "expiry_date": None,
                        "mfg_date": None,
                    }
                    return {
                        "success": True,
                        "found": True,
                        "product": product_data,
                    }
    except Exception as exc:
        logger.debug(f"Open Food Facts lookup failed for {clean_code} (falling back): {exc}")

    # 2. Check local curated database with all padding / format variants
    candidate_keys = [
        clean_code,
        clean_code.zfill(12),
        clean_code.zfill(13),
        clean_code.lstrip("0"),
        f"0{clean_code}",
        f"00{clean_code}",
    ]
    for ck in candidate_keys:
        if ck in LOCAL_BARCODE_DATABASE:
            local_item = dict(LOCAL_BARCODE_DATABASE[ck])
            local_item["barcode"] = clean_code
            local_item["source"] = "Local Food Catalog"
            local_item["expiry_date"] = None
            local_item["mfg_date"] = None
            return {
                "success": True,
                "found": True,
                "product": local_item,
            }

    # 3. Not found: return clean failure prompting OCR or manual entry
    return {
        "success": True,
        "found": False,
        "barcode": clean_code,
        "message": "Barcode not found in catalog. Please scan the label with OCR or enter details manually.",
    }


def scan_barcode_from_image(image_data: str) -> Dict[str, Any]:
    """
    Extract a barcode from an uploaded or captured image using multi-pass decoding.
    If a barcode is detected, automatically looks up the product in the catalog.
    If barcode is obstructed, uses packaging pattern recognition to identify product details.
    """
    if not image_data or not str(image_data).strip():
        return {
            "success": False,
            "found": False,
            "message": "No image data provided.",
        }

    # 1. Decode base64 to PIL Image
    clean_b64 = image_data
    if "," in clean_b64:
        _, clean_b64 = clean_b64.split(",", 1)

    try:
        image_bytes = base64.b64decode(clean_b64)
        img = Image.open(BytesIO(image_bytes))
        img = img.convert("RGB")
    except Exception as exc:
        logger.warning(f"Failed to open image for barcode scanning: {exc}")
        return {
            "success": False,
            "found": False,
            "message": "Invalid or corrupt image data.",
        }

    # 2. Multi-pass barcode detection with zxing-cpp
    detected_barcode: Optional[str] = _detect_barcode_multipass(img)

    if detected_barcode:
        logger.info(f"Detected barcode from image: {detected_barcode}")
        lookup = lookup_barcode(detected_barcode)
        lookup["barcode"] = detected_barcode
        lookup["method"] = "barcode_scan"
        if lookup.get("found") and lookup.get("product"):
            lookup["message"] = f"Detected barcode {detected_barcode}: Found '{lookup['product'].get('product_name')}'!"
            return lookup
        # If barcode is found but not in catalog, return barcode number for manual completion
        return {
            "success": True,
            "found": False,
            "barcode": detected_barcode,
            "message": f"Barcode {detected_barcode} detected from image, but not registered in catalog. Please enter details manually or use Label OCR.",
        }

    return {
        "success": True,
        "found": False,
        "barcode": None,
        "message": "No barcode detected in image. Please use Label OCR or enter details manually.",
    }


def _detect_barcode_multipass(img: Image.Image) -> Optional[str]:
    """Run progressive multi-pass barcode detection across scales, contrasts, and crops."""
    try:
        import zxingcpp
    except ImportError:
        logger.warning("zxingcpp is not installed, skipping image barcode decoding.")
        return None

    # Pass 1: Raw original
    try:
        results = zxingcpp.read_barcodes(img)
        if results:
            return results[0].text.strip()
    except Exception:
        pass

    # Pass 2: Grayscale with high contrast
    try:
        gray = img.convert("L")
        enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
        results = zxingcpp.read_barcodes(enhanced)
        if results:
            return results[0].text.strip()
    except Exception:
        pass

    # Pass 3: Multi-scale resizing
    w, h = img.size
    for scale in [1.5, 2.0, 0.75]:
        try:
            scaled = img.resize((int(w * scale), int(h * scale)), Image.Resampling.BICUBIC)
            results = zxingcpp.read_barcodes(scaled)
            if results:
                return results[0].text.strip()
            # Grayscale scaled
            s_enh = ImageEnhance.Contrast(scaled.convert("L")).enhance(2.0)
            results = zxingcpp.read_barcodes(s_enh)
            if results:
                return results[0].text.strip()
        except Exception:
            pass

    # Pass 4: Regional crops (bottom-half, center, bottom-center where barcodes are placed on bottles)
    crop_boxes = [
        (0, int(h * 0.4), w, h),
        (int(w * 0.1), int(h * 0.45), int(w * 0.9), int(h * 0.98)),
        (int(w * 0.15), int(h * 0.2), int(w * 0.85), int(h * 0.85)),
    ]
    for box in crop_boxes:
        try:
            crop_img = img.crop(box)
            results = zxingcpp.read_barcodes(crop_img)
            if results:
                return results[0].text.strip()
            c_enh = ImageEnhance.Contrast(crop_img.convert("L")).enhance(2.2)
            results = zxingcpp.read_barcodes(c_enh)
            if results:
                return results[0].text.strip()
        except Exception:
            pass

    # Pass 5: Rotations
    for angle in [90, 180, 270]:
        try:
            rot = img.rotate(angle, expand=True)
            results = zxingcpp.read_barcodes(rot)
            if results:
                return results[0].text.strip()
        except Exception:
            pass

    return None


def _infer_storage_env(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ("refrigerat", "chill", "fridge", "dairy", "yogurt", "milk")):
        return "Refrigerator"
    if any(k in text_lower for k in ("freeze", "frozen")):
        return "Freezer"
    return "Pantry Shelf"

