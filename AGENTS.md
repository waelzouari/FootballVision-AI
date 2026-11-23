# FootballVision — Codex development policy

## Mission
Implement the FootballVision single-camera football analysis system incrementally, using the provided cahier des charges as the source of requirements. Start with P0: MP4/camera ingestion, YOLO player/referee/ball detection, ByteTrack player tracking and separate ball tracking, team A/B/unknown, annotated video, CSV and basic dashboard, plus evaluation. P1: validated field calibration/2D projection, corners/goals, passes. P2: offside, fouls, cards as uncertain prototypes.

## Coordination
You are the PRIMARY ORCHESTRATOR. Delegate only bounded, independent tasks to named specialist agents; never have more than 2 subagents active. Do not delegate trivial edits. Assign exclusive file ownership. Never spawn agents merely to discuss plans. Do not ask agents to read the whole repository or full PDF. Share task ID, exact paths, relevant contract, acceptance criteria and brief context. If a dependency is unfinished, implement sequentially. Collect brief completion reports and integrate centrally.

## Required reading
Read docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/TASKS.md and only relevant files. The original PDF is the authority for requirements when present; do not assume it is available in the repository. Record assumptions in docs/DECISIONS.md. Avoid unnecessary web research.

## Shared rules
- Python modules use typed interfaces defined in contracts/schemas.py. Changes to contracts require orchestrator approval before downstream implementation.
- Only orchestrator edits shared contracts, docs/TASKS.md, docs/DECISIONS.md, global dependency files and cross-module integration.
- Specialist agents edit only their assigned owned directories and local tests; request other edits in their final report.
- No fabrication of missing player/ball positions, inferred metres without validated homography, or definitive referee decisions. Emit unknown/uncertain when needed.
- Prefer pretrained models and reproducible short sample clips. No automatic downloading of large datasets/weights without approval. Check dataset/video/model licences.
- Separate train/validation/test by match or video. No secrets or media binaries in git. Preserve existing user changes.
- Validate using focused tests, then orchestrator runs integration tests. Do not claim performance numbers without measurement on actual hardware.
- Do not create fake implementations or demo results disguised as real inference. Mark placeholders explicitly.

## Mandatory subagent completion report (maximum 120 words)
TASK: <ID>
STATUS: DONE | BLOCKED | PARTIAL
FILES: <changed paths only>
INTERFACE: <input -> output or none>
TESTS: <command and result>
BLOCKERS: <none or precise blocker>
NEXT: <one short next action>

## Orchestrator response
Summarize progress in <= 180 words: completed tasks, tests, blockers, next task. Do not paste logs or whole files unless explicitly requested.
