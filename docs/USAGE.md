# Usage Guide

This document provides hands-on usage instructions and example workflows for running the CALM evaluation suite.

1) Quick start

 - Activate your Python virtual environment.
 - Install dependencies.
 - Run the harness or launcher to execute tasks and collect results.

Example (run all test tasks once using `uv`):

```powershell
uv sync
uv run python main.py launch
```

Notes:
- This `uv` workflow also works from Windows Subsystem for Linux (WSL).
- If `uv` is unavailable you can run `python main.py` directly as a fallback.

2) Running a specific task or set of tasks

- The harness supports running specific task indices in code/config; if you prefer command-line selection check your launcher or run wrapper for supported flags. If the `--task_ids` flag is not exposed by your runner, run the `main.py` or use the launcher to set `task_ids` in the run configuration programmatically.
- Set the task split (`test`, `train`, or `dev`) in the run configuration when available.

3) Launching agents separately

 - Use the `src/launcher.py` helper to start both green and white agents as separate processes (useful for interactive or networked testing).

4) Interpreting outputs

 - After runs complete, `results/` will contain JSON summaries and per-run logs.
 - Each entry contains `reward_info` with per-dimension scores and `details` explaining violations or successful scheduling.

5) Reproducibility

 - Seed-based randomness is supported; set `seed` in the run configuration to reproduce experiments.

6) Extending the harness

 - Add new persona JSON files or expand `scheduling_requests.json` to broaden scenarios.
 - Add tasks to `tasks_test.py` (or add a new `tasks_*.py`) to include new test cases.
