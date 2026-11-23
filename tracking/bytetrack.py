"""Observed-player adapter for Ultralytics' ByteTrack implementation.

ByteTrack maintains a Kalman state internally, but this adapter returns a
``TrackedObject`` only for a detection supplied in the current frame.  The
reported box, confidence and timestamp therefore remain observations rather
than tracker predictions.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Protocol

from contracts.schemas import Detection, ObjectType, TrackedObject


@dataclass(frozen=True)
class ByteTrackSettings:
    track_high_thresh: float = 0.5
    track_low_thresh: float = 0.1
    new_track_thresh: float = 0.6
    track_buffer: int = 30
    # A moderately permissive association threshold reduces short-lived IDs
    # on the P0 football clip without emitting tracker-predicted boxes.
    match_thresh: float = 0.85
    fuse_score: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.track_low_thresh <= self.track_high_thresh <= 1:
            raise ValueError("ByteTrack confidence thresholds must be in [0, 1]")
        if not 0 <= self.new_track_thresh <= 1 or self.track_buffer < 1 or not 0 <= self.match_thresh <= 1:
            raise ValueError("ByteTrack settings are invalid")


class ByteTrackBackend(Protocol):
    """Runtime seam returning ``[x1,y1,x2,y2,id,score,class,input_index]`` rows."""

    def update(self, detections: Sequence[Detection]) -> Sequence[Sequence[float]]: ...


class ByteTrackPlayerTracker:
    """Assign stable IDs to *observed* player detections with ByteTrack."""

    def __init__(
        self,
        *,
        settings: ByteTrackSettings | None = None,
        backend_factory: Callable[[ByteTrackSettings], ByteTrackBackend] | None = None,
    ) -> None:
        self._settings = settings or ByteTrackSettings()
        self._backend_factory = backend_factory or _create_ultralytics_backend
        self._backend: ByteTrackBackend | None = None

    def update(self, detections: Sequence[Detection]) -> tuple[TrackedObject, ...]:
        players = tuple(item for item in detections if item.object_type is ObjectType.PLAYER)
        if self._backend is None:
            try:
                self._backend = self._backend_factory(self._settings)
            except (ImportError, ModuleNotFoundError) as error:
                raise RuntimeError(
                    "ByteTrack requires the optional Ultralytics runtime; install footballvision[runtime]."
                ) from error

        rows = self._backend.update(players)
        tracked: list[TrackedObject] = []
        seen_indices: set[int] = set()
        for row in rows:
            if len(row) < 8:
                raise ValueError("ByteTrack backend returned a malformed tracking row")
            track_id = int(row[4])
            input_index = int(row[7])
            if track_id <= 0 or input_index < 0 or input_index >= len(players) or input_index in seen_indices:
                continue
            seen_indices.add(input_index)
            observed = players[input_index]
            tracked.append(
                TrackedObject(
                    track_id=track_id,
                    object_type=ObjectType.PLAYER,
                    xyxy=observed.xyxy,
                    confidence=observed.confidence,
                    timestamp_s=observed.timestamp_s,
                )
            )
        return tuple(tracked)


class _DetectionBatch:
    """Small NumPy-backed shape compatible with Ultralytics BYTETracker."""

    def __init__(self, xyxy: object, conf: object, cls: object) -> None:
        self.xyxy = xyxy
        self.conf = conf
        self.cls = cls
        self.xywh = xyxy.copy()
        self.xywh[:, 2] = xyxy[:, 2] - xyxy[:, 0]
        self.xywh[:, 3] = xyxy[:, 3] - xyxy[:, 1]
        self.xywh[:, 0] = xyxy[:, 0] + self.xywh[:, 2] / 2
        self.xywh[:, 1] = xyxy[:, 1] + self.xywh[:, 3] / 2

    def __len__(self) -> int:
        return len(self.conf)

    def __getitem__(self, index: object) -> "_DetectionBatch":
        return _DetectionBatch(self.xyxy[index], self.conf[index], self.cls[index])


class _UltralyticsByteTrackBackend:
    def __init__(self, settings: ByteTrackSettings) -> None:
        import numpy as np
        from ultralytics.trackers.byte_tracker import BYTETracker

        self._np = np
        self._tracker = BYTETracker(SimpleNamespace(**settings.__dict__))

    def update(self, detections: Sequence[Detection]) -> Sequence[Sequence[float]]:
        if not detections:
            # ByteTrack must still advance its lifecycle on empty frames.
            xyxy = self._np.empty((0, 4), dtype=float)
            batch = _DetectionBatch(xyxy, self._np.empty(0), self._np.empty(0))
        else:
            batch = _DetectionBatch(
                self._np.asarray([item.xyxy for item in detections], dtype=float),
                self._np.asarray([item.confidence for item in detections], dtype=float),
                self._np.zeros(len(detections), dtype=float),
            )
        return self._tracker.update(batch).tolist()


def _create_ultralytics_backend(settings: ByteTrackSettings) -> ByteTrackBackend:
    return _UltralyticsByteTrackBackend(settings)
