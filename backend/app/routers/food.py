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
detection_service.load_model()

food_repository = FoodRepository()
food_service = FoodService(food_repository)
analysis_repository = AnalysisRepository()
analysis_service = AnalysisService(analysis_repository)

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)




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

    detections = detection_service.predict(saved_image["path"])

    saved_detections = []

    for detection in detections:
        saved_detection = food_service.save_detection(
            db=db,
            analysis_id=analysis.id,
            class_id=detection["class_id"],
            class_name=detection["class_name"],
            confidence=detection["confidence"],
        )

        saved_detections.append(
            {
                "class_id": saved_detection.class_id,
                "class_name": saved_detection.class_name,
                "confidence": saved_detection.confidence,
                "x1": detection["x1"],
                "y1": detection["y1"],
                "x2": detection["x2"],
                "y2": detection["y2"],
            }
        )

    return {
        "image_id": saved_image["image_id"],
        "detections": saved_detections,
    }