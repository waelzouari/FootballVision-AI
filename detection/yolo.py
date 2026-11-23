"""A small, dependency-light adapter around an already available YOLO model.

The module deliberately does not select or download a model.  Applications can
inject a predictor (including a test double), or supply a local model path for
lazy Ultralytics loading when that optional dependency is installed.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any, Protocol

from contracts.schemas import Detection, ObjectType


@dataclass(frozen=True)
class RawPrediction:
    """One model prediction expressed in source-frame pixel coordinates."""

    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]


class YoloPredictor(Protocol):
    """Minimal predictor seam used by :class:`YoloDetector`."""

    def predict(self, frame: Any) -> Iterable[RawPrediction]:
        """Return predictions for one frame without changing its coordinates."""


@dataclass(frozen=True)
class LocalYoloModelInfo:
    """Inspectable metadata for explicitly supplied, local YOLO weights."""

    path: Path
    provenance: str
    class_names: tuple[str, ...]


def inspect_local_yolo_model(
    model_path: str | Path,
    *,
    loader: Callable[[str], Any] | None = None,
) -> LocalYoloModelInfo:
    """Load only an explicit local weights file and report its declared labels.

    ``loader`` exists to make runtime validation testable without Ultralytics.
    It must load the exact supplied path; this function never resolves model
    aliases, URLs, or cache locations.
    """
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"YOLO weights not found at {path}; supply an approved local weights file. "
            "Automatic model downloads are disabled."
        )
    if loader is None:
        try:
            from ultralytics import YOLO
        except ImportError as error:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "Ultralytics is not installed; install it before using approved local YOLO weights."
            ) from error
        loader = YOLO

    model = loader(str(path))
    names = getattr(model, "names", None)
    if isinstance(names, Mapping):
        class_names = tuple(str(names[index]) for index in sorted(names))
    elif isinstance(names, Sequence) and not isinstance(names, (str, bytes)):
        class_names = tuple(str(name) for name in names)
    else:
        raise ValueError("The local YOLO model does not expose a usable class-label mapping.")
    return LocalYoloModelInfo(
        path=path.resolve(),
        provenance=f"local file: {path.resolve()}",
        class_names=class_names,
    )


class YoloDetector:
    """Map YOLO labels to FootballVision's typed detection contract."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        *,
        predictor: YoloPredictor | None = None,
        confidence_threshold: float = 0.25,
        class_mapping: Mapping[str, ObjectType] | None = None,
        image_size: int = 640,
        device: str | None = None,
    ) -> None:
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if predictor is None and model_path is None:
            raise ValueError("provide a predictor or a local model_path")
        if image_size < 32:
            raise ValueError("image_size must be at least 32")

        mapping = {
            "person": ObjectType.PLAYER,
            "sports ball": ObjectType.BALL,
            "referee": ObjectType.REFEREE,
            "official": ObjectType.REFEREE,
        }
        if class_mapping:
            mapping.update({name.casefold(): kind for name, kind in class_mapping.items()})

        self._model_path = Path(model_path) if model_path is not None else None
        self._predictor = predictor
        self._confidence_threshold = confidence_threshold
        self._class_mapping = mapping
        self._image_size = image_size
        self._device = device

    def detect(self, frame: Any, timestamp_s: float) -> tuple[Detection, ...]:
        """Return valid player, ball and referee detections for a video frame."""
        if not isfinite(timestamp_s) or timestamp_s < 0:
            raise ValueError("timestamp_s must be a finite value >= 0")

        predictions = self._get_predictor().predict(frame)
        detections: list[Detection] = []
        for prediction in predictions:
            object_type = self._class_mapping.get(prediction.class_name.casefold())
            if object_type is None or not self._is_valid_prediction(prediction):
                continue
            if prediction.confidence < self._confidence_threshold:
                continue
            detections.append(
                Detection(
                    object_type=object_type,
                    xyxy=tuple(float(value) for value in prediction.xyxy),
                    confidence=float(prediction.confidence),
                    timestamp_s=timestamp_s,
                )
            )
        return tuple(detections)

    def _get_predictor(self) -> YoloPredictor:
        if self._predictor is None:
            if self._model_path is None or not self._model_path.is_file():
                raise FileNotFoundError(
                    "YOLO model path must point to an existing local weights file; "
                    "automatic model downloads are disabled."
                )
            self._predictor = _UltralyticsPredictor(
                self._model_path,
                confidence_threshold=self._confidence_threshold,
                image_size=self._image_size,
                device=self._device,
            )
        return self._predictor

    @staticmethod
    def _is_valid_prediction(prediction: RawPrediction) -> bool:
        if not 0.0 <= prediction.confidence <= 1.0:
            return False
        left, top, right, bottom = prediction.xyxy
        return all(isfinite(value) for value in prediction.xyxy) and left < right and top < bottom


class _UltralyticsPredictor:
    """Optional adapter kept private so core tests need no ML dependency."""

    def __init__(
        self,
        model_path: Path,
        *,
        confidence_threshold: float,
        image_size: int,
        device: str | None,
    ) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as error:  # pragma: no cover - dependency is optional
            raise RuntimeError("Install ultralytics to use a local YOLO model") from error
        self._model = YOLO(str(model_path))
        self._confidence_threshold = confidence_threshold
        self._image_size = image_size
        self._device = device

    def predict(self, frame: Any) -> Iterable[RawPrediction]:  # pragma: no cover - optional runtime
        for result in self._model.predict(
            frame,
            conf=self._confidence_threshold,
            imgsz=self._image_size,
            device=self._device,
            verbose=False,
        ):
            names = result.names
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                yield RawPrediction(
                    class_name=str(names[class_id]),
                    confidence=float(box.conf[0].item()),
                    xyxy=tuple(float(value) for value in box.xyxy[0].tolist()),
                )
