import numpy as np

from contracts.schemas import Team
from teams.jersey import (
    JerseyTeamClassifier,
    TemporalTeamSmoother,
    dominant_color,
    extract_jersey_crop,
)


def test_extract_jersey_crop_clamps_to_frame_and_uses_upper_body():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    frame[3:12, 0:10] = (10, 20, 200)  # BGR red jersey region

    crop = extract_jersey_crop(frame, (-4, 0, 10, 18))

    assert crop is not None
    assert crop.shape[1] == 10
    assert dominant_color(crop) == (200.0, 20.0, 10.0)
    assert extract_jersey_crop(frame, (7, 2, 7, 10)) is None


def test_ndarray_crops_calibrate_and_keep_missing_colours_unknown():
    red_bgr = np.full((4, 4, 3), (5, 15, 210), dtype=np.uint8)
    blue_bgr = np.full((4, 4, 3), (210, 15, 5), dtype=np.uint8)
    classifier = JerseyTeamClassifier(max_distance=30, ambiguity_margin=2)

    assert classifier.calibrate((red_bgr, blue_bgr))
    assert classifier.classify(red_bgr) is Team.A
    assert classifier.classify(blue_bgr) is Team.B
    assert classifier.classify(None) is Team.UNKNOWN


def test_temporal_smoother_requires_evidence_and_rejects_unknown_candidate():
    smoother = TemporalTeamSmoother(window_size=3, min_observations=2)

    assert smoother.update(7, Team.A) is Team.UNKNOWN
    assert smoother.update(7, Team.A) is Team.A
    assert smoother.update(7, Team.B) is Team.A
    assert smoother.update(7, Team.UNKNOWN) is Team.UNKNOWN
