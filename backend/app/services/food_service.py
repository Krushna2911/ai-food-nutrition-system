from sqlalchemy.orm import Session

from app.models.food import Food
from app.repositories.food_repository import FoodRepository


class FoodService:
    def __init__(self, repository: FoodRepository):
        self.repository = repository

    def save_detection(
        self,
        db: Session,
        analysis_id: int,
        class_id: int,
        class_name: str,
        confidence: float,
    ) -> Food:
        detection = self.repository.create_detection(
            db=db,
            analysis_id=analysis_id,
            class_id=class_id,
            class_name=class_name,
            confidence=confidence,
        )

        db.commit()

        return detection

    def get_detections_by_analysis_id(
        self,
        db: Session,
        analysis_id: int,
    ) -> list[Food]:
        return self.repository.get_by_analysis_id(
            db=db,
            analysis_id=analysis_id,
        )