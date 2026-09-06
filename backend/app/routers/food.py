from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ml_service import FoodDetectionService
from app.services.image_service import save_uploaded_image

from app.models.food import FoodDetectionResponse
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.food_service import FoodService
from app.repositories.food_repository import FoodRepository

from app.repositories.analysis_repository import AnalysisRepository
from app.services.analysis_service import AnalysisService


detection_service = FoodDetectionService()

food_repository = FoodRepository()
food_service = FoodService(food_repository)
analysis_repository = AnalysisRepository()
analysis_service = AnalysisService(analysis_repository)

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)

detection_service = FoodDetectionService()


@router.get("/test")
def test_food_endpoint():
    return {
        "message": "Food API is working"
    }

@router.post("/upload")
async def upload_food_image(file: UploadFile = File(...)):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/jpg",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPEG, PNG, or WEBP image.",
        )

    try:
        saved_image = await save_uploaded_image(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=413,
            detail=str(exc),
        ) from exc

    return {
        "message": "Food image uploaded successfully",
        **saved_image,
    } 

@router.post("/detect", response_model=FoodDetectionResponse)
async def detect_food(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    saved_image = await save_uploaded_image(file)

    analysis = analysis_service.create_analysis(
        db=db,
        image_id=saved_image["image_id"],
    )

    test_detection = food_service.save_detection(
    db=db,
    analysis_id=analysis.id,
    class_id=0,
    class_name="rice",
    confidence=0.95,
)

    return {
        "image_id": saved_image["image_id"],
        "detections": [
            {
                "class_id": test_detection.class_id,
                "class_name": test_detection.class_name,
                "confidence": test_detection.confidence,
                "x1": 0.10,
                "y1": 0.10,
                "x2": 0.90,
                "y2": 0.90,
            }
        ],
    }