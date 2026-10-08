from pydantic import BaseModel


class DietPlanRequest(BaseModel):
    profile_id: int


class DietPlanFood(BaseModel):
    food_name: str
    portion_g: float
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float


class DietPlanMeal(BaseModel):
    meal: str
    foods: list[DietPlanFood]
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float


class DietPlanResponse(BaseModel):
    daily_calorie_target: float
    total_calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    amdr_compliant: bool
    meals: list[DietPlanMeal]

    