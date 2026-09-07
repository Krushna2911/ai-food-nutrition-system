from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_profile_repository import UserProfileRepository
from app.services.user_profile_service import UserProfileService


router = APIRouter(prefix="/profile", tags=["User Profile"])

profile_service = UserProfileService(UserProfileRepository())


class UserProfileRequest(BaseModel):
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str
    diet_goal: str
    dietary_preference: str
    food_restrictions: str | None = None


@router.post("")
def create_profile(
    profile: UserProfileRequest,
    db: Session = Depends(get_db),
):
    created_profile = profile_service.create_profile(
        db=db,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        diet_goal=profile.diet_goal,
        dietary_preference=profile.dietary_preference,
        food_restrictions=profile.food_restrictions,
    )

    return {
        "id": created_profile.id,
        "age": created_profile.age,
        "height_cm": created_profile.height_cm,
        "weight_kg": created_profile.weight_kg,
        "activity_level": created_profile.activity_level,
        "diet_goal": created_profile.diet_goal,
        "dietary_preference": created_profile.dietary_preference,
        "food_restrictions": created_profile.food_restrictions,
    }


@router.get("/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile(
        db=db,
        profile_id=profile_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Profile {profile_id} not found.",
        )

    return profile



