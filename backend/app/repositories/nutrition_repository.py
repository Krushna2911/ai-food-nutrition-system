from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.nutrition import Nutrition


class NutritionRepository:
    def get_by_food_name(
        self,
        db: Session,
        food_name: str,
    ) -> Optional[Nutrition]:
        statement = select(Nutrition).where(
            Nutrition.food_name.ilike(food_name.strip())
        )

        return db.execute(statement).scalar_one_or_none()