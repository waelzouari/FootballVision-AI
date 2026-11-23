"""Dependency-free dashboard summaries for the P0 analysis pipeline.

This module deliberately accepts already-produced :class:`GameState` values.
It does not infer a ball location or a team assignment when the pipeline has
not observed one.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from statistics import fmean
from typing import Sequence

from contracts.schemas import BallVisibility, GameState, ObjectType, Team


@dataclass(frozen=True)
class PipelineMetrics:
    """Measured processing timings supplied by the pipeline."""

    frames_processed: int
    elapsed_s: float
    latencies_ms: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.frames_processed < 0:
            raise ValueError("frames_processed must be non-negative")
        if self.elapsed_s < 0:
            raise ValueError("elapsed_s must be non-negative")
        if any(latency < 0 for latency in self.latencies_ms):
            raise ValueError("latencies_ms must contain non-negative values")

    @property
    def fps(self) -> float | None:
        """Processing rate, or ``None`` when no duration was measured."""
        if self.elapsed_s == 0:
            return None
        return self.frames_processed / self.elapsed_s

    @property
    def mean_latency_ms(self) -> float | None:
        return fmean(self.latencies_ms) if self.latencies_ms else None

    @property
    def p95_latency_ms(self) -> float | None:
        if not self.latencies_ms:
            return None
        ordered = sorted(self.latencies_ms)
        return ordered[ceil(0.95 * len(ordered)) - 1]


@dataclass(frozen=True)
class DashboardSnapshot:
    """A display-ready view of the most recent observed game state."""

    timestamp_s: float | None
    player_count: int
    referee_count: int
    team_a_count: int
    team_b_count: int
    team_unknown_count: int
    ball_visibility: BallVisibility | None
    metrics: PipelineMetrics


def build_snapshot(
    states: Sequence[GameState], metrics: PipelineMetrics
) -> DashboardSnapshot:
    """Build a snapshot from the latest state without filling unknown values."""
    if not states:
        return DashboardSnapshot(
            timestamp_s=None,
            player_count=0,
            referee_count=0,
            team_a_count=0,
            team_b_count=0,
            team_unknown_count=0,
            ball_visibility=None,
            metrics=metrics,
        )

    latest = states[-1]
    players = [obj for obj in latest.objects if obj.object_type is ObjectType.PLAYER]
    referees = [obj for obj in latest.objects if obj.object_type is ObjectType.REFEREE]
    return DashboardSnapshot(
        timestamp_s=latest.timestamp_s,
        player_count=len(players),
        referee_count=len(referees),
        team_a_count=sum(player.team is Team.A for player in players),
        team_b_count=sum(player.team is Team.B for player in players),
        team_unknown_count=sum(player.team is Team.UNKNOWN for player in players),
        ball_visibility=latest.ball.visibility,
        metrics=metrics,
    )


def render_text(snapshot: DashboardSnapshot) -> str:
    """Render a compact, dependency-free status panel."""
    fps = "unmeasured" if snapshot.metrics.fps is None else f"{snapshot.metrics.fps:.2f}"
    latency = (
        "unmeasured"
        if snapshot.metrics.mean_latency_ms is None
        else f"{snapshot.metrics.mean_latency_ms:.2f} ms"
    )
    timestamp = "unavailable" if snapshot.timestamp_s is None else f"{snapshot.timestamp_s:.3f} s"
    ball = "unknown" if snapshot.ball_visibility is None else snapshot.ball_visibility.value
    return "\n".join(
        (
            f"Timestamp: {timestamp}",
            f"Players: {snapshot.player_count} (A={snapshot.team_a_count}, B={snapshot.team_b_count}, unknown={snapshot.team_unknown_count})",
            f"Referees: {snapshot.referee_count}",
            f"Ball: {ball}",
            f"FPS: {fps}",
            f"Latency mean: {latency}",
        )
    )
