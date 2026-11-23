# Task queue — orchestrator owns updates

## P0 milestones (sequential dependencies)
- [x] P0-001 Create typed contracts, minimal Python package layout, config and focused tests (orchestrator).
- [x] P0-002 OpenCV video ingestion and timestamps (orchestrator integration or dashboard agent with exclusive ownership).
- [x] P0-003 YOLO detector with player/ball/referee mapping, confidence and box outputs (real local YOLO11n inference validated; COCO has no referee class).
- [x] P0-004 Player ByteTrack adapter and independent ball state/tracking (real ByteTrack IDs and explicit ball visibility states validated).
- [x] P0-005 Jersey team classification A/B/unknown (colour-based calibration and temporal smoothing; unknown remains explicit).
- [x] P0-006 Annotated MP4, CSV, FPS and basic dashboard (validated with real detector output on `corrected_excerpt.mp4`).
- [x] P0-007 Per-module evaluation, reproducible test clips and metrics (real-run report in `evaluation/REPORT.md`; ground-truth metrics unavailable).
- [x] P0-008 Integrate real P0 pipeline and validate on licensed sample clips (orchestrator; outputs intentionally ignored by Git).

## P1
- [ ] P1-001 Pitch line/keypoint detection, validated homography and 2D view (teams_field).
- [ ] P1-002 Corner and goal candidates using geometry + temporal evidence (game_intelligence).
- [ ] P1-003 Pass/high-pass/cross candidate spotting (game_intelligence).

## P2
- [ ] P2-001 Offside prototype with indeterminate option (game_intelligence).
- [ ] P2-002 Foul/card candidate spotting with uncertainty (game_intelligence).

## Acceptance
Each task needs focused tests, paths changed, honest status, reproducible run instructions and no undocumented contract breakage. Do not begin P1 until a usable P0 demo exists.
