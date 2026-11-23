"""Executable P0 pipeline for a locally supplied YOLO model and MP4 source."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from statistics import fmean

from contracts.schemas import BallState, Detection, GameState, ObjectType, Team, TrackedObject
from detection.yolo import YoloDetector
from ingestion.video import OpenCVVideoReader
from teams.jersey import JerseyTeamClassifier, TemporalTeamSmoother, extract_jersey_crop
from tracking.bytetrack import ByteTrackPlayerTracker, ByteTrackSettings
from tracking.simple import BallTracker

from .dashboard import PipelineMetrics, build_snapshot, render_text
from .exports import AnnotatedVideoWriter, export_observations_csv


@dataclass(frozen=True)
class PipelineConfig:
    source: Path
    model_path: Path
    output_dir: Path
    confidence_threshold: float = 0.20
    image_size: int = 640
    device: str | None = None
    max_frames: int | None = None

    def __post_init__(self) -> None:
        if not self.source.is_file():
            raise FileNotFoundError(f"Video not found: {self.source}")
        if not self.model_path.is_file():
            raise FileNotFoundError(f"YOLO weights not found: {self.model_path}")
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if self.image_size < 32:
            raise ValueError("image_size must be at least 32")
        if self.max_frames is not None and self.max_frames < 1:
            raise ValueError("max_frames must be positive when supplied")


@dataclass(frozen=True)
class PipelineRun:
    source: str
    frames_processed: int
    elapsed_s: float
    fps: float | None
    mean_latency_ms: float | None
    p95_latency_ms: float | None
    player_observations: int
    ball_observations: int
    ball_visible_frames: int
    annotated_video: str
    observations_csv: str
    model_path: str
    model_classes: tuple[str, ...]


def run_pipeline(config: PipelineConfig) -> PipelineRun:
    """Process each decoded frame and export only actual observed results."""
    reader = OpenCVVideoReader(config.source)
    info = reader.info()
    detector = YoloDetector(
        config.model_path,
        confidence_threshold=config.confidence_threshold,
        image_size=config.image_size,
        device=config.device,
    )
    player_tracker = ByteTrackPlayerTracker(
        settings=ByteTrackSettings(
            track_high_thresh=config.confidence_threshold,
            track_low_thresh=min(0.10, config.confidence_threshold),
            new_track_thresh=max(config.confidence_threshold, 0.25),
        )
    )
    ball_tracker = BallTracker()
    classifier = JerseyTeamClassifier()
    smoother = TemporalTeamSmoother()
    config.output_dir.mkdir(parents=True, exist_ok=True)
    annotated_path = config.output_dir / "annotated.mp4"
    csv_path = config.output_dir / "observations.csv"
    states: list[tuple[int, GameState]] = []
    latencies_ms: list[float] = []
    player_observations = ball_observations = ball_visible_frames = 0
    started = time.perf_counter()

    with AnnotatedVideoWriter(
        annotated_path, fps=info.fps, frame_size=(info.width, info.height)
    ) as writer:
        for video_frame in reader.frames():
            if config.max_frames is not None and len(states) >= config.max_frames:
                break
            frame_started = time.perf_counter()
            detections = detector.detect(video_frame.image, video_frame.packet.timestamp_s)
            players = player_tracker.update(detections)
            players = _with_teams(video_frame.image, players, classifier, smoother)
            ball_state = ball_tracker.update(detections, video_frame.packet.timestamp_s)
            ball = _observed_ball(detections)
            objects = players + ((ball,) if ball is not None else ())
            state = GameState(
                timestamp_s=video_frame.packet.timestamp_s,
                objects=objects,
                ball=ball_state,
            )
            writer.write_frame(video_frame.image, objects)
            states.append((video_frame.packet.frame_index, state))
            latencies_ms.append((time.perf_counter() - frame_started) * 1000)
            player_observations += len(players)
            ball_observations += int(ball is not None)
            ball_visible_frames += int(ball_state.visibility.value == "visible")

    elapsed_s = time.perf_counter() - started
    export_observations_csv(csv_path, config.source.name, states)
    metrics = PipelineMetrics(
        frames_processed=len(states), elapsed_s=elapsed_s, latencies_ms=tuple(latencies_ms)
    )
    if states:
        (config.output_dir / "dashboard.txt").write_text(
            render_text(build_snapshot([state for _, state in states], metrics)) + "\n",
            encoding="utf-8",
        )
    model_classes = _model_classes(detector)
    run = PipelineRun(
        source=str(config.source),
        frames_processed=len(states),
        elapsed_s=elapsed_s,
        fps=metrics.fps,
        mean_latency_ms=metrics.mean_latency_ms,
        p95_latency_ms=metrics.p95_latency_ms,
        player_observations=player_observations,
        ball_observations=ball_observations,
        ball_visible_frames=ball_visible_frames,
        annotated_video=str(annotated_path),
        observations_csv=str(csv_path),
        model_path=str(config.model_path),
        model_classes=model_classes,
    )
    (config.output_dir / "run.json").write_text(
        json.dumps(asdict(run), indent=2) + "\n", encoding="utf-8"
    )
    return run


def _with_teams(
    frame: object,
    players: tuple[TrackedObject, ...],
    classifier: JerseyTeamClassifier,
    smoother: TemporalTeamSmoother,
) -> tuple[TrackedObject, ...]:
    crops = [extract_jersey_crop(frame, player.xyxy) for player in players]
    if not classifier.calibrated:
        classifier.calibrate(crops)
    labelled: list[TrackedObject] = []
    for player, crop in zip(players, crops, strict=True):
        team = smoother.update(player.track_id, classifier.classify(crop))
        labelled.append(replace(player, team=team))
    return tuple(labelled)


def _observed_ball(detections: tuple[Detection, ...]) -> TrackedObject | None:
    balls = [item for item in detections if item.object_type is ObjectType.BALL]
    if not balls:
        return None
    observed = max(balls, key=lambda item: item.confidence)
    return TrackedObject(
        track_id=0,
        object_type=ObjectType.BALL,
        xyxy=observed.xyxy,
        confidence=observed.confidence,
        timestamp_s=observed.timestamp_s,
        team=Team.UNKNOWN,
    )


def _model_classes(detector: YoloDetector) -> tuple[str, ...]:
    """Expose labels after the detector's lazy predictor has been initialised."""
    predictor = detector._predictor  # noqa: SLF001 - integration metadata only
    model = getattr(predictor, "_model", None)
    names = getattr(model, "names", {})
    return tuple(str(names[index]) for index in sorted(names)) if isinstance(names, dict) else ()
