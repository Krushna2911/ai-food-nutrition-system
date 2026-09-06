from pathlib import Path

MODEL_PATH = Path("ml/models/best.pt")


class FoodDetectionService:
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.model = None

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        # YOLO26 model loading will be added here
        # after the trained weights are available.
        return True

    def predict(self, image_path: str):
        if self.model is None:
            raise RuntimeError("YOLO model has not been loaded.")

        # Detection inference will be implemented here.
        return []