from app.dashboard import PipelineMetrics, build_snapshot, render_text
from contracts.schemas import (
    BallState,
    BallVisibility,
    GameState,
    ObjectType,
    Team,
    TrackedObject,
)


def _object(track_id: int, object_type: ObjectType, team: Team = Team.UNKNOWN) -> TrackedObject:
    return TrackedObject(
        track_id=track_id,
        object_type=object_type,
        xyxy=(0.0, 0.0, 10.0, 10.0),
        confidence=0.9,
        timestamp_s=2.0,
        team=team,
    )


def test_snapshot_keeps_lost_ball_and_unknown_team_explicit():
    state = GameState(
        timestamp_s=2.0,
        objects=(
            _object(1, ObjectType.PLAYER, Team.A),
            _object(2, ObjectType.PLAYER),
            _object(3, ObjectType.REFEREE),
        ),
        ball=BallState(BallVisibility.LOST),
    )
    snapshot = build_snapshot((state,), PipelineMetrics(20, 2.0, (10.0, 30.0)))

    assert snapshot.ball_visibility is BallVisibility.LOST
    assert snapshot.team_unknown_count == 1
    assert "Ball: lost" in render_text(snapshot)
    assert "unknown=1" in render_text(snapshot)


def test_metrics_render_measured_fps_and_latency():
    metrics = PipelineMetrics(frames_processed=30, elapsed_s=2.0, latencies_ms=(10.0, 30.0))
    snapshot = build_snapshot((), metrics)

    assert metrics.fps == 15.0
    assert metrics.mean_latency_ms == 20.0
    assert metrics.p95_latency_ms == 30.0
    rendered = render_text(snapshot)
    assert "FPS: 15.00" in rendered
    assert "Latency mean: 20.00 ms" in rendered
