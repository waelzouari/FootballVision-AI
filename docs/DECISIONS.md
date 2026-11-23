# Architecture decision log

- ADR-001: One coordinator + up to two concurrent subagents; bounded file ownership.
- ADR-002: Initial scope is P0 MVP; P1/P2 postponed.
- ADR-003: Contract schema is an implementation proposal; coordinate changes centrally.
- ADR-004: No fixed Codex model to preserve compatibility with signed-in model availability.
- ADR-005: No assumed frontend framework or service API: start with a minimal dashboard; choose implementation only after checking deployment needs and dependencies.
- ADR-006: OpenCV is an optional `video` dependency. Ingestion supports injected capture adapters for deterministic unit tests and does not require bundled media or model downloads.
- ADR-007: The initial detector is an adapter with an injected predictor. It never downloads YOLO weights; connecting a licensed, locally supplied model is deferred to P0 integration.
- ADR-008: Team labels begin as `unknown`. The classifier needs two explicit, distinct calibration samples before emitting A/B; ambiguous or missing crops stay unknown.
- ADR-009: Player tracking starts with a transparent IoU baseline and separate ball-state logic. A ByteTrack backend will be selected only after dependency approval and integration evaluation.
- ADR-010: `data/videos/corrected_excerpt.mp4` is the initial 15-second 720p integration candidate. A visual spot-check shows pre-existing overlay annotations; they must not be treated as ground truth or as FootballVision output.
- ADR-011: The initial runtime has no local YOLO weights, Ultralytics, Torch, or OpenCV. We will not download YOLO weights without explicit approval; therefore real P0 inference and its metrics are currently blocked rather than simulated.
- ADR-012: Following explicit user approval, P0 uses the official Ultralytics YOLO11n COCO weights (`models/yolo11n.pt`) with the local Apple MPS runtime. It maps only COCO `person` and `sports ball`; it must not claim reliable referee detection or football-specialist accuracy.
- ADR-013: The P0 end-to-end validation completed on `corrected_excerpt.mp4`: 375 frames, annotated MP4, CSV, dashboard text and measured timing. No reference labels were supplied, so mAP/precision/recall/IDF1/HOTA are explicitly not reported.
- ADR-014: The source clip has baked football-analysis overlays, including `BALL CANDIDATE`. They confound generic ball detection, so no ball-quality claim or threshold promotion may be based on this clip alone.
- ADR-015: The retained P0 configuration is YOLO11n at 640 px and 0.20 confidence. A 0.15 threshold and 960 px inference were measured on the same clip and did not improve player/track quality enough to offset lower ball confidence, fragmentation or latency.
- ADR-016: Git tracks code, configuration, tests, documentation and textual evaluation reports only. Local model weights, source videos and generated outputs remain ignored. No asset archive is created until the owner confirms that the required videos may be redistributed; collaborators must obtain weights from the official source and use a licensed local MP4.
