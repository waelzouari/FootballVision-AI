# Task queue — orchestrator owns updates

## P0 milestones (sequential dependencies)
- [x] P0-001 Create typed contracts, minimal Python package layout, config and focused tests (orchestrator).
- [x] P0-002 OpenCV video ingestion and timestamps (orchestrator integration or dashboard agent with exclusive ownership).
- [x] P0-003 YOLO detector with player/ball/referee mapping, confidence and box outputs (detection).
- [x] P0-004 Player tracking adapter and independent ball state/tracking (transparent IoU baseline; ByteTrack runtime adapter pending dependency approval).
- [x] P0-005 Jersey team classification A/B/unknown (teams_field; depends on crops/detections).
- [ ] P0-006 Annotated MP4, CSV, FPS and basic dashboard (fixture-backed metrics/dashboard complete; annotated MP4 and CSV pending integration).
- [ ] P0-007 Per-module evaluation, reproducible test clips and metrics (evaluation).
- [ ] P0-008 Integrate real P0 pipeline and validate on licensed sample clips (orchestrator).

## P1
- [ ] P1-001 Pitch line/keypoint detection, validated homography and 2D view (teams_field).
- [ ] P1-002 Corner and goal candidates using geometry + temporal evidence (game_intelligence).
- [ ] P1-003 Pass/high-pass/cross candidate spotting (game_intelligence).

## P2
- [ ] P2-001 Offside prototype with indeterminate option (game_intelligence).
- [ ] P2-002 Foul/card candidate spotting with uncertainty (game_intelligence).

## Acceptance
Each task needs focused tests, paths changed, honest status, reproducible run instructions and no undocumented contract breakage. Do not begin P1 until a usable P0 demo exists.
