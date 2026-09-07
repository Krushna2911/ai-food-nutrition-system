from pydantic import BaseModel
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    height_cm: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    weight_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    activity_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    diet_goal: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    dietary_preference: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    food_restrictions: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


class UserProfileResponse(BaseModel):
    id: int
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str
    diet_goal: str
    dietary_preference: str
    food_restrictions: str | None