from contracts.schemas import BallState, BallVisibility, GameState


def test_missing_ball_is_explicit():
    state = GameState(timestamp_s=0.0, objects=(), ball=BallState(BallVisibility.LOST))
    assert state.ball.observed_position is None
    assert not state.calibration.validated
