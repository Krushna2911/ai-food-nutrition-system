from pydantic import BaseModel
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import unicodedata

from app.repositories.nutrition_repository import NutritionRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.services.diet_planning_service import DietPlanningService
from app.services.nutrition_requirement_service import NutritionRequirementService
from app.services.nutrition_service import NutritionService


class RecommendationState(BaseModel):
    profile_id: int
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str
    diet_goal: str
    dietary_preference: str
    food_restrictions: str | None

    daily_calorie_target: float

    total_calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    amdr_compliant: bool

    meals: list[dict]
    recommendation: str | None = None


class RecommendationService:
    def __init__(self):
        nutrition_service = NutritionService(NutritionRepository())
        self.nutrition_requirement_service = NutritionRequirementService()
        self.diet_planning_service = DietPlanningService(nutrition_service)
        self.nutrition_repository = NutritionRepository()
        self.user_profile_repository = UserProfileRepository()
        
        load_dotenv()

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )
        
    def build_graph(self):
        graph = StateGraph(RecommendationState)

        graph.add_node("prepare", lambda state: state)
        graph.add_node("recommendation", self.generate_recommendation)

        graph.add_edge(START, "prepare")
        graph.add_edge("prepare", "recommendation")
        graph.add_edge("recommendation", END)

        return graph.compile()

    def build_state(self, db, profile_id: int) -> RecommendationState:
        profile = self.user_profile_repository.get_by_id(db, profile_id)

        if profile is None:
            raise ValueError(f"Profile {profile_id} not found.")

        daily_calorie_target = (
            self.nutrition_requirement_service.calculate_daily_calories(
                age=profile.age,
                height_cm=profile.height_cm,
                weight_kg=profile.weight_kg,
                activity_level=profile.activity_level,
                diet_goal=profile.diet_goal,
            )
        )

        nutrition_records = self.nutrition_repository.get_all(db)

        diet_plan = self.diet_planning_service.generate_plan(
            daily_calories=daily_calorie_target,
            dietary_preference=profile.dietary_preference,
            food_restrictions=profile.food_restrictions,
            nutrition_records=nutrition_records,
        )

        return RecommendationState(
            profile_id=profile.id,
            age=profile.age,
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            activity_level=profile.activity_level,
            diet_goal=profile.diet_goal,
            dietary_preference=profile.dietary_preference,
            food_restrictions=profile.food_restrictions,
            daily_calorie_target=diet_plan["daily_calorie_target"],
            total_calories=diet_plan["total_calories"],
            protein_g=diet_plan["protein_g"],
            carbohydrates_g=diet_plan["carbohydrates_g"],
            fat_g=diet_plan["fat_g"],
            amdr_compliant=diet_plan["amdr_compliant"],
            meals=diet_plan["meals"],
        )
        
    def generate_recommendation(self, state: RecommendationState) -> RecommendationState:
        prompt = f"""
            You are a diet-plan explanation assistant.

            Your job is to explain the already-validated diet plan below.

            STRICT RULES:
            - Do not calculate or modify calories, macronutrients, portions, or AMDR.
            - Do not introduce foods that are not present in the validated plan.
            - Do not claim that a food is "healthy", "unhealthy", "clean", "optimal", or medically beneficial.
            - Do not make medical, disease-prevention, treatment, or clinical claims.
            - Do not claim that the plan guarantees weight loss, weight gain, muscle gain, or any other outcome.
            - Do not invent nutritional facts.
            - Only mention numerical values that are explicitly provided below.
            - If something cannot be established from the provided data, do not claim it.

            User profile:
            - Age: {state.age}
            - Height: {state.height_cm} cm
            - Weight: {state.weight_kg} kg
            - Activity level: {state.activity_level}
            - Diet goal: {state.diet_goal}
            - Dietary preference: {state.dietary_preference}
            - Food restrictions: {state.food_restrictions or "None"}

            Validated daily diet plan:
            - Daily calorie target: {state.daily_calorie_target} kcal
            - Total calories: {state.total_calories} kcal
            - Protein: {state.protein_g} g
            - Carbohydrates: {state.carbohydrates_g} g
            - Fat: {state.fat_g} g
            - AMDR compliant: {state.amdr_compliant}

            Validated meals:
            {state.meals}

            Provide a concise response with exactly three sections:

            1. Plan summary
            Explain how the total calories compare with the daily calorie target and state whether the validated plan is AMDR compliant.

            2. Meal distribution
            Briefly describe the calorie and macro distribution across breakfast, lunch, and dinner using only the provided meal data.

            3. Practical adherence tips
            Give 1-2 practical tips about following the portions and meals in this plan. Do not introduce new foods or nutritional claims.

            Keep the response factual and concise.

            OUTPUT FORMAT RULES:
            - Use plain ASCII spaces only.
            - Do not use non-breaking spaces or special Unicode spacing characters.
            - Use standard Markdown only.
            - Write units normally, such as "2468.5 kcal" and "150 g".
            """
        response = self.llm.invoke(prompt)

        recommendation = unicodedata.normalize("NFKC", response.content)
        recommendation = recommendation.replace("\u00a0", " ")
        recommendation = recommendation.replace("\u202f", " ")
        recommendation = recommendation.encode("ascii", "ignore").decode("ascii")

        return state.model_copy(
            update={"recommendation": recommendation}
        )