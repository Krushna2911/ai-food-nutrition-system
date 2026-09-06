from typing import Optional

from sqlalchemy.orm import Session

from app.models.nutrition import Nutrition
from app.repositories.nutrition_repository import NutritionRepository


class NutritionService:
    def __init__(self, repository: NutritionRepository):
        self.repository = repository

    def get_nutrition(
        self,
        db: Session,
        food_name: str,
    ) -> Optional[Nutrition]:
        return self.repository.get_by_food_name(
            db,
            food_name,
        )

    def calculate_nutrition(
        self,
        nutrition: Nutrition,
        portion_g: float,
    ) -> dict:
        if portion_g <= 0:
            raise ValueError("Portion size must be greater than 0.")

        multiplier = portion_g / nutrition.serving_size_g

        return {
            "food_name": nutrition.food_name,
            "portion_g": portion_g,
            "calories": round(nutrition.calories * multiplier, 2),
            "protein_g": round(nutrition.protein_g * multiplier, 2),
            "carbohydrates_g": round(
                nutrition.carbohydrates_g * multiplier,
                2,
            ),
            "fat_g": round(nutrition.fat_g * multiplier, 2),
        }