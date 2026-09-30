"""
FoodFresh AI - Food Recognition API Route
Handles multipart image upload and dispatches inference to the FoodRecognitionService.
"""

import logging
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse

from backend.app.services.food_recognition_service import get_food_recognition_service

logger = logging.getLogger("foodfresh.routes.food_recognition")

router = APIRouter(prefix="/api/food-recognition", tags=["food-recognition"])


@router.post("/predict")
async def predict_food(
    file: UploadFile = File(...),
    storage_type: str = Form(default="countertop"),
    days_stored: int = Form(default=0),
    top_k: int = Query(default=3, ge=1, le=24, description="Number of top predictions to return")
):
    """
    Accept an uploaded food image and run real-time inference using the trained EfficientNet-B0 model.

    Returns:
        JSON object with detectedFood, recognitionConfidence, topPredictions, source, model, and status.
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided. Please upload or capture an image."
        )

    # Read binary contents
    try:
        image_bytes = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded image."
        )

    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty. Please select a valid food image."
        )

    # 15 MB maximum size guard
    max_size_bytes = 15 * 1024 * 1024
    if len(image_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds the 15 MB limit."
        )

    service = get_food_recognition_service()
    result = service.predict_image(
        image_bytes,
        top_k=top_k,
        storage_type=storage_type,
        days_stored=days_stored
    )

    if not result.get("success"):
        if result.get("status") == "invalid_image":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )
        elif result.get("status") == "model_unavailable":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=result
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=result
            )

    return result
