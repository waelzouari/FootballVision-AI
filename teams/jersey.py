"""Conservative, calibration-driven jersey colour classification."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from math import sqrt
from typing import Any, TypeAlias

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
        self._extract = color_extractor or _tuple_extractor
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
