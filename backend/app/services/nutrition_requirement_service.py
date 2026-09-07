class NutritionRequirementService:
    def calculate_bmr(
        self,
        age: int,
        height_cm: float,
        weight_kg: float,
    ) -> float:
        return round(
            (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5,
            2,
        )

    def get_activity_multiplier(self, activity_level: str) -> float:
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }

        if activity_level not in multipliers:
            raise ValueError(
                f"Unsupported activity level: {activity_level}"
            )

        return multipliers[activity_level]

    def calculate_daily_calories(
        self,
        age: int,
        height_cm: float,
        weight_kg: float,
        activity_level: str,
        diet_goal: str,
    ) -> float:
        bmr = self.calculate_bmr(
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
        )

        activity_multiplier = self.get_activity_multiplier(
            activity_level
        )

        maintenance_calories = bmr * activity_multiplier

        goal_adjustments = {
            "weight_loss": -500,
            "maintenance": 0,
            "weight_gain": 300,
        }

        if diet_goal not in goal_adjustments:
            raise ValueError(
                f"Unsupported diet goal: {diet_goal}"
            )

        daily_calories = (
            maintenance_calories + goal_adjustments[diet_goal]
        )

        return round(daily_calories, 2)