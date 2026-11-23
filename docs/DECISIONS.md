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
