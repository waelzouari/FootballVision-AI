from detection.yolo import RawPrediction, YoloDetector
from contracts.schemas import ObjectType


class FakePredictor:
    def __init__(self, predictions):
        self.predictions = predictions

    def predict(self, frame):
        return self.predictions


def test_maps_player_ball_and_configured_referee_labels():
    detector = YoloDetector(
        predictor=FakePredictor(
            [
                RawPrediction("person", 0.9, (1, 2, 4, 6)),
                RawPrediction("sports ball", 0.8, (3, 4, 5, 6)),
                RawPrediction("match official", 0.7, (7, 8, 10, 12)),
            ]
        ),
        class_mapping={"match official": ObjectType.REFEREE},
    )

    detections = detector.detect(frame=object(), timestamp_s=1.25)

    assert [item.object_type for item in detections] == [
        ObjectType.PLAYER,
        ObjectType.BALL,
        ObjectType.REFEREE,
    ]
    assert all(item.timestamp_s == 1.25 for item in detections)


def test_filters_low_confidence_unknown_labels_and_invalid_boxes():
    detector = YoloDetector(
        predictor=FakePredictor(
            [
                RawPrediction("person", 0.2, (1, 1, 2, 2)),
                RawPrediction("car", 0.99, (1, 1, 2, 2)),
                RawPrediction("person", 0.9, (2, 1, 2, 3)),
                RawPrediction("person", 1.1, (1, 1, 2, 2)),
                RawPrediction("person", 0.9, (1, 1, 3, 3)),
            ]
        ),
        confidence_threshold=0.25,
    )

    detections = detector.detect(frame=None, timestamp_s=0.0)

    assert len(detections) == 1
    assert detections[0].xyxy == (1.0, 1.0, 3.0, 3.0)


def test_missing_local_model_does_not_trigger_download():
    detector = YoloDetector(model_path="missing-local-weights.pt")

    try:
        detector.detect(frame=None, timestamp_s=0.0)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing local weights must fail before loading YOLO")
