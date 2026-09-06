from sqlalchemy.orm import Session

from app.models.food import Food


class FoodRepository:
    def create_detection(
        self,
        db: Session,
        analysis_id: int,
        class_id: int,
        class_name: str,
        confidence: float,
    ) -> Food:
        detection = Food(
            analysis_id=analysis_id,
            class_id=class_id,
            class_name=class_name,
            confidence=confidence,
        )

    def get_by_analysis_id(
        self,
        db: Session,
        analysis_id: int,
    ) -> list[Food]:
        return (
            db.query(Food)
            .filter(Food.analysis_id == analysis_id)
            .all()
        )

        db.add(detection)
        db.flush()
        db.refresh(detection)

        return detection