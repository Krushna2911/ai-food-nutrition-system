
import json

import pytest

from app.services.itd_segmentation_service import ITDSegmentationService


def test_load_model_rejects_missing_checkpoint(tmp_path):
    class_map_path = tmp_path / "class_map.json"
    class_map_path.write_text(
        json.dumps({str(i): f"class_{i}" for i in range(51)}),
        encoding="utf-8",
    )

    service = ITDSegmentationService(
        model_path=str(tmp_path / "missing.pt"),
        class_map_path=str(class_map_path),
    )

    with pytest.raises(FileNotFoundError, match="checkpoint not found"):
        service.load_model()


def test_load_model_rejects_missing_class_map(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.pt"
    checkpoint_path.touch()

    service = ITDSegmentationService(
        model_path=str(checkpoint_path),
        class_map_path=str(tmp_path / "missing.json"),
    )

    with pytest.raises(FileNotFoundError, match="class map not found"):
        service.load_model()


def test_predict_rejects_unloaded_model():
    service = ITDSegmentationService()

    with pytest.raises(
        RuntimeError,
        match="ITD segmentation model has not been loaded",
    ):
        service.predict("unused-image.jpg")
