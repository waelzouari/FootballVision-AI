# FootballVision architecture

Source: FootballVision cahier des charges (5 pages). Video from one camera; no promise of full game reconstruction.

Pipeline: OpenCV MP4/camera -> YOLO detections -> ByteTrack players + separate ball tracker -> jersey/team classifier -> optional calibrated pitch coordinates -> timestamped game state/window buffers -> temporal event candidates -> annotated video/dashboard/CSV/event log.

Ownership: detection/ (detection), tracking/ (tracking), teams/ and field/ (teams_field), analysis/ and events/ (game_intelligence), app/ and outputs exporters (dashboard), evaluation/ (evaluation). Orchestrator owns contracts/, shared integration, dependency manifest, docs and cross-module tests.

P0: ingestion, player/ball/referee detection, player IDs, ball visible/lost/uncertain, A/B/unknown teams, annotated video, CSV, dashboard FPS/latency and evaluation.
P1: field calibration/homography validated before metric distances, corners/goals and ball actions/pass classes.
P2: offside, foul and cards prototypes. Require temporal evidence and report indeterminate where insufficient.

Prefer CPU-compatible baseline; benchmark on target machine before making real-time claims. Handle camera cuts, occlusions, changing viewpoints and missed ball detections explicitly.
