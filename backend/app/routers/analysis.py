from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import AnalysisResponse
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.food_repository import FoodRepository
from app.services.analysis_service import AnalysisService
from app.services.food_service import FoodService


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


analysis_service = AnalysisService(
    AnalysisRepository()
)

food_service = FoodService(
    FoodRepository()
)


@router.get("/{image_id}", response_model=AnalysisResponse)
def get_analysis(
    image_id: str,
    db: Session = Depends(get_db),
):
    analysis = analysis_service.get_analysis_by_image_id(
        db=db,
        image_id=image_id,
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found for image '{image_id}'.",
        )

    detections = food_service.get_detections_by_analysis_id(
        db=db,
        analysis_id=analysis.id,
    )

    return {
    "id": analysis.id,
    "image_id": analysis.image_id,
    "detections": [
        {
            "id": detection.id,
            "class_id": detection.class_id,
            "class_name": detection.class_name,
            "confidence": detection.confidence,
        }
        for detection in detections
    ],
}

   