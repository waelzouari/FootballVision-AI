# FootballVision AI

Single-camera football-video analysis, developed incrementally. The current P0 foundation provides typed contracts, deterministic MP4/camera ingestion, an opt-in local YOLO adapter, fixture-backed dashboard metrics, player/ball tracking, and team classification. It does not download models, datasets, or produce unmeasured performance claims.

## Quick start

```bash
python3 -m pytest
```

Video decoding requires the optional dependency:

```bash
python3 -m pip install -e '.[video,dev]'
```

Supply any YOLO weights locally; automatic weight downloads are deliberately disabled. See [the task queue](docs/TASKS.md) and [architecture](docs/ARCHITECTURE.md) for the current P0 scope.
