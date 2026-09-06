from app.core.database import SessionLocal
from app.models.nutrition import Nutrition


db = SessionLocal()

try:
    rice = Nutrition(
        food_name="rice",
        serving_size_g=100,
        calories=130,
        protein_g=2.7,
        carbohydrates_g=28.2,
        fat_g=0.3,
    )

    db.add(rice)
    db.commit()

    print("Rice nutrition record inserted successfully")

finally:
    db.close()