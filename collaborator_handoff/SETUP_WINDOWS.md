# Windows setup

In PowerShell, from a writable development directory:

```powershell
git clone https://github.com/waelzouari/FootballVision-AI.git
cd FootballVision-AI
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[runtime,dev]"
```

If PowerShell blocks activation, use the standard local execution-policy
procedure approved for your machine, or invoke `.venv\Scripts\python.exe`
directly.  Python 3.11 or 3.12 is recommended.

Place an officially obtained model at `models\yolo11n.pt` and an authorized
MP4 at `data\videos\your_clip.mp4`, then follow `VERIFY_INSTALLATION.md`.
