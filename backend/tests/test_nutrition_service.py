from types import SimpleNamespace

import pytest

from app.services.nutrition_service import NutritionService


def test_calculate_nutrition_for_portion():
    service = NutritionService(repository=None)

    nutrition = SimpleNamespace(
        food_name="apple",
        serving_size_g=100,
        calories=52,
        protein_g=0.3,
        carbohydrates_g=13.8,
        fat_g=0.2,
    )

    result = service.calculate_nutrition(
        nutrition,
        portion_g=150,
    )

    assert result == {
        "food_name": "apple",
        "portion_g": 150,
        "calories": 78.0,
        "protein_g": 0.45,
        "carbohydrates_g": 20.7,
        "fat_g": 0.3,
    }


def test_calculate_nutrition_rejects_zero_portion():
    service = NutritionService(repository=None)

    nutrition = SimpleNamespace(
        food_name="apple",
        serving_size_g=100,
        calories=52,
        protein_g=0.3,
        carbohydrates_g=13.8,
        fat_g=0.2,
    )

    with pytest.raises(
        ValueError,
        match="Portion size must be greater than 0.",
    ):
        service.calculate_nutrition(
            nutrition,
            portion_g=0,
        )