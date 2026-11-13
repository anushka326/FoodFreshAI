"""ML feedback API — collect corrections; no automatic training."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.deps.auth import get_current_user
from backend.app.services.ml_feedback_service import create_feedback_record, list_feedback_for_user

logger = logging.getLogger("foodfresh.routes.ml_feedback")

router = APIRouter(prefix="/api/ml-feedback", tags=["ml-feedback"])


class FeedbackRequest(BaseModel):
    analysisId: Optional[str] = None
    imagePath: Optional[str] = None
    predictedFood: Optional[str] = None
    predictedFoodConfidence: Optional[float] = None
    predictedFoodForm: Optional[str] = None
    predictedFreshness: Optional[str] = None
    predictedFreshnessConfidence: Optional[float] = None
    predictedShelfLife: Optional[str] = None
    userCorrectedFood: Optional[str] = None
    userCorrectedFoodForm: Optional[str] = None
    userCorrectedFreshness: Optional[str] = None
    userCorrectedShelfLife: Optional[str] = None
    storageType: Optional[str] = None
    daysStored: Optional[int] = None


@router.post("")
def submit_feedback(req: FeedbackRequest, user: dict = Depends(get_current_user)):
    try:
        record = create_feedback_record(user["id"], req.model_dump())
        return {"success": True, "feedback": record}
    except Exception as e:
        logger.error(f"Feedback save failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save feedback.")


@router.get("")
def get_my_feedback(user: dict = Depends(get_current_user)):
    items = list_feedback_for_user(user["id"])
    return {"success": True, "items": items}
