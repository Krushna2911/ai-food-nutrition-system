
from pathlib import Path
import json

import numpy as np
import torch
from PIL import Image
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "itd_segmentation_best.pt"
CLASS_MAP_PATH = PROJECT_ROOT / "ml" / "metadata" / "itd_class_map.json"

INPUT_SIZE = 384

# Initial preprocessing assumption: RGB values scaled to [0, 1].
# Confirm against the original training code before production use.
CHANNEL_MEAN = (0.485, 0.456, 0.406)
CHANNEL_STD = (0.229, 0.224, 0.225)


class ITDSegmentationService:
    """Torchvision DeepLabV3 segmentation service for the ITD dataset."""

    def __init__(
        self,
        model_path: str | None = None,
        class_map_path: str | None = None,
    ):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.class_map_path = (
            Path(class_map_path) if class_map_path else CLASS_MAP_PATH
        )
        self.model = None
        self.class_map: dict[int, str] = {}

        self.mean = torch.tensor(CHANNEL_MEAN).view(1, 3, 1, 1)
        self.std = torch.tensor(CHANNEL_STD).view(1, 3, 1, 1)

    def load_model(self):
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"ITD segmentation checkpoint not found: {self.model_path}"
            )

        if not self.class_map_path.is_file():
            raise FileNotFoundError(
                f"ITD class map not found: {self.class_map_path}"
            )

        with self.class_map_path.open("r", encoding="utf-8") as file:
            raw_map = json.load(file)

        self.class_map = {int(key): str(value) for key, value in raw_map.items()}

        checkpoint = torch.load(
            self.model_path,
            map_location="cpu",
            weights_only=False,
        )

        num_classes = int(checkpoint["num_classes"])
        checkpoint_input_size = int(checkpoint["input_size"])

        if num_classes != len(self.class_map):
            raise ValueError(
                f"Checkpoint has {num_classes} classes, "
                f"but class map has {len(self.class_map)} entries."
            )

        if set(self.class_map) != set(range(num_classes)):
            raise ValueError("Class map IDs are not contiguous from 0.")

        if checkpoint_input_size != INPUT_SIZE:
            raise ValueError(
                f"Expected input size {INPUT_SIZE}, "
                f"got {checkpoint_input_size}."
            )

        model = deeplabv3_mobilenet_v3_large(
            weights=None,
            weights_backbone=None,
            num_classes=num_classes,
        )
        model.load_state_dict(checkpoint["model_state_dict"], strict=True)
        model.eval()

        self.model = model
        return True

    def predict(self, image_path: str):
        if self.model is None:
            raise RuntimeError("ITD segmentation model has not been loaded.")

        image_path = Path(image_path)
        if not image_path.is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with Image.open(image_path) as source:
            image = source.convert("RGB")

        original_width, original_height = image.size

        # Resize to the checkpoint's input size.
        resized = image.resize(
            (INPUT_SIZE, INPUT_SIZE),
            resample=Image.Resampling.BILINEAR,
        )

        image_array = np.asarray(resized, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
        tensor = (tensor - self.mean) / self.std

        with torch.inference_mode():
            output = self.model(tensor)["out"]
            prediction = output.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

        # Restore the label map to the original image dimensions.
        label_image = Image.fromarray(prediction, mode="L")
        label_image = label_image.resize(
            (original_width, original_height),
            resample=Image.Resampling.NEAREST,
        )
        label_map = np.asarray(label_image)

        total_pixels = int(label_map.size)
        segmentations = []

        for class_id in sorted(int(value) for value in np.unique(label_map)):
            if class_id == 0:
                # Background is useful for masks but isn't a food item.
                continue

            class_mask = label_map == class_id
            pixel_count = int(np.count_nonzero(class_mask))

            if pixel_count == 0:
                continue

            ys, xs = np.where(class_mask)

            segmentations.append(
                {
                    "class_id": class_id,
                    "class_name": self.class_map[class_id],
                    "pixel_count": pixel_count,
                    "area_ratio": pixel_count / total_pixels,
                    "x1": int(xs.min()),
                    "y1": int(ys.min()),
                    "x2": int(xs.max()) + 1,
                    "y2": int(ys.max()) + 1,
                }
            )

        return {
            "image_width": original_width,
            "image_height": original_height,
            "input_size": INPUT_SIZE,
            "segmentations": segmentations,
            "label_map": label_map,
        }
