from contracts.schemas import Team
from teams.jersey import JerseyTeamClassifier


def test_classifier_requires_two_distinct_calibration_colours():
    classifier = JerseyTeamClassifier()

    assert not classifier.calibrate([(10, 20, 30), (10, 20, 30)])
    assert classifier.classify((10, 20, 30)) is Team.UNKNOWN


def test_classifier_assigns_calibrated_colours_and_preserves_unknowns():
    classifier = JerseyTeamClassifier(max_distance=30, ambiguity_margin=2)
    assert classifier.calibrate([(200, 20, 20), (20, 20, 200)])

    assert classifier.classify_many([(198, 21, 20), (21, 20, 198), None]) == (
        Team.A,
        Team.B,
        Team.UNKNOWN,
    )
    assert classifier.classify((20, 200, 20)) is Team.UNKNOWN


def test_classifier_marks_near_equal_match_as_ambiguous():
    classifier = JerseyTeamClassifier(max_distance=100, ambiguity_margin=3)
    assert classifier.calibrate([(0, 0, 0), (20, 0, 0)])

    assert classifier.classify((10, 0, 0)) is Team.UNKNOWN
