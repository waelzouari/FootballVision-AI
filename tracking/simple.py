"""Small deterministic tracking baseline used until a ByteTrack backend is wired."""

from __future__ import annotations

from dataclasses import dataclass

from contracts.schemas import BallState, BallVisibility, Detection, ObjectType, TrackedObject


def _iou(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> float:
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    overlap = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if overlap == 0:
        return 0.0
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - overlap
    return overlap / union if union else 0.0


@dataclass
class _Track:
    track_id: int
    xyxy: tuple[float, float, float, float]


class PlayerTracker:
    """IoU baseline with stable IDs for currently observed player detections.

    It deliberately emits no prediction when a player is not detected. This is
    a transparent adapter point for an eventual ByteTrack implementation.
    """

    def __init__(self, *, min_iou: float = 0.3) -> None:
        if not 0 <= min_iou <= 1:
            raise ValueError("min_iou must be between 0 and 1")
        self._min_iou = min_iou
        self._next_track_id = 1
        self._tracks: list[_Track] = []

    def update(self, detections: tuple[Detection, ...] | list[Detection]) -> tuple[TrackedObject, ...]:
        players = [item for item in detections if item.object_type is ObjectType.PLAYER]
        unmatched_tracks = set(range(len(self._tracks)))
        updated: list[_Track] = []
        output: list[TrackedObject] = []
        for detection in players:
            candidates = [
                (index, _iou(track.xyxy, detection.xyxy))
                for index, track in enumerate(self._tracks)
                if index in unmatched_tracks
            ]
            index, score = max(candidates, key=lambda candidate: candidate[1], default=(-1, 0.0))
            if score >= self._min_iou:
                track_id = self._tracks[index].track_id
                unmatched_tracks.remove(index)
            else:
                track_id = self._next_track_id
                self._next_track_id += 1
            updated.append(_Track(track_id=track_id, xyxy=detection.xyxy))
            output.append(
                TrackedObject(
                    track_id=track_id,
                    object_type=ObjectType.PLAYER,
                    xyxy=detection.xyxy,
                    confidence=detection.confidence,
                    timestamp_s=detection.timestamp_s,
                )
            )
        self._tracks = updated
        return tuple(output)


class BallTracker:
    """Maintain explicit visibility without predicting an unobserved ball."""

    def __init__(self, *, uncertain_after_s: float = 0.75) -> None:
        if uncertain_after_s < 0:
            raise ValueError("uncertain_after_s must be non-negative")
        self._uncertain_after_s = uncertain_after_s
        self._last_seen_s: float | None = None

    def update(self, detections: tuple[Detection, ...] | list[Detection], timestamp_s: float) -> BallState:
        observed = [item for item in detections if item.object_type is ObjectType.BALL]
        if observed:
            best = max(observed, key=lambda item: item.confidence)
            self._last_seen_s = best.timestamp_s
            x1, y1, x2, y2 = best.xyxy
            return BallState(
                visibility=BallVisibility.VISIBLE,
                observed_position=((x1 + x2) / 2, (y1 + y2) / 2),
                last_seen_s=self._last_seen_s,
            )
        if self._last_seen_s is None or timestamp_s - self._last_seen_s > self._uncertain_after_s:
            return BallState(visibility=BallVisibility.LOST, last_seen_s=self._last_seen_s)
        return BallState(visibility=BallVisibility.UNCERTAIN, last_seen_s=self._last_seen_s)
