# Verify the installation

From the repository root with the virtual environment active:

```bash
python -m pytest
```

Expected result: all tests pass without media or weights.

For a real local run, replace the sample paths with files you may use:

```bash
python -m app.run_pipeline data/videos/your_clip.mp4 \
  --model models/yolo11n.pt \
  --output-dir outputs/your_clip
```

On Windows PowerShell, use the same command on one line (or use a backtick for
line continuation).  A successful run prints the processed-frame count and
creates `annotated.mp4`, `observations.csv`, `dashboard.txt` and `run.json` in
the requested output directory.  These generated outputs are intentionally
ignored by Git.

If `ultralytics` or OpenCV is missing, repeat the runtime installation command
from the platform setup guide.  If a video or weights file is missing, pass
the correct local path; the pipeline does not fall back to downloads.
