from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.repositories.user_profile_repository import UserProfileRepository


class UserProfileService:
    def __init__(self, repository: UserProfileRepository):
        self.repository = repository

    def create_profile(
        self,
        db: Session,
        age: int,
        height_cm: float,
        weight_kg: float,
        activity_level: str,
        diet_goal: str,
        dietary_preference: str,
        food_restrictions: str | None,
    ) -> UserProfile:
        profile = self.repository.create(
            db=db,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            diet_goal=diet_goal,
            dietary_preference=dietary_preference,
            food_restrictions=food_restrictions,
        )

        db.commit()
        return profile

    def get_profile(
        self,
        db: Session,
        profile_id: int,
    ) -> UserProfile | None:
        return self.repository.get_by_id(
            db=db,
            profile_id=profile_id,
        )

    