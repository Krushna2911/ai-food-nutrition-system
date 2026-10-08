from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.diet_plan import DietPlanRequest, DietPlanResponse
from app.repositories.nutrition_repository import NutritionRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.services.diet_planning_service import DietPlanningService
from app.services.nutrition_requirement_service import NutritionRequirementService
from app.services.nutrition_service import NutritionService


router = APIRouter(
    prefix="/diet-plan",
    tags=["Diet Plan"],
)


profile_repository = UserProfileRepository()
nutrition_repository = NutritionRepository()
nutrition_service = NutritionService(nutrition_repository)
requirement_service = NutritionRequirementService()
diet_planning_service = DietPlanningService(nutrition_service)


@router.post(
    "",
    response_model=DietPlanResponse,
)
def generate_diet_plan(
    request: DietPlanRequest,
    db: Session = Depends(get_db),
):
    profile = profile_repository.get_by_id(
        db=db,
        profile_id=request.profile_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Profile {request.profile_id} not found.",
        )

    try:
        daily_calories = requirement_service.calculate_daily_calories(
            age=profile.age,
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            activity_level=profile.activity_level,
            diet_goal=profile.diet_goal,
        )

        nutrition_records = nutrition_repository.get_all(db)

        return diet_planning_service.generate_plan(
            daily_calories=daily_calories,
            dietary_preference=profile.dietary_preference,
            food_restrictions=profile.food_restrictions,
            nutrition_records=nutrition_records,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error