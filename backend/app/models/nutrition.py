from pydantic import BaseModel
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Nutrition(Base):
    __tablename__ = "nutrition"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    food_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    serving_size_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    calories: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    protein_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    carbohydrates_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fat_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )


class NutritionInfo(BaseModel):
    food_name: str
    serving_size_g: float
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float