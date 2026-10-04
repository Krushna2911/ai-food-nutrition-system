from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "food_segmentation_best.pt"


class FoodSegmentationService:
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.model = None

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Segmentation model not found: {self.model_path}"
            )

        self.model = YOLO(str(self.model_path))
        return True

    def predict(self, image_path: str):
        if self.model is None:
            raise RuntimeError("Segmentation model has not been loaded.")

        results = self.model.predict(
            source=image_path,
            device="cpu",
            verbose=False,
        )

        segmentations = []

        for result in results:
            if result.masks is None or result.boxes is None:
                continue

            for i, box in enumerate(result.boxes):
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                polygon = None

                if result.masks.xy is not None and i < len(result.masks.xy):
                    polygon = result.masks.xy[i].tolist()

                segmentations.append(
                    {
                        "class_id": class_id,
                        "class_name": self.model.names[class_id],
                        "confidence": confidence,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "polygon": polygon,
                    }
                )

        return segmentations