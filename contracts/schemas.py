from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ObjectType(str, Enum):
    PLAYER = "player"
    BALL = "ball"
    REFEREE = "referee"
    OTHER = "other"


class Team(str, Enum):
    A = "A"
    B = "B"
    UNKNOWN = "unknown"


class BallVisibility(str, Enum):
    VISIBLE = "visible"
    LOST = "lost"
    UNCERTAIN = "uncertain"


class EventStatus(str, Enum):
    PROBABLE = "probable"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class FramePacket:
    frame_index: int
    timestamp_s: float
    width: int
    height: int


@dataclass(frozen=True)
class Detection:
    object_type: ObjectType
    xyxy: tuple[float, float, float, float]
    confidence: float
    timestamp_s: float


@dataclass(frozen=True)
class TrackedObject:
    track_id: int
    object_type: ObjectType
    xyxy: tuple[float, float, float, float]
    confidence: float
    timestamp_s: float
    team: Team = Team.UNKNOWN
    pixel_position: Optional[tuple[float, float]] = None
    pitch_position_m: Optional[tuple[float, float]] = None


@dataclass(frozen=True)
class BallState:
    visibility: BallVisibility
    observed_position: Optional[tuple[float, float]] = None
    last_seen_s: Optional[float] = None


@dataclass(frozen=True)
class CalibrationState:
    validated: bool = False
    reprojection_error: Optional[float] = None


@dataclass(frozen=True)
class GameState:
    timestamp_s: float
    objects: tuple[TrackedObject, ...]
    ball: BallState
    calibration: CalibrationState = field(default_factory=CalibrationState)


@dataclass(frozen=True)
class EventCandidate:
    event_type: str
    timestamp_s: float
    confidence: float
    status: EventStatus
    evidence: tuple[str, ...] = ()
