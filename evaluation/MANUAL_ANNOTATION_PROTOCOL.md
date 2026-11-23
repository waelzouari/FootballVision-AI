# Small P0 manual annotation protocol

## Sampling

Select 30–50 frames before reviewing predictions: regular time intervals plus
predeclared difficult cases (small ball, occlusion, motion blur, crowded boxes,
camera movement). Prefer a clean licensed clip without baked annotations.
Keep all frames from one video in only one of train, validation or test.

## Labels

For every visible player, referee and ball, draw a tight source-pixel `xyxy`
box. Mark heavily occluded or ambiguous objects as `ignore`; do not invent an
unseen ball. Assign stable player identity only when a human can follow it.
Record jersey team as A, B or unknown; referees are never assigned A/B.

## Review and comparison

Have a second reviewer check all ball labels and a 20% sample of other boxes.
Freeze the annotation file before comparing variants on identical frames.
Report detection precision/recall by class, ball frame recall, and team metrics
only for non-ignored ground truth. Report ID switches/IDF1 only where identity
tracks were annotated. Separately report observed ball rows, fragmentation
proxies, processing FPS and latency; none substitutes for accuracy.
