# P0 Windows GPU optimization — `corrected_excerpt.mp4`
Run date: 2026-11-23. All runs used the same 375 decoded frames, YOLO11n
weights, 640 px inference size and 0.20 confidence threshold. Processing FPS
is wall-clock throughput, not the source video's fixed 25 FPS.

## Environment

- Windows x64, Python 3.12.10, NVIDIA RTX 4050 Laptop GPU (6 GB).
- NVIDIA driver 581.86; `nvidia-smi` reported CUDA capability 13.0.
- Official PyTorch wheels: 2.11.0+cu128 and torchvision 0.26.0+cu128.
- `torch.cuda.is_available()` was true. Explicit YOLO `device=0` inference
  allocated CUDA memory. No global CUDA Toolkit was installed.
- GPU baseline peak PyTorch memory: 56.1 MiB allocated, 68.0 MiB reserved.

## CPU versus GPU baseline

| Device | Time | Processing FPS | Mean latency | P95 latency | Player rows | Ball rows | IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CPU | 16.509 s | 22.72 | 42.31 ms | 36.65 ms | 772 | 40 | 75 |
| CUDA | 8.480 s | 44.22 | 21.08 ms | 17.49 ms | 767 | 40 | 75 |

CUDA provided 1.95× wall-clock throughput. Mean latency exceeds P95 because
the mean includes a large one-time model/CUDA warm-up outlier. CPU and CUDA
produced five different player rows due to backend numerical variation; this
is not an accuracy difference without ground truth.

## Baseline versus optimized CUDA

| Variant | Player rows | IDs | Median track observations | One-frame IDs | IDs ≤3 frames | Known team transitions | Unknown rows | Ball rows | FPS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 767 | 75 | 5.0 | 12 | 30 | 3 | 95 | 40 | 44.22 |
| Optimized | 951 | 64 | 7.5 | 6 | 18 | 0 | 99 | 40 | 45.90 |

The selected tracking change raises ByteTrack `match_thresh` from 0.80 to
0.85. Fragmentation proxies improved, but they are not ID switches, IDF1 or
HOTA. The higher player-row count means more current-frame detections were
associated and exported; it is not evidence of better detection recall.

Team labels now lock per track after the initial evidence threshold. This
removed observed A/B changes while retaining explicit unknown results. Team
accuracy and F1 remain unmeasurable without labelled jerseys.

## Ball diagnostic

YOLO11n emitted 40 ball rows in both CUDA variants. Twelve baseline detections
on frames 2–13 form a near-static sequence associated with graphics already
baked into the source. Lowering confidence to 0.15 adds 13 ambiguous candidates,
including more overlay-region detections, so it was rejected. These counts are
observations, not ball recall. No specialized weights were downloaded.

## Limitations and recommendation

The clip contains overlays and has no player boxes, identities, team labels or
ball ground truth. Precision, recall, mAP, ID switches, IDF1, HOTA and team F1
cannot be reported. Annotate clean, representative frames using the companion
protocol before judging a football-specific model or fine-tuning. Fine-tuning
may become beneficial if annotation confirms systematic small-ball or distant-
player misses, but current evidence is insufficient to recommend training.

