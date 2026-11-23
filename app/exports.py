"""P0 output writers for observed tracking results.

The CSV writer is dependency-free.  The MP4 writer imports OpenCV only when it
is explicitly used, allowing the rest of the project to remain testable on
machines without video support.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from contracts.schemas import GameState, ObjectType, Team, TrackedObject


CSV_FIELDS = (
    "source_video_id",
    "frame_id",
    "timestamp",
    "object_id",
    "object_class",
    "team",
    "confidence",
    "bbox_x1",
    "bbox_y1",
    "bbox_x2",
    "bbox_y2",
)


def export_observations_csv(
    destination: str | Path,
    source_video_id: str,
    frames: Iterable[tuple[int, GameState]],
) -> Path:
    """Write only observed tracked objects in the portable P0 CSV format."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for frame_id, state in frames:
            for obj in state.objects:
                writer.writerow(_csv_row(source_video_id, frame_id, state.timestamp_s, obj))
    return path


def _csv_row(
    source_video_id: str, frame_id: int, timestamp_s: float, obj: TrackedObject
) -> dict[str, str | int | float]:
    left, top, right, bottom = obj.xyxy
    return {
        "source_video_id": source_video_id,
        "frame_id": frame_id,
        "timestamp": timestamp_s,
        "object_id": obj.track_id,
        "object_class": obj.object_type.value,
        "team": obj.team.value,
        "confidence": obj.confidence,
        "bbox_x1": left,
        "bbox_y1": top,
        "bbox_x2": right,
        "bbox_y2": bottom,
    }


class AnnotatedVideoWriter:
    """Write supplied observations over decoded frames; it never predicts data."""

    def __init__(
        self,
        destination: str | Path,
        *,
        fps: float,
        frame_size: tuple[int, int],
    ) -> None:
        if fps <= 0:
            raise ValueError("fps must be positive")
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "OpenCV is required for annotated MP4 output; install footballvision[video]."
            ) from exc
        self._cv2 = cv2
        self.destination = Path(destination)
        self.destination.parent.mkdir(parents=True, exist_ok=True)
        self._writer = cv2.VideoWriter(
            str(self.destination), cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size
        )
        if not self._writer.isOpened():
            self._writer.release()
            raise RuntimeError(f"Cannot create annotated video: {self.destination}")

    def write_frame(self, frame: Any, observations: Sequence[TrackedObject]) -> None:
        """Draw the supplied boxes and labels, then append one frame."""
        for observation in observations:
            self._draw_observation(frame, observation)
        self._writer.write(frame)

    def close(self) -> None:
        self._writer.release()

    def __enter__(self) -> "AnnotatedVideoWriter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _draw_observation(self, frame: Any, observation: TrackedObject) -> None:
        left, top, right, bottom = (round(value) for value in observation.xyxy)
        color = _color_for(observation)
        label = f"{observation.object_type.value} #{observation.track_id} {observation.confidence:.2f}"
        if observation.object_type is ObjectType.PLAYER:
            label = f"{label} {observation.team.value}"
        self._cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        (label_width, label_height), baseline = self._cv2.getTextSize(
            label, self._cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
        )
        label_y = max(label_height + baseline + 2, top - 6)
        self._cv2.rectangle(
            frame,
            (left, label_y - label_height - baseline - 4),
            (left + label_width + 4, label_y + 2),
            (0, 0, 0),
            -1,
        )
        self._cv2.putText(
            frame,
            label,
            (left + 2, label_y - baseline - 1),
            self._cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            self._cv2.LINE_AA,
        )


def _color_for(observation: TrackedObject) -> tuple[int, int, int]:
    if observation.object_type is ObjectType.BALL:
        return (0, 255, 255)
    if observation.object_type is ObjectType.REFEREE:
        return (255, 255, 255)
    if observation.team is Team.A:
        return (255, 80, 80)
    if observation.team is Team.B:
        return (80, 80, 255)
    return (150, 150, 150)
