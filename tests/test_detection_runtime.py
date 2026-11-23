from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from detection.yolo import _UltralyticsPredictor, inspect_local_yolo_model


@dataclass
class FakeModel:
    names: dict[int, str]


def test_missing_weights_fail_before_the_loader_can_run(tmp_path):
    called = False

    def loader(path: str):
        nonlocal called
        called = True
        raise AssertionError(path)

    with pytest.raises(FileNotFoundError, match="Automatic model downloads are disabled"):
        inspect_local_yolo_model(tmp_path / "missing.pt", loader=loader)
    assert not called


def test_local_model_report_contains_explicit_provenance_and_labels(tmp_path):
    weights = tmp_path / "approved-football.pt"
    weights.touch()

    info = inspect_local_yolo_model(
        weights,
        loader=lambda path: FakeModel({0: "person", 32: "sports ball"}),
    )

    assert info.path == weights.resolve()
    assert info.provenance == f"local file: {weights.resolve()}"
    assert info.class_names == ("person", "sports ball")


def test_model_without_label_mapping_is_rejected(tmp_path):
    weights = tmp_path / "approved.pt"
    weights.touch()

    with pytest.raises(ValueError, match="class-label mapping"):
        inspect_local_yolo_model(weights, loader=lambda path: object())


def test_ultralytics_predictor_receives_footballvision_threshold_and_image_size(monkeypatch):
    received = {}

    class RuntimeModel:
        def predict(self, frame, **kwargs):
            received.update(kwargs)
            return []

    monkeypatch.setitem(sys.modules, "ultralytics", SimpleNamespace(YOLO=lambda _: RuntimeModel()))
    predictor = _UltralyticsPredictor(
        Path("local.pt"), confidence_threshold=0.15, image_size=960, device="mps"
    )

    assert list(predictor.predict(object())) == []
    assert received == {"conf": 0.15, "imgsz": 960, "device": "mps", "verbose": False}
