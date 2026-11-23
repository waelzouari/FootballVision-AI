from __future__ import annotations

import csv
import sys

import pytest

from app.exports import AnnotatedVideoWriter, export_observations_csv
from contracts.schemas import BallState, BallVisibility, GameState, ObjectType, Team, TrackedObject


def _state() -> GameState:
    return GameState(
        timestamp_s=1.25,
        objects=(
            TrackedObject(
                track_id=7,
                object_type=ObjectType.PLAYER,
                xyxy=(1.0, 2.0, 30.0, 40.0),
                confidence=0.91,
                timestamp_s=1.25,
                team=Team.A,
            ),
        ),
        ball=BallState(BallVisibility.LOST),
    )


def test_csv_contains_only_explicit_object_observations(tmp_path):
    path = export_observations_csv(tmp_path / "observations.csv", "clip.mp4", [(12, _state())])

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [{
        "source_video_id": "clip.mp4", "frame_id": "12", "timestamp": "1.25",
        "object_id": "7", "object_class": "player", "team": "A", "confidence": "0.91",
        "bbox_x1": "1.0", "bbox_y1": "2.0", "bbox_x2": "30.0", "bbox_y2": "40.0",
    }]


def test_video_writer_reports_missing_opencv(monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", None)
    with pytest.raises(RuntimeError, match="OpenCV"):
        AnnotatedVideoWriter("ignored.mp4", fps=25, frame_size=(1280, 720))
