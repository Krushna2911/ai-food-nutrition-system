
from pathlib import Path

import numpy as np
from PIL import Image

from app.services.itd_segmentation_service import ITDSegmentationService


def test_itd_checkpoint_loads_and_predicts(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    checkpoint = project_root / "ml" / "models" / "itd_segmentation_best.pt"
    class_map = project_root / "ml" / "metadata" / "itd_class_map.json"

    if not checkpoint.is_file() or not class_map.is_file():
        import pytest
        pytest.skip("ITD model assets are not available locally.")

    # A synthetic image checks execution and output structure,
    # not segmentation accuracy.
    image_path = tmp_path / "smoke_test.png"
    image = np.zeros((128, 160, 3), dtype=np.uint8)
    image[:, :, 0] = 180
    Image.fromarray(image, mode="RGB").save(image_path)

    service = ITDSegmentationService()
    assert service.load_model() is True

    result = service.predict(str(image_path))

    assert result["image_width"] == 160
    assert result["image_height"] == 128
    assert result["input_size"] == 384
    assert isinstance(result["segmentations"], list)
    assert result["label_map"].shape == (128, 160)

    for item in result["segmentations"]:
        assert 1 <= item["class_id"] <= 50
        assert item["class_name"] == service.class_map[item["class_id"]]
        assert 0 < item["pixel_count"] <= 160 * 128
        assert 0 < item["area_ratio"] <= 1
