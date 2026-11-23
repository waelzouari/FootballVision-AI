"""Command-line entrypoint for the P0 MP4 pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import PipelineConfig, run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FootballVision P0 on an MP4 video.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--confidence", type=float, default=0.20)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", help="Ultralytics device, for example 0 or cpu")
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args()
    run = run_pipeline(
        PipelineConfig(
            source=args.source,
            model_path=args.model,
            output_dir=args.output_dir,
            confidence_threshold=args.confidence,
            image_size=args.imgsz,
            device=args.device,
            max_frames=args.max_frames,
        )
    )
    print(f"frames={run.frames_processed} fps={run.fps:.2f}" if run.fps else "frames=0 fps=unmeasured")
    print(f"annotated_video={run.annotated_video}")
    print(f"observations_csv={run.observations_csv}")


if __name__ == "__main__":
    main()
