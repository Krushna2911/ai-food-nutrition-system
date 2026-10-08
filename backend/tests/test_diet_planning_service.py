from types import SimpleNamespace

import pytest

from app.services.diet_planning_service import DietPlanningService
from app.services.nutrition_service import NutritionService


def test_generate_three_meal_plan():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
    ]

    result = service.generate_plan(
        daily_calories=2000,
        dietary_preference="balanced",
        food_restrictions=None,
        nutrition_records=foods,
    )

    assert result["daily_calorie_target"] == 2000
    assert len(result["meals"]) == 3

    assert [meal["meal"] for meal in result["meals"]] == [
        "breakfast",
        "lunch",
        "dinner",
    ]

    assert all(
        all(50 <= food["portion_g"] <= 300 for food in meal["foods"])
        for meal in result["meals"]
    )      


def test_vegan_plan_excludes_animal_foods():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
        SimpleNamespace(
            food_name="beef curry",
            serving_size_g=100,
            calories=113,
            protein_g=7.57,
            carbohydrates_g=6.53,
            fat_g=6.57,
        ),
        SimpleNamespace(
            food_name="fried rice",
            serving_size_g=100,
            calories=174,
            protein_g=4.05,
            carbohydrates_g=32.79,
            fat_g=2.96,
        ),
        SimpleNamespace(
            food_name="soba noodle",
            serving_size_g=100,
            calories=99,
            protein_g=5.06,
            carbohydrates_g=21.44,
            fat_g=0.1,
        ),
    ]

    result = service.generate_plan(
        daily_calories=2000,
        dietary_preference="vegan",
        food_restrictions=None,
        nutrition_records=foods,
    )
    
    assert len(result["meals"]) == 3

    for meal in result["meals"]:
        assert all(
            food["food_name"] in {"rice", "fried rice", "soba noodle"}
            for food in meal["foods"]
        )


def test_plan_rejects_insufficient_foods():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        )
    ]

    with pytest.raises(
        ValueError,
        match="At least 3 compatible foods are required",
    ):
        service.generate_plan(
            daily_calories=2000,
            dietary_preference="balanced",
            food_restrictions=None,
            nutrition_records=foods,
        )

def test_plan_stays_close_to_daily_calorie_target():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
        SimpleNamespace(
            food_name="fried rice",
            serving_size_g=100,
            calories=174,
            protein_g=4.05,
            carbohydrates_g=32.79,
            fat_g=2.96,
        ),
        SimpleNamespace(
            food_name="roast chicken",
            serving_size_g=100,
            calories=223,
            protein_g=23.97,
            carbohydrates_g=0,
            fat_g=13.39,
        ),
    ]

    result = service.generate_plan(
        daily_calories=2000,
        dietary_preference="balanced",
        food_restrictions=None,
        nutrition_records=foods,
    )

    generated_calories = sum(
        meal["calories"] for meal in result["meals"]
    )

    assert 1800 <= generated_calories <= 2200

def test_calculate_macro_distribution():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    result = service.calculate_macro_distribution(
        calories=2000,
        protein_g=100,
        carbohydrates_g=250,
        fat_g=66.67,
    )
    
def test_macro_distribution_uses_reported_calories_as_denominator():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    # Macro-derived energy is 2,073.33 kcal,
    # while the reported food energy is 2,000 kcal.
    # AMDR percentages intentionally use the reported calorie value.
    result = service.calculate_macro_distribution(
        calories=2000,
        protein_g=125,
        carbohydrates_g=275,
        fat_g=66.67,
    )

    assert result["protein_percent"] == pytest.approx(25.0, abs=0.1)
    assert result["carbohydrates_percent"] == pytest.approx(55.0, abs=0.1)
    assert result["fat_percent"] == pytest.approx(30.0, abs=0.1)


def test_macro_distribution_is_within_amdr():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    result = service.is_within_amdr(
        calories=2000,
        protein_g=125,
        carbohydrates_g=275,
        fat_g=66.67,
    )

    assert result is True

def test_generated_plan_is_within_amdr():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)
    
    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
        SimpleNamespace(
            food_name="fried rice",
            serving_size_g=100,
            calories=174,
            protein_g=4.05,
            carbohydrates_g=32.79,
            fat_g=2.96,
        ),
        SimpleNamespace(
            food_name="potato salad",
            serving_size_g=100,
            calories=143,
            protein_g=2.68,
            carbohydrates_g=11.17,
            fat_g=9.93,
        ),
        SimpleNamespace(
            food_name="croissant",
            serving_size_g=100,
            calories=406,
            protein_g=8.2,
            carbohydrates_g=45.8,
            fat_g=21.0,
        ),
    ]

    result = service.generate_plan(
        daily_calories=2000,
        dietary_preference="balanced",
        food_restrictions=None,
        nutrition_records=foods,
    )

    total_calories = sum(
        meal["calories"] for meal in result["meals"]
    )
    total_protein = sum(
        meal["protein_g"] for meal in result["meals"]
    )
    total_carbohydrates = sum(
        meal["carbohydrates_g"] for meal in result["meals"]
    )
    total_fat = sum(
        meal["fat_g"] for meal in result["meals"]
    )

    assert service.is_within_amdr(
        calories=total_calories,
        protein_g=total_protein,
        carbohydrates_g=total_carbohydrates,
        fat_g=total_fat,
    )

def test_macro_balance_score_prefers_amdr_compliant_plan():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    compliant_score = service.calculate_macro_balance_score(
        calories=2000,
        protein_g=125,
        carbohydrates_g=275,
        fat_g=66.67,
    )

    imbalanced_score = service.calculate_macro_balance_score(
        calories=2000,
        protein_g=124.66,
        carbohydrates_g=183.34,
        fat_g=78.18,
    )

    assert compliant_score < imbalanced_score

def test_food_portion_calculation_returns_valid_nutrition():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    food = SimpleNamespace(
        food_name="rice",
        serving_size_g=100,
        calories=130,
        protein_g=2.69,
        carbohydrates_g=28.17,
        fat_g=0.28,
    )

    nutrition = service.calculate_food_portion(
        food=food,
        portion_g=200,
    )

    assert nutrition["food_name"] == "rice"
    assert nutrition["portion_g"] == 200
    assert nutrition["calories"] == 260
    assert nutrition["protein_g"] == 5.38
    assert nutrition["carbohydrates_g"] == 56.34
    assert nutrition["fat_g"] == 0.56

def test_food_candidate_score_prefers_better_macro_balance():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    rice = SimpleNamespace(
        food_name="rice",
        serving_size_g=100,
        calories=130,
        protein_g=2.69,
        carbohydrates_g=28.17,
        fat_g=0.28,
    )

    grilled_salmon = SimpleNamespace(
        food_name="grilled salmon",
        serving_size_g=100,
        calories=259,
        protein_g=25.92,
        carbohydrates_g=0,
        fat_g=16.48,
    )

    rice_score = service.calculate_food_candidate_score(
        food=rice,
        portion_g=200,
        target_calories=500,
    )

    salmon_score = service.calculate_food_candidate_score(
        food=grilled_salmon,
        portion_g=200,
        target_calories=500,
    )

    assert rice_score != salmon_score

def test_feasible_plan_check():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    assert service.is_feasible_plan(
        calories=2000,
        protein_g=125,
        carbohydrates_g=250,
        fat_g=66.67,
        target_calories=2000,
    )

    assert not service.is_feasible_plan(
        calories=2000,
        protein_g=160,
        carbohydrates_g=100,
        fat_g=100,
        target_calories=2000,
    )

def test_find_best_food_combination():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
        SimpleNamespace(
            food_name="fried rice",
            serving_size_g=100,
            calories=174,
            protein_g=4.05,
            carbohydrates_g=32.79,
            fat_g=2.96,
        ),
    ]

    result = service.find_best_food_combination(
        foods=foods,
        target_calories=500,
    )

    assert len(result) == 2
    assert all(food["portion_g"] >= 50 for food in result)
    assert all(food["portion_g"] <= 300 for food in result)

def test_find_best_three_food_combination():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
        SimpleNamespace(
            food_name="fried rice",
            serving_size_g=100,
            calories=174,
            protein_g=4.05,
            carbohydrates_g=32.79,
            fat_g=2.96,
        ),
    ]

    result = service.find_best_three_food_combination(
        foods=foods,
        target_calories=1000,
    )

    assert len(result) == 3
    assert len({food["food_name"] for food in result}) == 3
    assert all(50 <= food["portion_g"] <= 300 for food in result)
    
    
def test_generated_plan_allows_food_reuse_across_meals():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="fermented soybeans",
            serving_size_g=100,
            calories=211,
            protein_g=19.4,
            carbohydrates_g=12.68,
            fat_g=11.0,
        ),
        SimpleNamespace(
            food_name="pilaf",
            serving_size_g=100,
            calories=148,
            protein_g=2.94,
            carbohydrates_g=25.67,
            fat_g=3.7,
        ),
    ]

    result = service.generate_plan(
        daily_calories=1200,
        nutrition_records=foods,
        dietary_preference="balanced",
        food_restrictions=None,
    )

    food_names_by_meal = [
        food["food_name"]
        for meal in result["meals"]
        for food in meal["foods"]
    ]

    assert len(food_names_by_meal) > len(set(food_names_by_meal))
    
def test_food_restriction_excludes_beef():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="beef curry",
            serving_size_g=100,
            calories=113,
            protein_g=7.57,
            carbohydrates_g=6.53,
            fat_g=6.57,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
    ]

    filtered_foods = service._filter_foods(
        nutrition_records=foods,
        dietary_preference="balanced",
        food_restrictions="beef",
    )

    assert [food.food_name for food in filtered_foods] == [
        "rice",
        "grilled salmon",
    ]
    
def test_generated_plan_excludes_beef_when_restricted():
    nutrition_service = NutritionService(repository=None)
    service = DietPlanningService(nutrition_service)

    foods = [
        SimpleNamespace(
            food_name="rice",
            serving_size_g=100,
            calories=130,
            protein_g=2.69,
            carbohydrates_g=28.17,
            fat_g=0.28,
        ),
        SimpleNamespace(
            food_name="beef curry",
            serving_size_g=100,
            calories=113,
            protein_g=7.57,
            carbohydrates_g=6.53,
            fat_g=6.57,
        ),
        SimpleNamespace(
            food_name="grilled salmon",
            serving_size_g=100,
            calories=259,
            protein_g=25.92,
            carbohydrates_g=0,
            fat_g=16.48,
        ),
        SimpleNamespace(
            food_name="omelet",
            serving_size_g=100,
            calories=154,
            protein_g=10.57,
            carbohydrates_g=0.64,
            fat_g=11.66,
        ),
    ]

    result = service.generate_plan(
        daily_calories=2000,
        dietary_preference="balanced",
        food_restrictions="beef",
        nutrition_records=foods,
    )

    food_names = [
        food["food_name"]
        for meal in result["meals"]
        for food in meal["foods"]
    ]

    assert all("beef" not in food_name.lower() for food_name in food_names)