
import pandas as pd

from scripts.import_nutrition_mapping import (
    get_verified_nutrition_rows,
    load_nutrition_mapping,
)

def test_only_verified_rows_with_complete_nutrients_are_selected():
    df = load_nutrition_mapping()
    verified = get_verified_nutrition_rows(df)

    assert len(verified) == 1
    assert verified.iloc[0]["food_name"] == "rice"
    assert verified.iloc[0]["fdc_id"] == 169757

 
def test_strong_candidates_are_not_selected():
    df = pd.DataFrame(
        [
            {
                "food_name": "rice",
                "status": "verified",
                "fdc_id": 169757,
                "calories_kcal": 130,
                "carbohydrates_g": 28.17,
                "fat_g": 0.28,
                "protein_g": 2.69,
            },
            {
                "food_name": "candidate food",
                "status": "strong_candidate",
                "fdc_id": 12345,
                "calories_kcal": 200,
                "carbohydrates_g": 20,
                "fat_g": 5,
                "protein_g": 10,
            },
        ]
    )

    selected = get_verified_nutrition_rows(df)

    assert selected["food_name"].tolist() == ["rice"]
