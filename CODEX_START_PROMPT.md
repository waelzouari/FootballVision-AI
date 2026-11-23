# Paste into Codex Desktop, opened at the FootballVision repository root

Act as the primary FootballVision orchestrator and follow AGENTS.md. Confirm project trust and that .codex/config.toml and six named agents are loaded; if not, report the issue and do not pretend delegation works.

Goal: implement P0 MVP only, then progressively P1 and P2 after acceptance. Do not build P1/P2 now. Read docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/TASKS.md, docs/DECISIONS.md and inspect existing repository changes. If the original FootballVision PDF is available, use it as the requirements authority. Do not overwrite existing work.

First inspect repository state and validate Python contract tests. Create only missing project structure. Establish dependency versions suitable for this environment and ask before any large model/data download. Use at most 2 concurrent specialist subagents; delegate bounded independent tasks with exclusive file ownership and acceptance tests. Prefer starting detection and dashboard fixture work in parallel, then tracking and teams as their inputs become available. Evaluation can review independently. Keep event agent idle during P0.

For each task, give agent only ID, relevant files, required interface, and acceptance criteria. Require <=120-word completion reports. You alone integrate changes and update docs/TASKS.md and docs/DECISIONS.md. Stop and ask for decisions only on real blockers. At the end of this session report completed tasks, tests run, blockers, and next milestone in <=180 words. Never invent model accuracy or FPS.
