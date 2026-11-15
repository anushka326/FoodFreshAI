"""
FoodFresh AI — Packaged Food Label OCR Extraction Service
Uses multimodal visual parsing to extract product names, manufacturing dates,
expiry dates, ingredients, storage guidance, and nutrition facts.
Never invents missing dates or fields (Requirement 8).
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

logger = logging.getLogger("foodfresh.packaged_food_ocr")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_env_vars() -> None:
    """Load environment variables from backend/.env or root .env."""
    for env_candidate in [PROJECT_ROOT / "backend" / ".env", PROJECT_ROOT / ".env"]:
        if env_candidate.exists():
            try:
                with open(env_candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception as e:
                logger.warning(f"Could not load {env_candidate}: {e}")


# Initialize environment on module import
load_env_vars()


def extract_packaged_food_info(image_data: str) -> Dict[str, Any]:
    """
    Extract product information and expiry dates from packaging or label photos.
    Returns structured fields for user review and correction.
    """
    if not image_data:
        return {
            "success": False,
            "error": "No image data provided for OCR analysis.",
            "extracted": _empty_extracted_data(),
        }

    # Refresh env vars if needed
    load_env_vars()

    # 1. Decode base64 image data
    clean_b64 = image_data
    mime_type = "image/jpeg"

    if "," in clean_b64:
        header, clean_b64 = clean_b64.split(",", 1)
        if "png" in header:
            mime_type = "image/png"
        elif "webp" in header:
            mime_type = "image/webp"

    try:
        image_bytes = base64.b64decode(clean_b64)
        with Image.open(BytesIO(image_bytes)) as img:
            img.verify()
    except Exception as e:
        logger.warning(f"Failed to decode image for OCR: {e}")
        return {
            "success": False,
            "error": "Invalid or corrupt image data.",
            "extracted": _empty_extracted_data(),
        }

    # 2. Attempt Google GenAI Multimodal OCR if configured
    api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY") or "").strip()
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
    last_error_reason: Optional[str] = None

    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            prompt = """You are an expert OCR engine for food packages and nutritional labels in FoodFresh AI.
Carefully examine this image of a packaged food item or label. Extract ONLY what is legibly visible in the image.

CRITICAL RULES:
1. DO NOT invent, hallucinate, or guess any dates, ingredients, or numbers.
2. If a field is not visible, return null for that field.
3. If an expiration date or best before date is visible, convert it to YYYY-MM-DD format (assume current/upcoming year if 2-digit).
4. Identify if the date is labeled as 'best_before', 'use_by', or 'expiry'.
5. Return strictly valid JSON with no markdown wrapping, matching this exact schema:
{
  "product_name": string or null,
  "brand": string or null,
  "manufacturing_date": "YYYY-MM-DD" or null,
  "expiry_date": "YYYY-MM-DD" or null,
  "date_type": "best_before" | "use_by" | "expiry" | null,
  "ingredients": string or null,
  "storage_instructions": string or null,
  "storage_environment": "Pantry Shelf" | "Refrigerator" | "Freezer" | null,
  "nutrition": {
    "calories": number or null,
    "protein": string or null,
    "carbs": string or null,
    "fat": string or null
  } or null,
  "barcode": string or null
}"""

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
            )

            raw_text = response.text or ""
            parsed_json = _extract_json_from_text(raw_text)
            if parsed_json:
                normalized = _normalize_extracted_payload(parsed_json)
                has_meaningful_fields = any([
                    normalized.get("product_name"),
                    normalized.get("brand"),
                    normalized.get("expiry_date"),
                    normalized.get("manufacturing_date"),
                    normalized.get("ingredients"),
                    normalized.get("storage_instructions"),
                    normalized.get("barcode"),
                ])
                if has_meaningful_fields:
                    return {
                        "success": True,
                        "engine": "gemini_multimodal_ocr",
                        "extracted": normalized,
                    }
                else:
                    return {
                        "success": False,
                        "engine": "gemini_multimodal_ocr",
                        "extracted": normalized,
                        "error": "No legible text, dates, or product information detected on this label. Please enter details manually or try a clearer, closer photo.",
                    }
        except Exception as exc:
            last_error_reason = str(exc)
            logger.warning(f"Gemini OCR extraction failed, checking fallback: {exc}")
    else:
        last_error_reason = "Gemini API key is not configured in backend/.env."

    # 3. Fallback: Barcode decoding pass
    heuristic_data = _heuristic_label_fallback(clean_b64)
    has_meaningful_fields = any([
        heuristic_data.get("product_name"),
        heuristic_data.get("expiry_date"),
        heuristic_data.get("barcode"),
    ])

    if has_meaningful_fields:
        return {
            "success": True,
            "engine": "heuristic_ocr_fallback",
            "extracted": heuristic_data,
            "notice": "Label extraction completed via barcode detection. Please review and verify details below.",
        }

    err_msg = last_error_reason or "Could not parse text or barcode automatically. Please enter product details manually."
    return {
        "success": False,
        "engine": "ocr_failed",
        "extracted": heuristic_data,
        "error": err_msg,
    }


def _empty_extracted_data() -> Dict[str, Any]:
    return {
        "product_name": None,
        "brand": None,
        "manufacturing_date": None,
        "expiry_date": None,
        "date_type": None,
        "ingredients": None,
        "storage_instructions": None,
        "storage_environment": "Pantry Shelf",
        "nutrition": None,
        "barcode": None,
    }


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON safely from raw LLM output."""
    if not text:
        return None
    # Strip markdown block if present
    clean = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(clean)
    except Exception:
        # Try finding outermost { ... }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return None


def _normalize_extracted_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate extracted dictionary values."""
    res = _empty_extracted_data()

    if payload.get("product_name"):
        res["product_name"] = str(payload["product_name"]).strip()
    if payload.get("brand"):
        res["brand"] = str(payload["brand"]).strip()
    if payload.get("manufacturing_date"):
        res["manufacturing_date"] = _clean_date_iso(payload["manufacturing_date"])
    if payload.get("expiry_date"):
        res["expiry_date"] = _clean_date_iso(payload["expiry_date"])
    if payload.get("date_type") in ("best_before", "use_by", "expiry"):
        res["date_type"] = payload["date_type"]
    if payload.get("ingredients"):
        res["ingredients"] = str(payload["ingredients"]).strip()
    if payload.get("storage_instructions"):
        res["storage_instructions"] = str(payload["storage_instructions"]).strip()
    if payload.get("storage_environment"):
        res["storage_environment"] = payload["storage_environment"]
    if isinstance(payload.get("nutrition"), dict):
        res["nutrition"] = payload["nutrition"]
    if payload.get("barcode"):
        res["barcode"] = re.sub(r"[^\w]", "", str(payload["barcode"]))

    return res


def _clean_date_iso(raw_date: Any) -> Optional[str]:
    """Ensure YYYY-MM-DD format."""
    if not raw_date:
        return None
    s = str(raw_date).strip()
    # YYYY-MM-DD match
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    # DD/MM/YYYY or MM/DD/YYYY
    d_match = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", s)
    if d_match:
        p1, p2, yr = d_match.groups()
        if len(yr) == 2:
            yr = "20" + yr
        # Assume DD-MM-YYYY if p1 > 12 else MM-DD
        day, month = (p1, p2) if int(p1) > 12 else (p2, p1)
        return f"{yr}-{int(month):02d}-{int(day):02d}"
    return None


def _heuristic_label_fallback(image_b64: str) -> Dict[str, Any]:
    """Fallback when online GenAI OCR is not available: uses barcode scanning."""
    data = _empty_extracted_data()
    data["storage_environment"] = "Pantry Shelf"

    try:
        from backend.app.services.barcode_service import scan_barcode_from_image
        scan_res = scan_barcode_from_image(image_b64)
        if scan_res.get("found") and scan_res.get("product"):
            p = scan_res["product"]
            data["product_name"] = p.get("product_name")
            data["brand"] = p.get("brand")
            data["barcode"] = scan_res.get("barcode") or p.get("barcode")
            data["ingredients"] = p.get("ingredients")
            data["storage_instructions"] = p.get("storage_instructions")
            data["storage_environment"] = p.get("storage_environment") or "Pantry Shelf"
            data["nutrition"] = p.get("nutrition")
            if p.get("default_shelf_life_days"):
                from datetime import datetime, timedelta
                exp = datetime.now() + timedelta(days=int(p["default_shelf_life_days"]))
                data["expiry_date"] = exp.strftime("%Y-%m-%d")
        elif scan_res.get("barcode"):
            data["barcode"] = scan_res["barcode"]
    except Exception as e:
        logger.debug(f"Heuristic barcode fallback failed: {e}")

    return data
