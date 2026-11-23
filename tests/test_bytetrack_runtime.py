from __future__ import annotations

import pytest

from contracts.schemas import Detection, ObjectType
from tracking.bytetrack import ByteTrackPlayerTracker


def _player(xyxy=(10.0, 10.0, 30.0, 60.0), timestamp=1.0) -> Detection:
    return Detection(ObjectType.PLAYER, xyxy, 0.9, timestamp)


class FakeBackend:
    def __init__(self):
        self.received = ()

    def update(self, detections):
        self.received = tuple(detections)
        return [[999, 999, 1000, 1000, 7, 0.1, 0, 0], [0, 0, 0, 0, 22, 0.9, 0, -1]]


def test_uses_only_current_detection_geometry_and_filters_non_players():
    backend = FakeBackend()
    tracker = ByteTrackPlayerTracker(backend_factory=lambda _: backend)
    referee = Detection(ObjectType.REFEREE, (1, 1, 2, 2), 0.8, 1.0)

    tracked = tracker.update((_player(), referee))

    assert len(backend.received) == 1
    assert tracked[0].track_id == 7
    assert tracked[0].xyxy == (10.0, 10.0, 30.0, 60.0)
    assert tracked[0].confidence == 0.9


def test_missing_runtime_raises_actionable_error():
    def unavailable(_):
        raise ImportError("not installed")

    with pytest.raises(RuntimeError, match="Ultralytics"):
        ByteTrackPlayerTracker(backend_factory=unavailable).update((_player(),))
