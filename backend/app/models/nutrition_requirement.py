from pydantic import BaseModel


class NutritionRequirementRequest(BaseModel):
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str
    diet_goal: str


class NutritionRequirementResponse(BaseModel):
    bmr: float
    daily_calories: float