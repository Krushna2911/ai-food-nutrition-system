from typing import Iterable
import itertools
import bisect


class DietPlanningService:
    def __init__(self, nutrition_service):
        self.nutrition_service = nutrition_service
     
    def generate_plan(
        self,
        daily_calories: float,
        dietary_preference: str,
        food_restrictions: str | None,
        nutrition_records: Iterable,
    ) -> dict:
        if daily_calories <= 0:
            raise ValueError("Daily calories must be greater than 0.")

        foods = self._filter_foods(
            nutrition_records=nutrition_records,
            dietary_preference=dietary_preference,
            food_restrictions=food_restrictions,
        )

        if len(foods) < 3:
            raise ValueError(
                "At least 3 compatible foods are required to generate a plan."
            )

        meal_targets = {
            "breakfast": daily_calories * 0.25,
            "lunch": daily_calories * 0.40,
            "dinner": daily_calories * 0.35,
        }

        meal_names = ["breakfast", "lunch", "dinner"]
        portion_values = range(50, 301, 25)

        # Build candidate meals.
        #
        # Each meal can contain one or two foods. Foods may be reused
        # across meals. This is important because the available nutrition
        # records may not contain enough distinct foods to reach the
        # daily calorie target.
        meal_candidates = {}

        for meal_name in meal_names:
            target = meal_targets[meal_name]
            candidates = []

            # One-food meals
            for food in foods:
                for portion in portion_values:
                    nutrition = self.calculate_food_portion(
                        food=food,
                        portion_g=portion,
                    )

                    candidates.append(
                        {
                            "foods": [nutrition],
                            "calories": nutrition["calories"],
                            "protein_g": nutrition["protein_g"],
                            "carbohydrates_g": nutrition["carbohydrates_g"],
                            "fat_g": nutrition["fat_g"],
                            "target_error": abs(
                                nutrition["calories"] - target
                            ),
                        }
                    )

            # Two-food meals
            for first_index, first_food in enumerate(foods):
                for second_food in foods[first_index + 1:]:
                    for first_portion in portion_values:
                        first = self.calculate_food_portion(
                            food=first_food,
                            portion_g=first_portion,
                        )

                        for second_portion in portion_values:
                            second = self.calculate_food_portion(
                                food=second_food,
                                portion_g=second_portion,
                            )

                            calories = (
                                first["calories"]
                                + second["calories"]
                            )

                            candidates.append(
                                {
                                    "foods": [first, second],
                                    "calories": calories,
                                    "protein_g": (
                                        first["protein_g"]
                                        + second["protein_g"]
                                    ),
                                    "carbohydrates_g": (
                                        first["carbohydrates_g"]
                                        + second["carbohydrates_g"]
                                    ),
                                    "fat_g": (
                                        first["fat_g"]
                                        + second["fat_g"]
                                    ),
                                    "target_error": abs(
                                        calories - target
                                    ),
                                }
                            )

            # Keep a sufficiently large candidate pool so that the
            # whole-day optimizer has macro-diverse choices.
            candidates.sort(key=lambda item: item["target_error"])
            meal_candidates[meal_name] = candidates[:150]

        best_plan = None
        best_score = float("inf")

        # Dinner candidates are sorted by calorie value so that, for each
        # breakfast/lunch combination, we only evaluate dinner candidates
        # near the remaining calorie requirement.
        dinner_by_calories = sorted(
            meal_candidates["dinner"],
            key=lambda item: item["calories"],
        )

        dinner_calories = [
            item["calories"]
            for item in dinner_by_calories
        ]

        # Evaluate a small neighborhood around the closest dinner calorie.
        # This preserves macro-diverse candidates while avoiding the full
        # 150 x 150 x 150 Cartesian product.
        neighbor_count = 10

        for breakfast in meal_candidates["breakfast"]:
            for lunch in meal_candidates["lunch"]:
                partial_calories = (
                    breakfast["calories"]
                    + lunch["calories"]
                )

                remaining_calories = daily_calories - partial_calories

                insertion_index = bisect.bisect_left(
                    dinner_calories,
                    remaining_calories,
                )

                start_index = max(
                    0,
                    insertion_index - neighbor_count,
                )

                end_index = min(
                    len(dinner_by_calories),
                    insertion_index + neighbor_count + 1,
                )

                for dinner in dinner_by_calories[start_index:end_index]:
                    total_calories = (
                        partial_calories
                        + dinner["calories"]
                    )

                    calorie_error = abs(
                        total_calories - daily_calories
                    )

                    protein_g = (
                        breakfast["protein_g"]
                        + lunch["protein_g"]
                        + dinner["protein_g"]
                    )

                    carbohydrates_g = (
                        breakfast["carbohydrates_g"]
                        + lunch["carbohydrates_g"]
                        + dinner["carbohydrates_g"]
                    )

                    fat_g = (
                        breakfast["fat_g"]
                        + lunch["fat_g"]
                        + dinner["fat_g"]
                    )

                    amdr_compliant = self.is_within_amdr(
                        calories=total_calories,
                        protein_g=protein_g,
                        carbohydrates_g=carbohydrates_g,
                        fat_g=fat_g,
                    )

                    macro_penalty = self.calculate_macro_balance_score(
                        calories=total_calories,
                        protein_g=protein_g,
                        carbohydrates_g=carbohydrates_g,
                        fat_g=fat_g,
                    )

                    score = (
                        calorie_error
                        + (1000 if not amdr_compliant else 0)
                        + (10 * macro_penalty)
                    )

                    if score < best_score:
                        best_score = score

                        best_plan = {
                            "breakfast": breakfast,
                            "lunch": lunch,
                            "dinner": dinner,
                            "calories": total_calories,
                            "protein_g": protein_g,
                            "carbohydrates_g": carbohydrates_g,
                            "fat_g": fat_g,
                            "amdr_compliant": amdr_compliant,
                        }

        if best_plan is None:
            raise ValueError(
                "Unable to generate a nutrition-aware diet plan "
                "with the available food records."
            )

        meals = []

        for meal_name in meal_names:
            meal = best_plan[meal_name]

            meals.append(
                {
                    "meal": meal_name,
                    "calories": round(meal["calories"], 2),
                    "protein_g": round(meal["protein_g"], 2),
                    "carbohydrates_g": round(
                        meal["carbohydrates_g"],
                        2,
                    ),
                    "fat_g": round(meal["fat_g"], 2),
                    "foods": meal["foods"],
                }
            )

        return {
            "daily_calorie_target": round(daily_calories, 2),
            "total_calories": round(best_plan["calories"], 2),
            "protein_g": round(best_plan["protein_g"], 2),
            "carbohydrates_g": round(
                best_plan["carbohydrates_g"],
                2,
            ),
            "fat_g": round(best_plan["fat_g"], 2),
            "amdr_compliant": best_plan["amdr_compliant"],
            "meals": meals,
        }
    
    def calculate_macro_distribution(
        self,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
    ) -> dict:
        if calories <= 0:
            raise ValueError("Calories must be greater than 0.")

        protein_percent = (protein_g * 4 / calories) * 100
        carbohydrates_percent = (carbohydrates_g * 4 / calories) * 100
        fat_percent = (fat_g * 9 / calories) * 100

        return {
            "protein_percent": round(protein_percent, 2),
            "carbohydrates_percent": round(carbohydrates_percent, 2),
            "fat_percent": round(fat_percent, 2),
        }

    def is_within_amdr(
        self,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
    ) -> bool:
        distribution = self.calculate_macro_distribution(
            calories=calories,
            protein_g=protein_g,
            carbohydrates_g=carbohydrates_g,
            fat_g=fat_g,
        )

        return (
            10.0 <= distribution["protein_percent"] <= 35.0
            and 45.0 <= distribution["carbohydrates_percent"] <= 65.0
            and 20.0 <= distribution["fat_percent"] <= 35.0
        )
    def calculate_macro_balance_score(
        self,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
    ) -> float:
        distribution = self.calculate_macro_distribution(
            calories=calories,
            protein_g=protein_g,
            carbohydrates_g=carbohydrates_g,
            fat_g=fat_g,
        )

        protein_percent = distribution["protein_percent"]
        carbohydrates_percent = distribution["carbohydrates_percent"]
        fat_percent = distribution["fat_percent"]

        protein_penalty = self._range_penalty(
            protein_percent,
            minimum=10.0,
            maximum=35.0,
        )

        carbohydrates_penalty = self._range_penalty(
            carbohydrates_percent,
            minimum=45.0,
            maximum=65.0,
        )

        fat_penalty = self._range_penalty(
            fat_percent,
            minimum=20.0,
            maximum=35.0,
        )

        return round(
            protein_penalty
            + carbohydrates_penalty
            + fat_penalty,
            4,
        )


    def calculate_plan_score(
        self,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
        target_calories: float,
    ) -> float:
        if calories <= 0:
            raise ValueError("Calories must be greater than 0.")

        calorie_error = abs(calories - target_calories)

        macro_penalty = self.calculate_macro_balance_score(
            calories=calories,
            protein_g=protein_g,
            carbohydrates_g=carbohydrates_g,
            fat_g=fat_g,
        )

        return round(
            calorie_error + (macro_penalty * 10.0),
            4,
        )

    def find_best_food_combination(
        self,
        foods: list,
        target_calories: float,
        minimum_portion_g: float = 50.0,
        maximum_portion_g: float = 300.0,
        portion_step_g: float = 25.0,
    ) -> list[dict]:
        best_plan = None
        best_score = None

        for first_index, first_food in enumerate(foods):
            for second_index in range(first_index + 1, len(foods)):
                second_food = foods[second_index]

                for first_portion in range(
                    int(minimum_portion_g),
                    int(maximum_portion_g) + 1,
                    int(portion_step_g),
                ):
                    first_nutrition = self.calculate_food_portion(
                        food=first_food,
                        portion_g=first_portion,
                    )

                    for second_portion in range(
                        int(minimum_portion_g),
                        int(maximum_portion_g) + 1,
                        int(portion_step_g),
                    ):
                        second_nutrition = self.calculate_food_portion(
                            food=second_food,
                            portion_g=second_portion,
                        )

                        total_calories = (
                            first_nutrition["calories"]
                            + second_nutrition["calories"]
                        )

                        total_protein = (
                            first_nutrition["protein_g"]
                            + second_nutrition["protein_g"]
                        )

                        total_carbohydrates = (
                            first_nutrition["carbohydrates_g"]
                            + second_nutrition["carbohydrates_g"]
                        )

                        total_fat = (
                            first_nutrition["fat_g"]
                            + second_nutrition["fat_g"]
                            
                        )

                        if abs(total_calories - target_calories) > 50.0:
                            continue

                        if not self.is_within_amdr(
                            calories=total_calories,
                            protein_g=total_protein,
                            carbohydrates_g=total_carbohydrates,
                            fat_g=total_fat,
                        ):
                            continue

                        score = self.calculate_plan_score(
                            calories=total_calories,
                            protein_g=total_protein,
                            carbohydrates_g=total_carbohydrates,
                            fat_g=total_fat,
                            target_calories=target_calories,
                        )

                        if best_score is None or score < best_score:
                            best_score = score
                            best_plan = [
                                first_nutrition,
                                second_nutrition,
                            ]

        return best_plan or []
    def find_best_three_food_combination(
        self,
        foods: list,
        target_calories: float,
        minimum_portion_g: float = 50.0,
        maximum_portion_g: float = 300.0,
        portion_step_g: float = 25.0,
    ) -> list[dict]:
        best_plan = None
        best_score = None

        for first_index, first_food in enumerate(foods):
            for second_index in range(first_index + 1, len(foods)):
                second_food = foods[second_index]

                for third_index in range(second_index + 1, len(foods)):
                    third_food = foods[third_index]

                    for first_portion in range(
                        int(minimum_portion_g),
                        int(maximum_portion_g) + 1,
                        int(portion_step_g),
                    ):
                        first_nutrition = self.calculate_food_portion(
                            food=first_food,
                            portion_g=first_portion,
                        )

                        for second_portion in range(
                            int(minimum_portion_g),
                            int(maximum_portion_g) + 1,
                            int(portion_step_g),
                        ):
                            second_nutrition = self.calculate_food_portion(
                                food=second_food,
                                portion_g=second_portion,
                            )

                            for third_portion in range(
                                int(minimum_portion_g),
                                int(maximum_portion_g) + 1,
                                int(portion_step_g),
                            ):
                                third_nutrition = self.calculate_food_portion(
                                    food=third_food,
                                    portion_g=third_portion,
                                )

                                total_calories = (
                                    first_nutrition["calories"]
                                    + second_nutrition["calories"]
                                    + third_nutrition["calories"]
                                )

                                total_protein = (
                                    first_nutrition["protein_g"]
                                    + second_nutrition["protein_g"]
                                    + third_nutrition["protein_g"]
                                )

                                total_carbohydrates = (
                                    first_nutrition["carbohydrates_g"]
                                    + second_nutrition["carbohydrates_g"]
                                    + third_nutrition["carbohydrates_g"]
                                )

                                total_fat = (
                                    first_nutrition["fat_g"]
                                    + second_nutrition["fat_g"]
                                    + third_nutrition["fat_g"]
                                )
                                
                                if abs(total_calories - target_calories) > 50.0:
                                    continue

                                if not self.is_within_amdr(
                                    calories=total_calories,
                                    protein_g=total_protein,
                                    carbohydrates_g=total_carbohydrates,
                                    fat_g=total_fat,
                                ):
                                    continue

                                score = self.calculate_plan_score(
                                    calories=total_calories,
                                    protein_g=total_protein,
                                    carbohydrates_g=total_carbohydrates,
                                    fat_g=total_fat,
                                    target_calories=target_calories,
                                )

                                if best_score is None or score < best_score:
                                    best_score = score
                                    best_plan = [
                                        first_nutrition,
                                        second_nutrition,
                                        third_nutrition,
                                    ]

        return best_plan or []

    def is_feasible_plan(
        self,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
        target_calories: float,
        calorie_tolerance: float = 50.0,
    ) -> bool:
        if calories <= 0:
            return False

        if abs(calories - target_calories) > calorie_tolerance:
            return False

        return self.is_within_amdr(
            calories=calories,
            protein_g=protein_g,
            carbohydrates_g=carbohydrates_g,
            fat_g=fat_g,
        )

    @staticmethod
    def _range_penalty(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        if value < minimum:
            return minimum - value

        if value > maximum:
            return value - maximum

        return 0.0

    def calculate_food_portion(
        self,
        food,
        portion_g: float,
    ) -> dict:
        if portion_g <= 0:
            raise ValueError("Portion size must be greater than 0.")

        return self.nutrition_service.calculate_nutrition(
            food,
            portion_g,
        )

    def calculate_food_candidate_score(
        self,
        food,
        portion_g: float,
        target_calories: float,
    ) -> float:
        nutrition = self.calculate_food_portion(
            food=food,
            portion_g=portion_g,
        )

        calorie_error = abs(
            nutrition["calories"] - target_calories
        )

        macro_score = self.calculate_macro_balance_score(
            calories=max(nutrition["calories"], 1.0),
            protein_g=nutrition["protein_g"],
            carbohydrates_g=nutrition["carbohydrates_g"],
            fat_g=nutrition["fat_g"],
        )

        return round(
            calorie_error + macro_score,
            4,
        )
    def _filter_foods(
        self,
        nutrition_records: Iterable,
        dietary_preference: str,
        food_restrictions: str | None,
    ) -> list:
        restrictions = {
            item.strip().lower()
            for item in (food_restrictions or "").split(",")
            if item.strip()
        }
        
        if "beef" in restrictions:
            restrictions.update({"hamburger", "meat sauce"})

        foods = []

        for food in nutrition_records:
            food_name = food.food_name.lower()

            if any(restriction in food_name for restriction in restrictions):
                continue

            if dietary_preference == "vegan":
                if any(
                    keyword in food_name
                    for keyword in [
                        "beef",
                        "chicken",
                        "fish",
                        "salmon",
                        "shrimp",
                        "pork",
                        "egg",
                        "omelet",
                        "milk",
                    ]
                ):
                    continue

            elif dietary_preference == "vegetarian":
                if any(
                    keyword in food_name
                    for keyword in [
                        "beef",
                        "chicken",
                        "fish",
                        "salmon",
                        "shrimp",
                        "pork",
                    ]
                ):
                    continue

            foods.append(food)

        return foods