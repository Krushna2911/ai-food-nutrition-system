from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.recommendation_service import RecommendationService


router = APIRouter(prefix="/recommendation", tags=["Recommendation"])

recommendation_service = RecommendationService()


class RecommendationRequest(BaseModel):
    profile_id: int


class RecommendationResponse(BaseModel):
    daily_calorie_target: float
    total_calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    amdr_compliant: bool
    meals: list[dict]
    recommendation: str


@router.post("", response_model=RecommendationResponse)
def generate_recommendation(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    try:
        state = recommendation_service.build_state(
            db=db,
            profile_id=request.profile_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    graph = recommendation_service.build_graph()
    result = graph.invoke(state)

    return RecommendationResponse(
        daily_calorie_target=result["daily_calorie_target"],
        total_calories=result["total_calories"],
        protein_g=result["protein_g"],
        carbohydrates_g=result["carbohydrates_g"],
        fat_g=result["fat_g"],
        amdr_compliant=result["amdr_compliant"],
        meals=result["meals"],
        recommendation=result["recommendation"],
    )