from contracts.schemas import BallVisibility, Detection, ObjectType
from tracking.simple import BallTracker, PlayerTracker


def detection(object_type, xyxy, timestamp=0.0, confidence=0.9):
    return Detection(object_type=object_type, xyxy=xyxy, confidence=confidence, timestamp_s=timestamp)


def test_player_ids_persist_and_non_players_are_excluded():
    tracker = PlayerTracker(min_iou=0.2)
    first = tracker.update([
        detection(ObjectType.PLAYER, (10, 10, 30, 50)),
        detection(ObjectType.REFEREE, (40, 10, 60, 50)),
    ])
    second = tracker.update([detection(ObjectType.PLAYER, (12, 10, 32, 50), timestamp=0.04)])

    assert first[0].track_id == second[0].track_id
    assert all(item.object_type is ObjectType.PLAYER for item in second)


def test_ball_visibility_never_invents_position_when_missing():
    tracker = BallTracker(uncertain_after_s=0.5)
    visible = tracker.update([detection(ObjectType.BALL, (20, 30, 24, 34), timestamp=1.0)], 1.0)
    uncertain = tracker.update([], 1.2)
    lost = tracker.update([], 1.6)

    assert visible.visibility is BallVisibility.VISIBLE
    assert visible.observed_position == (22, 32)
    assert uncertain.visibility is BallVisibility.UNCERTAIN
    assert uncertain.observed_position is None
    assert lost.visibility is BallVisibility.LOST
    assert lost.last_seen_s == 1.0
