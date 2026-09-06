from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.nutrition import NutritionInfo
from app.repositories.nutrition_repository import NutritionRepository
from app.services.nutrition_service import NutritionService


class NutritionCalculationRequest(BaseModel):
    food_name: str
    portion_g: float

router = APIRouter(
    prefix="/nutrition",
    tags=["Nutrition"],
)


nutrition_repository = NutritionRepository()
nutrition_service = NutritionService(nutrition_repository)

@router.get("/{food_name}", response_model=NutritionInfo)
def get_nutrition(
    food_name: str,
    db: Session = Depends(get_db),
):
    nutrition = nutrition_service.get_nutrition(
        db,
        food_name,
    )

    if nutrition is None:
        raise HTTPException(
            status_code=404,
            detail=f"Nutrition data not found for '{food_name}'.",
        )

    return nutrition

@router.post("/calculate")
def calculate_nutrition(
    request: NutritionCalculationRequest,
    db: Session = Depends(get_db),
):
    nutrition = nutrition_service.get_nutrition(
        db,
        request.food_name,
    )

    if nutrition is None:
        raise HTTPException(
            status_code=404,
            detail=f"Nutrition data not found for '{request.food_name}'.",
        )

    try:
        return nutrition_service.calculate_nutrition(
            nutrition,
            request.portion_g,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc