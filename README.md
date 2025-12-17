# CALM — Calendar Agent Evaluation Suite

This repository provides CALM, an evaluation platform for calendar-scheduling agents. It includes an automated benchmark harness, a green evaluator agent that instruments persona-aware and feasibility checks, a white agent interface (system under test), curated data/tasks, and tooling to run reproducible multi-trial evaluations.

---

## Setup & Reproduction

This project uses `uv` as the workspace runner. To synchronize and run the evaluation:

```powershell
uv sync
uv run python main.py launch
```

Notes:
- The `uv` workflow works from Windows Subsystem for Linux (WSL) as well.
- As a fallback you can run `python main.py` directly, or start the green and white agents manually via `src/launcher.py` if you do not use `uv`.

Environment keys:
- Create a `.env` file in the repository root and add any required API keys (for example `OPENAI_API_KEY=your_key_here`). The runner or agent processes can load these at runtime.

Results are written to the `results/` folder as JSON summaries. See the `results/` directory for example summaries.

---

## Overview / Goal

CALM is designed to evaluate how well calendar-scheduling agents (white agents) satisfy human-centered constraints and preferences. The green agent orchestrates experiments and scores white-agent outputs on multiple dimensions: constraint satisfaction (no conflicts / sleep constraints), persona alignment (chronotype and preference adherence), replanning robustness (minimize disruptive edits under perturbations), and external feasibility (venue and time constraints). These are combined into a weighted reward and returned with per-dimension diagnostics to support fine-grained analysis.

---

## Repository Layout

- `src/` — orchestration and agent entrypoints (green/white starters, utilities)
- `calm_bench/` — benchmark harness, environment implementations, tasks, and reward logic
  - `envs/calendar/` — calendar-specific environment, reward code, tasks, and data
  - `run.py` — harness to run tasks and collect summaries
- `results/` — output evaluation summaries (JSON)

Key components:
- Green agent: evaluation orchestrator and scorer (defines metrics and computes reward)
- White agent: system under test; expects to receive natural language tasks and interact via tool calls
- Data: personas, baseline calendars, scheduling requests, perturbations, and external constraints

---

## Data and Tasks

The benchmark uses curated JSON datasets representing:
- Personas: chronotype, sleep/wake windows, busy/recurring blocks
- Baseline calendars: initial events to seed conflicts or fully-booked scenarios
- Scheduling requests: natural-language goals used to prompt the white agent
- Perturbations: last-minute changes to test replanning robustness
- External constraints: venue hours and other feasibility data

The tasks are constructed to exercise a range of behaviors: successful scheduling, inability to schedule due to conflicts, venue-hour violations, sleep-window violations, and perturbation-driven replanning scenarios.

---

## Metrics & Scoring

The green evaluator computes the following dimensions and returns a combined reward along with detailed diagnostics for each dimension:

- Constraint Satisfaction: Detects overlapping busy slots and events during persona-defined sleep hours. Conflicts and sleep violations reduce the score with predefined penalties.
- Persona Alignment: Penalizes events that contradict a persona’s chronotype or sleep boundaries.
- Replanning Robustness: Computes an edit-distance-like measure (added + removed + modified events) and penalizes disruptive changes proportionally.
- External Feasibility: Checks event timing against venue operating hours and penalizes violations.

Default weights (can be customized): constraint_satisfaction 0.35, persona_alignment 0.30, replanning_robustness 0.20, external_feasibility 0.15.

When violations are detected, the system supports cooperative repair: agents can negotiate rescheduling attempts, and if no safe compromise is found the white agent may decline to schedule the event. All outcomes and the diagnostic reasons are included in the evaluation output.

---

## Running Evaluations

High level options for running experiments:

- Use the harness to run multiple tasks and trials and produce aggregated summaries.
- Start the green and white agents via the launcher for interactive or distributed testing.
Commands

Below are common commands for running the suite. Run these from the repository root.

- Sync workspace and run the main benchmark (recommended):

```bash
uv sync
uv run python main.py launch
```

- Fallback (no `uv`):

```bash
python main.py
```

Adjust `--task_split` (`test`, `train`, `dev`) and `--task_ids` to run specific tasks. See `calm_bench/run.py` for the CLI and supported arguments.

Developer Tools

The repository includes a small test-runner that aggregates task-level results and writes a final summary. This is intended for development and CI workflows.

- Run the test-runner (all tasks):

```bash
uv sync
uv run python tools/run_all_tests.py --model_provider openai --model gpt-4o
```

- Run the test-runner for a single task:

```bash
uv sync
uv run python tools/run_all_tests.py --task_id 3 --model_provider openai --model gpt-4o
```

- Run the test-runner for multiple tasks:

```bash
uv sync
uv run python tools/run_all_tests.py --task_ids 1,2,5 --model_provider openai --model gpt-4o
```

- Run the test-runner as a module (alternative):

```bash
uv sync
uv run python -m tools.run_all_tests --model_provider openai --model gpt-4o
```

- Fallback (no `uv`):

```bash
PYTHONPATH=. python tools/run_all_tests.py --model_provider openai --model gpt-4o
# PowerShell:
# $env:PYTHONPATH = "."; python tools/run_all_tests.py --model_provider openai --model gpt-4o
```
Adjust `--task_split` (`test`, `train`, `dev`) and `--task_ids` to run specific tasks. See `calm_bench/run.py` for the CLI and supported arguments.

---

## Interpreting Results

Evaluation output files in `results/` contain per-trial JSON entries with a `reward_info` structure that includes the combined reward, per-dimension scores, per-dimension details (conflicts, venue violations, chronotype issues), and the actions taken by the white agent. Aggregate summaries compute per-dimension means and list top violations across tasks.

Use the diagnostics to:
- Identify whether failures are due to hard constraint conflicts, persona mismatch, venue infeasibility, or disruptive replanning.
- Tune the white agent strategies toward reduced edits, better persona alignment, or feasibility-aware planning.

---

## Extending and Reusing

To add a new environment or new persona/task cases:

1. Add JSON data for personas/calendars/requests/perturbations/external constraints.
2. Add a `tasks_*.py` entry that constructs `Task` instances for the new cases.
3. Ensure any new reward dimensions are added in the reward pipeline and wired into the overall weighting logic.

The implementation is modular: the environment computes reward using a single `calculate_calendar_reward` function that can be imported and reused by other environments or external evaluation scripts.

---

## Troubleshooting

- If all per-dimension scores are `1.0`, verify that tasks are actually triggering violations. Many tests return perfect scores when no conflicts, sleep violations, or venue mismatches occur. Use targeted negative tasks to validate detection.
- If the white agent appears to ignore `get_free_slots` or `get_venue_hours` tools, inspect the agent implementation to ensure tool-calling logic passes expected kwargs.

---

## Contributing & License

Contributions are welcome. Please follow the CONTRIBUTING guidelines in the `docs/` folder.

---

## Contact

For questions, open an issue or contact the authors of the repository.
# Agentify Example: CALM-Bench

Example code for agentifying CALM-Bench using A2A and MCP standards.

## Project Structure

```
src/
├── green_agent/    # Assessment manager agent
├── white_agent/    # Target agent being tested
└── launcher.py     # Evaluation coordinator
```

## Installation

```bash
uv sync
```

## Usage

First, configure `.env` with `OPENAI_API_KEY=...`, then

```bash
# Launch complete evaluation
uv run python main.py launch
```
