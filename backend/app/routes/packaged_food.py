"""
FoodFresh AI — Packaged Food Scanning & OCR Routes
REST endpoints for barcode product lookup and packaging label OCR extraction.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.deps.auth import get_optional_user
from backend.app.services.barcode_service import lookup_barcode, scan_barcode_from_image
from backend.app.services.packaged_food_ocr_service import extract_packaged_food_info

logger = logging.getLogger("foodfresh.routes.packaged_food")

router = APIRouter(prefix="/api/packaged-food", tags=["packaged-food"])


class BarcodeLookupRequest(BaseModel):
    barcode: str = Field(..., description="EAN/UPC barcode number")


class OcrExtractRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image string of packaging or label")


@router.post("/barcode-lookup")
def api_barcode_lookup(
    req: BarcodeLookupRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """
    Look up product information using the scanned barcode.
    Queries Open Food Facts with offline database fallback.
    """
    try:
        result = lookup_barcode(req.barcode)
        return result
    except Exception as exc:
        logger.error(f"Barcode lookup failed for {req.barcode}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to look up barcode: {exc}",
        ) from exc


@router.post("/scan-image")
def api_scan_barcode_image(
    req: OcrExtractRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """
    Decode barcode and recognize product details directly from an image.
    Uses multi-pass barcode decoding.
    """
    try:
        result = scan_barcode_from_image(req.image)
        return result
    except Exception as exc:
        logger.error(f"Image barcode scanning failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scan barcode from image: {exc}",
        ) from exc


@router.post("/ocr")
def api_packaged_food_ocr(
    req: OcrExtractRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """
    Perform OCR on packaging label photo to extract product name,
    dates, ingredients, storage advice, and nutrition facts.
    """
    try:
        result = extract_packaged_food_info(req.image)
        return result
    except Exception as exc:
        logger.error(f"Packaging OCR extraction failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract packaging text via OCR: {exc}",
        ) from exc

