# macOS setup

Run from a terminal:

```bash
git clone https://github.com/waelzouari/FootballVision-AI.git
cd FootballVision-AI
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[runtime,dev]'
```

Python 3.11 or 3.12 is recommended.  The recorded evaluation used Apple MPS,
but the pipeline has no device flag and should use the locally supported
Ultralytics/PyTorch backend.  Confirm the runtime before making any speed
claim.

Place an officially obtained model at `models/yolo11n.pt` and an authorized
MP4 at `data/videos/your_clip.mp4`, then follow `VERIFY_INSTALLATION.md`.
