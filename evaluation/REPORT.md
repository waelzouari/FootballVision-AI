# P0 evaluation — `corrected_excerpt.mp4`

Run date: 2026-11-23

## Input and runtime

- Input: `data/videos/corrected_excerpt.mp4` (H.264, 1280×720, 25 FPS, 15.0 s, 375 frames).
- Runtime: Python 3.12.11; OpenCV 4.10.0; PyTorch 2.2.2; Ultralytics 8.4.191 on Apple MPS.
- Weights: `models/yolo11n.pt`, downloaded from Ultralytics' official assets release `v8.4.0`.
- Model: YOLO11n detection, COCO 80 classes. FootballVision maps `person` to player and `sports ball` to ball. COCO has no dedicated referee class.
- Licence: Ultralytics YOLO11 is available under AGPL-3.0 or an Enterprise licence. Confirm the applicable licence before a proprietary deployment: <https://docs.ultralytics.com/models/yolo11/>.

## End-to-end result

- Completed: 375 / 375 frames.
- Annotated MP4: `outputs/corrected_excerpt_yolo11n/annotated.mp4` (MPEG-4, 1280×720, 25 FPS, 15.0 s, 375 frames).
- CSV: `outputs/corrected_excerpt_yolo11n/observations.csv` (807 observed-object rows).
- Player observations: 774; distinct temporary ByteTrack IDs: 76.
- Ball observations: 33 frames. The tracker reports `lost` or `uncertain` for other frames; it does not fabricate ball positions.
- Team labels: 487 A, 193 B, 94 unknown. They are colour-based, calibration-dependent labels, not semantic club identities.
- Processing: 39.158 s wall time, 9.577 FPS, 102.796 ms mean frame latency, 113.963 ms p95 latency.

## Limitations

- No labelled ground truth was supplied. Precision, recall, mAP, IDF1 and HOTA are therefore **not measurable**.
- This is a generic COCO model, not football fine-tuned. Referees are detected only as generic persons and are not exported as confirmed referees.
- The source video contains pre-existing overlay annotations. They are neither ground truth nor FootballVision output; FootballVision labels use `player #<id>` and optional A/B/unknown labels.
- The relatively high number of temporary IDs demonstrates identity fragmentation under this baseline; it is not an IDF1 score.
