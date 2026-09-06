from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository


class AnalysisService:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository

    def create_analysis(
        self,
        db: Session,
        image_id: str,
    ) -> Analysis:
        analysis = self.repository.create_analysis(
            db=db,
            image_id=image_id,
        )

        db.commit()

        return analysis

    def get_analysis_by_image_id(
        self,
        db: Session,
        image_id: str,
    ) -> Analysis | None:
        return self.repository.get_by_image_id(
            db=db,
            image_id=image_id,
        )

    def get_all_analyses(
        self,
        db: Session,
    ) -> list[Analysis]:
        return self.repository.get_all(
            db=db,
        )