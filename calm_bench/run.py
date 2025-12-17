# Copyright Sierra

import os
import json
import random
import traceback
from math import comb
import multiprocessing
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from calm_bench.envs import get_env
from calm_bench.agents.base import Agent
from calm_bench.types import EnvRunResult, RunConfig
from litellm import provider_list
from calm_bench.envs.user import UserStrategy


def run(config: RunConfig) -> List[EnvRunResult]:
    assert config.env in ["retail", "airline", "calendar"], "Only retail, airline, and calendar envs are supported"
    assert config.model_provider in provider_list, "Invalid model provider"
    assert config.user_model_provider in provider_list, "Invalid user model provider"
    assert config.agent_strategy in ["tool-calling", "act", "react", "few-shot"], "Invalid agent strategy"
    assert config.task_split in ["train", "test", "dev"], "Invalid task split"
    assert config.user_strategy in [item.value for item in UserStrategy], "Invalid user strategy"

    random.seed(config.seed)
    time_str = datetime.now().strftime("%m%d%H%M%S")
    ckpt_path = f"{config.log_dir}/{config.agent_strategy}-{config.model.split('/')[-1]}-{config.temperature}_range_{config.start_index}-{config.end_index}_user-{config.user_model}-{config.user_strategy}_{time_str}.json"
    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir)

    print(f"Loading user with strategy: {config.user_strategy}")
    env = get_env(
        config.env,
        user_strategy=config.user_strategy,
        user_model=config.user_model,
        user_provider=config.user_model_provider,
        task_split=config.task_split,
    )
    agent = agent_factory(
        tools_info=env.tools_info,
        wiki=env.wiki,
        config=config,
    )
    end_index = (
        len(env.tasks) if config.end_index == -1 else min(config.end_index, len(env.tasks))
    )
    results: List[EnvRunResult] = []
    lock = multiprocessing.Lock()
    if config.task_ids and len(config.task_ids) > 0:
        print(f"Running tasks {config.task_ids} (checkpoint path: {ckpt_path})")
    else:
        print(
            f"Running tasks {config.start_index} to {end_index} (checkpoint path: {ckpt_path})"
    )
    for i in range(config.num_trials):
        if config.task_ids and len(config.task_ids) > 0:
            idxs = config.task_ids
        else:
            idxs = list(range(config.start_index, end_index))
        if config.shuffle:
            random.shuffle(idxs)

        def _run(idx: int) -> EnvRunResult:
            isolated_env = get_env(
                config.env,
                user_strategy=config.user_strategy,
                user_model=config.user_model,
                task_split=config.task_split,
                user_provider=config.user_model_provider,
                task_index=idx,
            )

            print(f"Running task {idx}")
            try:
                res = agent.solve(
                    env=isolated_env,
                    task_index=idx,
                )
                result = EnvRunResult(
                    task_id=idx,
                    reward=res.reward,
                    info=res.info,
                    traj=res.messages,
                    trial=i,
                )
            except Exception as e:
                result = EnvRunResult(
                    task_id=idx,
                    reward=0.0,
                    info={"error": str(e), "traceback": traceback.format_exc()},
                    traj=[],
                    trial=i,
                )
            print(
                "✅" if result.reward == 1 else "❌",
                f"task_id={idx}",
                result.info,
            )
            print("-----")
            with lock:
                data = []
                if os.path.exists(ckpt_path):
                    with open(ckpt_path, "r") as f:
                        data = json.load(f)
                with open(ckpt_path, "w") as f:
                    json.dump(data + [result.model_dump()], f, indent=2)
            return result

        with ThreadPoolExecutor(max_workers=config.max_concurrency) as executor:
            res = list(executor.map(_run, idxs))
            results.extend(res)

    display_metrics(results)

    with open(ckpt_path, "w") as f:
        json.dump([result.model_dump() for result in results], f, indent=2)
        print(f"\n📄 Results saved to {ckpt_path}\n")
    return results


def agent_factory(
    tools_info: List[Dict[str, Any]], wiki, config: RunConfig
) -> Agent:
    if config.agent_strategy == "tool-calling":
        # native tool calling
        from calm_bench.agents.tool_calling_agent import ToolCallingAgent

        return ToolCallingAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=config.model,
            provider=config.model_provider,
            temperature=config.temperature,
        )
    elif config.agent_strategy == "act":
        # `act` from https://arxiv.org/abs/2210.03629
        from calm_bench.agents.chat_react_agent import ChatReActAgent

        return ChatReActAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=config.model,
            provider=config.model_provider,
            use_reasoning=False,
            temperature=config.temperature,
        )
    elif config.agent_strategy == "react":
        # `react` from https://arxiv.org/abs/2210.03629
        from calm_bench.agents.chat_react_agent import ChatReActAgent

        return ChatReActAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=config.model,
            provider=config.model_provider,
            use_reasoning=True,
            temperature=config.temperature,
        )
    elif config.agent_strategy == "few-shot":
        from calm_bench.agents.few_shot_agent import FewShotToolCallingAgent
        assert config.few_shot_displays_path is not None, "Few shot displays path is required for few-shot agent strategy"
        with open(config.few_shot_displays_path, "r") as f:
            few_shot_displays = [json.loads(line)["messages_display"] for line in f]

        return FewShotToolCallingAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=config.model,
            provider=config.model_provider,
            few_shot_displays=few_shot_displays,
            temperature=config.temperature,
        )
    else:
        raise ValueError(f"Unknown agent strategy: {config.agent_strategy}")


def display_metrics(results: List[EnvRunResult]) -> None:
    def is_successful(reward: float) -> bool:
        return (1 - 1e-6) <= reward <= (1 + 1e-6)

    num_trials = len(set([r.trial for r in results]))
    rewards = [r.reward for r in results]
    avg_reward = sum(rewards) / len(rewards)
    # c from https://arxiv.org/pdf/2406.12045
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
        pass_hat_ks[k] = sum_task_pass_hat_k / len(c_per_task_id)
    print(f"🏆 Average reward: {avg_reward}")
    print("📈 Pass^k")
    for k, pass_hat_k in pass_hat_ks.items():
        print(f"  k={k}: {pass_hat_k}")
    # --- Aggregate detailed reward info (if available) ---
    per_task_details = {}
    dims = [
        "constraint_satisfaction",
        "persona_alignment",
        "replanning_robustness",
        "external_feasibility",
    ]
    dim_values = {d: [] for d in dims}
    venue_violations = {}
    conflict_counts = 0

    for r in results:
        info = r.info if isinstance(r.info, dict) else {}
        reward_info = info.get("reward_info") if isinstance(info, dict) else None
        if reward_info and isinstance(reward_info, dict):
            # reward_info expected shape: {"reward": float, "info": {dim scores...}, "actions": [...]}
            ri = reward_info
            ri_inner = ri.get("info") if isinstance(ri.get("info"), dict) else ri.get("info")
            # support both nested 'info' dict (CalendarRewardInfo) or older shapes
            scores = {}
            if isinstance(ri_inner, dict):
                for d in dims:
                    v = ri_inner.get(d)
                    if v is not None:
                        dim_values[d].append(v)
                        scores[d] = v
                # collect venue violations if present
                details = ri_inner.get("details") if isinstance(ri_inner.get("details"), dict) else {}
                ev = details.get("external_feasibility", {}) if isinstance(details, dict) else {}
                vv = ev.get("venue_violations") if isinstance(ev, dict) else None
                if vv and isinstance(vv, list):
                    for item in vv:
                        venue = item.get("venue") if isinstance(item, dict) else None
                        if venue:
                            venue_violations[venue] = venue_violations.get(venue, 0) + 1
                # collect conflict info
                cs_details = details.get("constraint_satisfaction", {}) if isinstance(details, dict) else {}
                conflicts = cs_details.get("conflicts") if isinstance(cs_details, dict) else None
                if conflicts and isinstance(conflicts, list):
                    conflict_counts += len(conflicts)
            per_task_details[r.task_id] = {"reward": ri.get("reward"), "scores": scores, "raw": ri}

    aggregates = {}
    for d in dims:
        vals = dim_values.get(d, [])
        if vals:
            aggregates[d] = {"mean": sum(vals) / len(vals), "count": len(vals)}
        else:
            aggregates[d] = {"mean": None, "count": 0}

    eval_summary = {
        "average_reward": avg_reward,
        "num_tasks": len(results),
        "per_dimension": aggregates,
        "venue_violations": venue_violations,
        "total_conflicts_reported": conflict_counts,
        "per_task": per_task_details,
    }

    # write summary to disk
    try:
        summary_path = f"results/eval_summary_{datetime.now().strftime('%m%d%H%M%S')}.json"
        if not os.path.exists("results"):
            os.makedirs("results")
        with open(summary_path, "w") as sf:
            json.dump(eval_summary, sf, indent=2)
        print(f"📝 Evaluation summary saved to {summary_path}")
    except Exception as e:
        print(f"Could not write evaluation summary: {e}")

    # print compact table
    print("\n=== Per-dimension averages ===")
    for d in dims:
        m = aggregates[d]["mean"]
        cnt = aggregates[d]["count"]
        print(f" - {d}: mean={m} (n={cnt})")
    if venue_violations:
        print("\nTop venue violations:")
        for v, c in sorted(venue_violations.items(), key=lambda x: -x[1])[:10]:
            print(f"  {v}: {c}")
    print(f"\nTotal conflicts reported in details: {conflict_counts}")
