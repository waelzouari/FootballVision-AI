# Shared contracts v1

Canonical types live in contracts/schemas.py. This is an initial design proposal based on the cahier des charges, not a format mandated by the PDF. Orchestrator approves changes.

FramePacket: frame_index, timestamp_s, width, height (image bytes/array kept out of messages).
Detection: object_type player/ball/referee/other, xyxy pixels, confidence [0,1], timestamp_s.
TrackedObject: track_id, object_type, bbox, confidence, timestamp_s, team A/B/unknown, position pixel optional, pitch position optional; never invent positions.
BallState: visible/lost/uncertain; observed_position optional; last_seen timestamp optional; uncertainty explicit.
GameState: timestamp, tracked objects, ball state, optional calibrated pitch status.
EventCandidate: type, timestamp, confidence, status probable/indeterminate, evidence list; no official referee verdict.

Coordinates use original frame pixels; xyxy = (left,top,right,bottom). Pitch metres are allowed only when calibration.validated is true. All timestamps in seconds relative to source video. CSV export must include source video identifier and timestamp. Downstream code must handle None and unknown.

Agent-to-agent communication is through task briefs and short reports, NOT through copying frame tensors, large logs, model weights, or videos into prompts.
