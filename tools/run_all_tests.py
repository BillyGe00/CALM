#!/usr/bin/env python3
"""Run all defined tasks and produce a final pass/fail summary.

This script is a thin wrapper around the benchmark harness. It constructs a
RunConfig from CLI arguments, invokes the harness, and writes a final JSON
summary to `results/` with per-task pass/fail and per-dimension aggregates.

Usage examples:
  python tools/run_all_tests.py --model_provider openai --model gpt-4o
  python tools/run_all_tests.py --agent_strategy tool-calling --task_split test

Note: This script depends on the same runtime environment as the harness.
If you normally run via `uv run python main.py launch`, run that instead.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from math import comb
from typing import List

# Ensure repository root is on sys.path so `calm_bench` imports work
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from calm_bench.run import run
from calm_bench.types import RunConfig, EnvRunResult


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model_provider", default="openai")
    p.add_argument("--user_model_provider", default="openai")
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--user_model", default="gpt-4o")
    p.add_argument("--num_trials", type=int, default=1)
    p.add_argument("--env", default="calendar")
    p.add_argument("--agent_strategy", default="tool-calling")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--task_split", default="test")
    p.add_argument("--start_index", type=int, default=0)
    p.add_argument("--end_index", type=int, default=-1)
    p.add_argument("--task_ids", default=None, help="Comma-separated list of task indices to run")
    p.add_argument("--task_id", type=int, default=None, help="Single task index to run (overrides --task_ids if provided)")
    p.add_argument("--log_dir", default="results")
    p.add_argument("--max_concurrency", type=int, default=1)
    p.add_argument("--seed", type=int, default=10)
    p.add_argument("--shuffle", type=int, default=0)
    p.add_argument("--user_strategy", default="llm")
    return p.parse_args()


def is_successful(reward: float) -> bool:
    return (1 - 1e-6) <= reward <= (1 + 1e-6)


def summarize_results(results: List[EnvRunResult]):
    num_trials = len(set([r.trial for r in results]))
    rewards = [r.reward for r in results]
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0

    c_per_task_id: dict[int, int] = {}
    for result in results:
        if result.task_id not in c_per_task_id:
            c_per_task_id[result.task_id] = 1 if is_successful(result.reward) else 0
        else:
            c_per_task_id[result.task_id] += 1 if is_successful(result.reward) else 0

    pass_hat_ks: dict[int, float] = {}
    for k in range(1, num_trials + 1):
        sum_task_pass_hat_k = 0
        for c in c_per_task_id.values():
            sum_task_pass_hat_k += comb(c, k) / comb(num_trials, k)
        pass_hat_ks[k] = sum_task_pass_hat_k / len(c_per_task_id) if c_per_task_id else 0.0

    # Aggregate per-dimension values if reward_info present in result.info
    dims = [
        "constraint_satisfaction",
        "persona_alignment",
        "replanning_robustness",
        "external_feasibility",
    ]
    dim_values = {d: [] for d in dims}
    per_task_details = {}

    for r in results:
        info = r.info if isinstance(r.info, dict) else {}
        reward_info = info.get("reward_info") if isinstance(info, dict) else None
        if reward_info and isinstance(reward_info, dict):
            ri = reward_info
            ri_inner = ri.get("info") if isinstance(ri.get("info"), dict) else ri.get("info")
            scores = {}
            if isinstance(ri_inner, dict):
                for d in dims:
                    v = ri_inner.get(d)
                    if v is not None:
                        dim_values[d].append(v)
                        scores[d] = v
            per_task_details[r.task_id] = {
                "reward": ri.get("reward"),
                "scores": scores,
                "raw": ri,
            }

    aggregates = {}
    for d in dims:
        vals = dim_values.get(d, [])
        aggregates[d] = {"mean": (sum(vals) / len(vals)) if vals else None, "count": len(vals)}

    eval_summary = {
        "average_reward": avg_reward,
        "num_tasks": len(results),
        "per_dimension": aggregates,
        "per_task": per_task_details,
        "pass_hat_ks": pass_hat_ks,
    }

    return eval_summary


def main():
    args = parse_args()

    task_ids = None
    # Support a single task selection via --task_id (overrides --task_ids)
    if args.task_id is not None:
        task_ids = [int(args.task_id)]
    elif args.task_ids:
        try:
            task_ids = [int(x.strip()) for x in args.task_ids.split(",") if x.strip()]
        except Exception:
            print("Could not parse --task_ids; ignoring")
            task_ids = None

    config = RunConfig(
        model_provider=args.model_provider,
        user_model_provider=args.user_model_provider,
        model=args.model,
        user_model=args.user_model,
        num_trials=args.num_trials,
        env=args.env,
        agent_strategy=args.agent_strategy,
        temperature=args.temperature,
        task_split=args.task_split,
        start_index=args.start_index,
        end_index=args.end_index,
        task_ids=task_ids,
        log_dir=args.log_dir,
        max_concurrency=args.max_concurrency,
        seed=args.seed,
        shuffle=args.shuffle,
        user_strategy=args.user_strategy,
    )

    print("Running harness with config:", config.dict())

    results = run(config)

    summary = summarize_results(results)

    # save summary
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    summary_path = os.path.join(args.log_dir, f"final_eval_summary_{datetime.now().strftime('%m%d%H%M%S')}.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Final evaluation summary written to {summary_path}")


if __name__ == "__main__":
    main()
