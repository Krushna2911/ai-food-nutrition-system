from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


class UserProfileRepository:
    def create(
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
        profile = UserProfile(
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            diet_goal=diet_goal,
            dietary_preference=dietary_preference,
            food_restrictions=food_restrictions,
        )

        db.add(profile)
        db.flush()
        db.refresh(profile)

        return profile

    def get_by_id(
        self,
        db: Session,
        profile_id: int,
    ) -> UserProfile | None:
        return (
            db.query(UserProfile)
            .filter(UserProfile.id == profile_id)
            .first()
        )

    def update(
        self,
        db: Session,
        profile_id: int,
        age: int,
        height_cm: float,
        weight_kg: float,
        activity_level: str,
        diet_goal: str,
        dietary_preference: str,
        food_restrictions: str | None,
    ) -> UserProfile | None:
        profile = self.get_by_id(db, profile_id)

        if profile is None:
            return None

        profile.age = age
        profile.height_cm = height_cm
        profile.weight_kg = weight_kg
        profile.activity_level = activity_level
        profile.diet_goal = diet_goal
        profile.dietary_preference = dietary_preference
        profile.food_restrictions = food_restrictions

        db.flush()
        db.refresh(profile)

        return profile