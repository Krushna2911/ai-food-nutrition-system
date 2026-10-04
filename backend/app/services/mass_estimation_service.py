from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "random_forest_mass.joblib"
)


FEATURE_COLUMNS = [
    "rgb_mean",
    "rgb_std",
    "depth_valid_ratio",
    "depth_mean",
    "depth_median",
    "depth_std",
    "depth_min",
    "depth_max",
]


class MassEstimationService:
    def __init__(self, model_path: str | None = None):
        self.model_path = (
            Path(model_path)
            if model_path
            else MODEL_PATH
        )
        self.model = None

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Mass estimation model not found: {self.model_path}"
            )

        self.model = joblib.load(self.model_path)
        return True

    def predict(self, features: dict) -> float:
        if self.model is None:
            raise RuntimeError(
                "Mass estimation model has not been loaded."
            )

        row = {
            column: features[column]
            for column in FEATURE_COLUMNS
        }

        input_data = pd.DataFrame(
            [row],
            columns=FEATURE_COLUMNS,
        )

        prediction = self.model.predict(input_data)[0]

        return float(prediction)