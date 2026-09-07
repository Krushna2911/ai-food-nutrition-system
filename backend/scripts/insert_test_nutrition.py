from app.core.database import SessionLocal
from app.models.nutrition import Nutrition


nutrition_records = [
    Nutrition(
        food_name="rice",
        serving_size_g=100,
        calories=130,
        protein_g=2.7,
        carbohydrates_g=28.2,
        fat_g=0.3,
    ),
    Nutrition(
        food_name="apple",
        serving_size_g=100,
        calories=52,
        protein_g=0.3,
        carbohydrates_g=13.8,
        fat_g=0.2,
    ),
    Nutrition(
        food_name="banana",
        serving_size_g=100,
        calories=89,
        protein_g=1.1,
        carbohydrates_g=22.8,
        fat_g=0.3,
    ),
]


db = SessionLocal()

try:
    for record in nutrition_records:
        existing = (
            db.query(Nutrition)
            .filter(Nutrition.food_name == record.food_name)
            .first()
        )

        if existing:
            print(f"{record.food_name} already exists, skipping")
            continue

        db.add(record)
        print(f"{record.food_name} added")

    db.commit()
    print("Nutrition seed completed successfully")

finally:
    db.close()