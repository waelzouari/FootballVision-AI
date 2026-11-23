# Files to transfer outside Git

All paths below are relative to the repository root on the current Mac.  Sizes
are recorded on 2026-11-23.  Git ignores these files; they are not required by
the unit tests.

| Local item | Size | Needed for | Destination on collaborator machine | Transfer status |
| --- | ---: | --- | --- | --- |
| `models/yolo11n.pt` | 5,613,764 bytes (5.36 MiB) | Real P0 inference | `<clone>/models/yolo11n.pt` | Do not copy from this handoff; obtain from the official source in `MODEL_SOURCES.md`. |
| `data/videos/corrected_excerpt.mp4` | 6,457,527 bytes (6.16 MiB) | Reproducing the recorded P0 demo only | `<clone>/data/videos/corrected_excerpt.mp4` | Do not transfer: redistribution rights have not been verified. Use an authorized MP4 instead. |
| Other local `data/videos/*.mp4` clips | 0.78–20.68 MiB each | Exploratory local work; not automated tests | `<clone>/data/videos/` only if authorized | Do not transfer: provenance/redistribution rights are unverified. |
| `outputs/` generated videos, CSVs and reports | up to 20.69 MiB per MP4 | Historical local inspection only | Not needed | Excluded as regenerated outputs. Textual findings are versioned under `evaluation/`. |

`FootballVision_Local_Assets.zip` was **not created**.  No video licence or
redistribution permission was provided, so packaging any local video would be
unsafe.  The supplied model is also excluded from the archive pending the
collaborator obtaining it under the chosen Ultralytics licence.

Never transfer `.venv/`, `.env`, `secrets/`, `*.pem`, `*.key`, caches,
`__pycache__/`, `.pytest_cache/`, or generated `outputs/` directories.
