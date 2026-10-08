from app.services.recommendation_service import (
    RecommendationService,
    RecommendationState,
)


def test_generate_recommendation_updates_state(monkeypatch):
    service = RecommendationService()

    class FakeResponse:
        content = "Validated recommendation."

    def fake_invoke(prompt):
        return FakeResponse()

    monkeypatch.setattr(
        type(service.llm),
        "invoke",
        lambda self, prompt: fake_invoke(prompt),
    )

    state = RecommendationState(
        profile_id=2,
        age=25,
        height_cm=170,
        weight_kg=70,
        activity_level="moderate",
        diet_goal="maintenance",
        dietary_preference="balanced",
        food_restrictions=None,
        daily_calorie_target=2000,
        total_calories=2000,
        protein_g=100,
        carbohydrates_g=250,
        fat_g=66.67,
        amdr_compliant=True,
        meals=[
            {
                "meal": "breakfast",
                "foods": [],
                "calories": 500,
                "protein_g": 25,
                "carbohydrates_g": 60,
                "fat_g": 15,
            }
        ],
    )

    result = service.generate_recommendation(state)

    assert result.recommendation == "Validated recommendation."