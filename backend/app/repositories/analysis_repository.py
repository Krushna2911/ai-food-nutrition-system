from sqlalchemy.orm import Session

from app.models.analysis import Analysis


class AnalysisRepository:
    def create_analysis(
        self,
        db: Session,
        image_id: str,
    ) -> Analysis:
        analysis = Analysis(
            image_id=image_id,
        )

        db.add(analysis)
        db.flush()
        db.refresh(analysis)

        return analysis

    def get_by_image_id(
        self,
        db: Session,
        image_id: str,
    ) -> Analysis | None:
        return (
            db.query(Analysis)
            .filter(Analysis.image_id == image_id)
            .first()
        )