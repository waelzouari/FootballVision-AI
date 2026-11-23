# FootballVision AI

Single-camera football-video analysis, developed incrementally. P0 provides typed contracts, MP4/camera ingestion, local YOLO inference, ByteTrack player IDs, separate ball visibility, colour-based A/B/unknown team labels, annotated video, CSV and measured dashboard metrics.

## Quick start

```bash
python3 -m pytest
```

For the real-video runtime (Python 3.11 or 3.12 recommended):

```bash
python3 -m pip install -e '.[runtime,dev]'
```

Run a local, approved YOLO model on a video:

```bash
python3 -m app.run_pipeline data/videos/corrected_excerpt.mp4 \
  --model models/yolo11n.pt --output-dir outputs/corrected_excerpt_yolo11n
```

The generic COCO YOLO11n model identifies `person` and `sports ball`, but does not have a referee class and is not football fine-tuned. See [the evaluation report](evaluation/REPORT.md), [task queue](docs/TASKS.md) and [architecture](docs/ARCHITECTURE.md) for scope and limitations.

For a clean-clone setup and the local assets that are intentionally not in Git,
start with [the collaborator handoff](collaborator_handoff/README_HANDOFF.md).
