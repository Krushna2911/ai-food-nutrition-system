from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal
from app.models.nutrition import Nutrition


CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "uec_nutrition_mapping.csv"
)


def load_nutrition_mapping() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)

    required_columns = {
        "uec_id",
        "food_name",
        "fdc_id",
        "status",
        "calories_kcal",
        "carbohydrates_g",
        "fat_g",
        "protein_g",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return df


def seed_nutrition() -> None:
    df = load_nutrition_mapping()

    # Only import records with actual USDA nutrition values.
    mapped_df = df.dropna(
        subset=[
            "fdc_id",
            "calories_kcal",
            "carbohydrates_g",
            "fat_g",
            "protein_g",
        ]
    )

    db = SessionLocal()

    try:
        for row in mapped_df.itertuples(index=False):
            existing = (
                db.query(Nutrition)
                .filter(Nutrition.food_name == row.food_name)
                .first()
            )

            if existing:
                existing.serving_size_g = 100
                existing.calories = float(row.calories_kcal)
                existing.protein_g = float(row.protein_g)
                existing.carbohydrates_g = float(row.carbohydrates_g)
                existing.fat_g = float(row.fat_g)

                print(f"{row.food_name} updated")
                continue

            db.add(
                Nutrition(
                    food_name=row.food_name,
                    serving_size_g=100,
                    calories=float(row.calories_kcal),
                    protein_g=float(row.protein_g),
                    carbohydrates_g=float(row.carbohydrates_g),
                    fat_g=float(row.fat_g),
                )
            )

            print(f"{row.food_name} added")

        db.commit()

        print()
        print(f"Mapping rows: {len(df)}")
        print(f"Nutrition records imported: {len(mapped_df)}")
        print(
            f"Unresolved records skipped: "
            f"{len(df) - len(mapped_df)}"
        )
        print("Nutrition import completed successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed_nutrition()