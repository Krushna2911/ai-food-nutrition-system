from pydantic import BaseModel
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
    ForeignKey("analyses.id"),
    nullable=False,
    index=True,
)

   
    class_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )


class FoodDetection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


class FoodDetectionResponse(BaseModel):
    image_id: str
    detections: list[FoodDetection]