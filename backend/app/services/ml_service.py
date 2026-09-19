from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "best.pt"


class FoodDetectionService:
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.model = None

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        self.model = YOLO(str(self.model_path))
        return True

    def predict(self, image_path: str):
        if self.model is None:
            raise RuntimeError("YOLO model has not been loaded.")

        results = self.model.predict(
            source=image_path,
            device="cpu",
            verbose=False,
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": self.model.names[class_id],
                        "confidence": confidence,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    }
                )

        return detections