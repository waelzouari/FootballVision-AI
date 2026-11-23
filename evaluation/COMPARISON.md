# P0 quality comparison — YOLO11n on `corrected_excerpt.mp4`

Run date: 2026-11-23. Each run used the same 375-frame, 15-second 1280×720 input, the same YOLO11n weights, ByteTrack settings and output format. Metrics below are measured on this Mac; they are not accuracy metrics.

| Variant | Person observations | ByteTrack IDs | Median track (frames) | One-frame IDs | Ball frames | Mean ball confidence | FPS | Mean latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial P0 run (effective Ultralytics filter 0.25) | 774 | 76 | 5 | 12 | 33 | 0.439 | 9.58 | 102.8 ms |
| Corrected baseline: 640 px, confidence 0.20 | 787 | 77 | 5 | 12 | 40 | 0.403 | 9.63 | 102.3 ms |
| Lower threshold: 640 px, confidence 0.15 | 787 | 77 | 5 | 12 | 53 | 0.346 | 8.76 | 112.5 ms |
| Higher resolution: 960 px, confidence 0.20 | 777 | 99 | 3 | 25 | 44 | 0.301 | 5.15 | 192.5 ms |

## Findings

- The former adapter allowed Ultralytics' own default confidence filter to run before FootballVision's configured threshold. It now forwards FootballVision's threshold and image size to the model.
- Relative to the initial P0 run, the corrected baseline emits 13 additional player observations and seven additional ball rows at comparable speed. This is a configuration-correctness improvement, not a labelled-accuracy claim.
- Reducing the threshold to 0.15 did not recover player observations. It added 13 ball rows, but at lower mean confidence and lower speed. It is not selected.
- Raising inference resolution to 960 px reduced player observations, fragmented ByteTrack IDs, lowered ball confidence, and halved processing speed. It is not selected.
- The corrected 640 px / 0.20 configuration is retained as the P0 operating point. Its annotations now use opaque black label backgrounds for readability.

## Ball diagnostic

`BALL CANDIDATE` and its yellow circle are baked into the **source** video (for example around 3 seconds); FootballVision does not produce that text. At 960 px the generic COCO model can label that overlay graphic as `sports ball` (0.21 in the sampled frame). The clip is therefore unsuitable for an objective ball-detection comparison: source overlays can both hide the true ball and create false positives. Ball detections remain explicit observations only; no candidate is promoted to a confirmed track without a model detection.

## Teams and IDs

Team labels are still colour-derived, A/B/unknown labels rather than club identities. On the retained run, 493 player observations are A, 198 B and 96 unknown. No reference identity annotations exist, so IDF1/HOTA and a true ID-switch count are not measurable. The 77 temporary IDs, median five-frame lifetime and 12 one-frame IDs demonstrate remaining fragmentation.

## Football-specialist model review

A compatible third-party candidate exists: the Hugging Face model `gianpaj/football-players-detection-1` advertises four classes (ball, goalkeeper, player, referee), YOLOv8x compatibility and AGPL-3.0 licensing. Its published validation results are self-reported and ball recall is only 0.40, so it is not a proven replacement on this camera. It will not be downloaded without explicit approval. Roboflow alternatives require an API key or external inference and are not selected for local P0 evaluation.
