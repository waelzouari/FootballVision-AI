# YOLO model source and licence

The validated P0 configuration uses the official Ultralytics YOLO11n COCO
weights, file name `yolo11n.pt`.  Obtain them from the official Ultralytics
YOLO11 documentation or its linked official release assets:

- <https://docs.ultralytics.com/models/yolo11/>
- <https://github.com/ultralytics/assets/releases>

Put the downloaded file at `models/yolo11n.pt` (or supply any permitted local
path through `--model`).  The local validation file had SHA-256
`0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`.

Ultralytics documents YOLO11 under AGPL-3.0 or an Enterprise licence.  Review
the applicable terms before use or redistribution, especially for proprietary
work.  FootballVision never downloads weights automatically.

This generic COCO model maps `person` to player and `sports ball` to ball.  It
does not provide a dedicated referee class and is not football fine-tuned.
