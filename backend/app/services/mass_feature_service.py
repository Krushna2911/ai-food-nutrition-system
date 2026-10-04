from pathlib import Path

import numpy as np
from PIL import Image


class MassFeatureService:
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

    @staticmethod
    def extract_features(
        rgb_path: str,
        depth_path: str,
    ) -> dict:
        rgb_image = Image.open(Path(rgb_path)).convert("RGB")
        depth_image = Image.open(Path(depth_path))

        rgb = np.asarray(rgb_image)
        depth = np.asarray(depth_image)

        if rgb.shape[:2] != depth.shape[:2]:
            raise ValueError(
                "RGB and depth images must have the same dimensions."
            )

        rgb_float = rgb.astype(np.float32)

        valid_depth = depth[depth > 0]

        if valid_depth.size == 0:
            raise ValueError(
                "Depth image contains no valid depth pixels."
            )

        features = {
            "rgb_mean": float(rgb_float.mean()),
            "rgb_std": float(rgb_float.std()),
            "depth_valid_ratio": float(
                valid_depth.size / depth.size
            ),
            "depth_mean": float(valid_depth.mean()),
            "depth_median": float(np.median(valid_depth)),
            "depth_std": float(valid_depth.std()),
            "depth_min": float(valid_depth.min()),
            "depth_max": float(valid_depth.max()),
        }

        return features