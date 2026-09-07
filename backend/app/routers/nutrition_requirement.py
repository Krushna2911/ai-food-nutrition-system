from fastapi import APIRouter, HTTPException

from app.models.nutrition_requirement import (
    NutritionRequirementRequest,
    NutritionRequirementResponse,
)
from app.services.nutrition_requirement_service import (
    NutritionRequirementService,
)


router = APIRouter(
    prefix="/nutrition-requirements",
    tags=["Nutrition Requirements"],
)

requirement_service = NutritionRequirementService()


@router.post(
    "",
    response_model=NutritionRequirementResponse,
)
def calculate_nutrition_requirements(
    request: NutritionRequirementRequest,
):
    try:
        bmr = requirement_service.calculate_bmr(
            age=request.age,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
        )

        daily_calories = requirement_service.calculate_daily_calories(
            age=request.age,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            activity_level=request.activity_level,
            diet_goal=request.diet_goal,
        )

        return {
            "bmr": bmr,
            "daily_calories": daily_calories,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )