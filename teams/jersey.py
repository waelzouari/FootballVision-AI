"""Conservative, calibration-driven jersey colour classification."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable
from math import sqrt
from typing import Any, Literal, TypeAlias

from contracts.schemas import Team

Color: TypeAlias = tuple[float, float, float]
ColorExtractor: TypeAlias = Callable[[Any], Color | None]


def _tuple_extractor(crop: Any) -> Color | None:
    """Accept an RGB triple for lightweight integrations and tests only."""
    if not isinstance(crop, tuple) or len(crop) != 3:
        return None
    if not all(isinstance(value, (int, float)) for value in crop):
        return None
    return (float(crop[0]), float(crop[1]), float(crop[2]))


def extract_jersey_crop(
    frame: Any,
    xyxy: tuple[float, float, float, float],
    *,
    upper_body_fraction: float = 0.55,
) -> Any | None:
    """Return a bounds-checked upper-body crop from an observed player box.

    The input frame is expected to be an OpenCV-style HWC array.  Invalid,
    off-screen, or too-small boxes return ``None`` rather than a fabricated
    crop.  The crop starts below the head to reduce face/grass contamination.
    """
    if not 0 < upper_body_fraction <= 1:
        raise ValueError("upper_body_fraction must be in (0, 1]")
    shape = getattr(frame, "shape", None)
    if not isinstance(shape, tuple) or len(shape) < 3 or shape[2] < 3:
        return None
    try:
        left, top, right, bottom = (float(value) for value in xyxy)
    except (TypeError, ValueError):
        return None
    if not left < right or not top < bottom:
        return None
    frame_height, frame_width = int(shape[0]), int(shape[1])
    x1, x2 = max(0, int(left)), min(frame_width, int(-(-right // 1)))
    y1, y2 = max(0, int(top)), min(frame_height, int(-(-bottom // 1)))
    if x2 - x1 < 2 or y2 - y1 < 3:
        return None
    height = y2 - y1
    jersey_top = y1 + max(1, int(height * 0.18))
    jersey_bottom = min(y2, jersey_top + max(1, int(height * upper_body_fraction)))
    if jersey_bottom <= jersey_top:
        return None
    return frame[jersey_top:jersey_bottom, x1:x2, :3]


def dominant_color(
    crop: Any, *, color_order: Literal["BGR", "RGB"] = "BGR"
) -> Color | None:
    """Return the mean jersey colour as an RGB triple, if a crop is valid."""
    if color_order not in {"BGR", "RGB"}:
        raise ValueError("color_order must be BGR or RGB")
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - environment dependent
        return None
    array = np.asarray(crop)
    if array.ndim != 3 or array.shape[0] == 0 or array.shape[1] == 0 or array.shape[2] < 3:
        return None
    values = array[..., :3].reshape(-1, 3)
    if not np.isfinite(values).all():
        return None
    channels = tuple(float(value) for value in values.mean(axis=0))
    return channels[::-1] if color_order == "BGR" else channels


def _default_extractor(crop: Any) -> Color | None:
    return _tuple_extractor(crop) or dominant_color(crop)


def _distance(left: Color, right: Color) -> float:
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


class JerseyTeamClassifier:
    """Assign ``A``/``B`` only after two distinguishable jersey colours exist.

    A production colour extractor can be supplied by the caller. This class never
    guesses a team for absent colours, colours too far from calibration, or a tie.
    """

    def __init__(
        self,
        color_extractor: ColorExtractor | None = None,
        *,
        max_distance: float = 80.0,
        ambiguity_margin: float = 5.0,
    ) -> None:
        if max_distance <= 0 or ambiguity_margin < 0:
            raise ValueError("Colour thresholds must be non-negative and max_distance positive")
        self._extract = color_extractor or _default_extractor
        self._max_distance = max_distance
        self._ambiguity_margin = ambiguity_margin
        self._team_a: Color | None = None
        self._team_b: Color | None = None

    @property
    def calibrated(self) -> bool:
        return self._team_a is not None and self._team_b is not None

    def calibrate(self, crops: Iterable[Any]) -> bool:
        """Record the first two distinct observable jersey colours as teams A/B."""
        colors = [color for crop in crops if (color := self._extract(crop)) is not None]
        if len(colors) < 2:
            return False
        first = colors[0]
        second = next((color for color in colors[1:] if _distance(first, color) > self._ambiguity_margin), None)
        if second is None:
            return False
        self._team_a, self._team_b = first, second
        return True

    def classify(self, crop: Any) -> Team:
        color = self._extract(crop)
        if color is None or not self.calibrated:
            return Team.UNKNOWN
        assert self._team_a is not None and self._team_b is not None
        distance_a = _distance(color, self._team_a)
        distance_b = _distance(color, self._team_b)
        if min(distance_a, distance_b) > self._max_distance:
            return Team.UNKNOWN
        if abs(distance_a - distance_b) <= self._ambiguity_margin:
            return Team.UNKNOWN
        return Team.A if distance_a < distance_b else Team.B

    def classify_many(self, crops: Iterable[Any]) -> tuple[Team, ...]:
        return tuple(self.classify(crop) for crop in crops)


class TemporalTeamSmoother:
    """Conservative per-track smoothing for already-classified player crops."""

    def __init__(self, *, window_size: int = 5, min_observations: int = 2) -> None:
        if window_size < 1 or not 1 <= min_observations <= window_size:
            raise ValueError("min_observations must be between 1 and window_size")
        self._window_size = window_size
        self._min_observations = min_observations
        self._history: dict[int, deque[Team]] = {}

    def update(self, track_id: int, candidate: Team) -> Team:
        """Return a stable A/B label only after an unambiguous local majority."""
        if candidate is Team.UNKNOWN:
            return Team.UNKNOWN
        history = self._history.setdefault(track_id, deque(maxlen=self._window_size))
        history.append(candidate)
        counts = {team: sum(value is team for value in history) for team in (Team.A, Team.B)}
        best_count = max(counts.values())
        if best_count < self._min_observations or counts[Team.A] == counts[Team.B]:
            return Team.UNKNOWN
        return Team.A if counts[Team.A] > counts[Team.B] else Team.B
