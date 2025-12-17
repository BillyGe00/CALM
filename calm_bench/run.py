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
from calm_bench.eval.process_evaluator import score_trace, llm_score_trace


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
                    trace=res.trace,
                    trial=i,
                )
                # attach process-derived scores to the per-task result so checkpoints include them
                try:
                    trace_for_proc = getattr(result, "trace", None)
                    if trace_for_proc and isinstance(trace_for_proc, list):
                        proc = score_trace(trace_for_proc)
                        if getattr(config, "process_eval_model", None):
                            try:
                                llmres = llm_score_trace(trace_for_proc, model=config.process_eval_model, provider=config.model_provider)
                                proc["llm"] = llmres
                            except Exception:
                                proc["llm"] = {"note": "llm scoring failed"}
                        info_dict = result.info if isinstance(result.info, dict) else {}
                        info_dict["process_scores"] = proc
                        result.info = info_dict
                except Exception:
                    # don't fail the run for process scoring attachment
                    pass
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

    display_metrics(results, config)

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
            emit_trace=config.emit_trace,
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
            emit_trace=config.emit_trace,
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
            emit_trace=config.emit_trace,
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
            emit_trace=config.emit_trace,
        )
    else:
        raise ValueError(f"Unknown agent strategy: {config.agent_strategy}")


def display_metrics(results: List[EnvRunResult], config: RunConfig) -> None:
    def is_successful(reward: float) -> bool:
        return (1 - 1e-6) <= reward <= (1 + 1e-6)

    num_trials = len(set([r.trial for r in results]))
    rewards = [r.reward for r in results]
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0

    # per-task pass counts for pass^k computation
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

    print(f"🏆 Average reward: {avg_reward}")
    print("📈 Pass^k")
    for k, pass_hat_k in pass_hat_ks.items():
        print(f"  k={k}: {pass_hat_k}")

    # --- Aggregate detailed reward info (if available) ---
    per_task_details: Dict[int, Dict[str, Any]] = {}
    dims = [
        "constraint_satisfaction",
        "persona_alignment",
        "replanning_robustness",
        "external_feasibility",
    ]
    dim_values = {d: [] for d in dims}
    venue_violations: Dict[str, int] = {}
    conflict_counts = 0

    for r in results:
        info = r.info if isinstance(r.info, dict) else {}
        reward_info = info.get("reward_info") if isinstance(info, dict) else None
        if reward_info and isinstance(reward_info, dict):
            ri = reward_info
            ri_inner = ri.get("info") if isinstance(ri.get("info"), dict) else ri.get("info")
            scores: Dict[str, Any] = {}
            if isinstance(ri_inner, dict):
                for d in dims:
                    v = ri_inner.get(d)
                    if v is not None:
                        dim_values[d].append(v)
                        scores[d] = v
                details = ri_inner.get("details") if isinstance(ri_inner.get("details"), dict) else {}
                ev = details.get("external_feasibility", {}) if isinstance(details, dict) else {}
                vv = ev.get("venue_violations") if isinstance(ev, dict) else None
                if vv and isinstance(vv, list):
                    for item in vv:
                        venue = item.get("venue") if isinstance(item, dict) else None
                        if venue:
                            venue_violations[venue] = venue_violations.get(venue, 0) + 1
                cs_details = details.get("constraint_satisfaction", {}) if isinstance(details, dict) else {}
                conflicts = cs_details.get("conflicts") if isinstance(cs_details, dict) else None
                if conflicts and isinstance(conflicts, list):
                    conflict_counts += len(conflicts)
            per_task_details[r.task_id] = {"reward": ri.get("reward"), "scores": scores, "raw": ri}

        # process-level scoring from emitted trace (if present)
        trace = getattr(r, "trace", None)
        if trace and isinstance(trace, list):
            proc = score_trace(trace)
            per_task_details.setdefault(r.task_id, {"reward": None, "scores": {}, "raw": None})
            per_task_details[r.task_id]["process_scores"] = proc
            # optional LLM-based scoring when requested via config
            if getattr(config, "process_eval_model", None):
                try:
                    llmres = llm_score_trace(trace, model=config.process_eval_model, provider=config.model_provider)
                    per_task_details[r.task_id]["process_scores"]["llm"] = llmres
                except Exception as e:
                    per_task_details[r.task_id]["process_scores"]["llm"] = {"note": f"llm scoring failed: {e}"}

    aggregates: Dict[str, Dict[str, Any]] = {}
    for d in dims:
        vals = dim_values.get(d, [])
        aggregates[d] = {"mean": (sum(vals) / len(vals)) if vals else None, "count": len(vals)}

    eval_summary: Dict[str, Any] = {
        "average_reward": avg_reward,
        "num_tasks": len(results),
        "per_dimension": aggregates,
        "venue_violations": venue_violations,
        "total_conflicts_reported": conflict_counts,
        "per_task": per_task_details,
        "pass_hat_ks": pass_hat_ks,
        "process": {},
    }

    # aggregate simple process metrics (tool_call_success_rate, rounds)
    tcrs: List[float] = []
    rounds: List[int] = []
    for r in results:
        trace = getattr(r, "trace", None)
        if trace and isinstance(trace, list):
            proc = score_trace(trace)
            if proc.get("tool_call_success_rate") is not None:
                tcrs.append(proc.get("tool_call_success_rate"))
            if proc.get("rounds") is not None:
                rounds.append(proc.get("rounds"))
            # collect LLM numeric dims for aggregation when available
            if getattr(config, "process_eval_model", None):
                llm_entry = proc.get("llm") if isinstance(proc, dict) else None
                if isinstance(llm_entry, dict):
                    # gather numeric fields from llm_entry
                    for k, v in llm_entry.items():
                        if isinstance(v, (int, float)):
                            eval_summary.setdefault("process", {}).setdefault("llm_numeric_summaries", {}).setdefault(k, []).append(v)
    eval_summary["process"]["tool_call_success_rate_mean"] = (sum(tcrs) / len(tcrs)) if tcrs else None
    eval_summary["process"]["rounds_mean"] = (sum(rounds) / len(rounds)) if rounds else None

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

    # --- Print process-level aggregates and per-task process scores ---
    print("\n=== Process metrics ===")
    proc = eval_summary.get("process", {})
    print(f" - tool_call_success_rate_mean: {proc.get('tool_call_success_rate_mean')}")
    print(f" - rounds_mean: {proc.get('rounds_mean')}")
    # LLM numeric summaries (if any)
    llm_numeric = proc.get("llm_numeric_summaries") if isinstance(proc, dict) else None
    if llm_numeric:
        print("\nLLM numeric summaries:")
        for k, vals in llm_numeric.items():
            try:
                mean = (sum(vals) / len(vals)) if vals else None
            except Exception:
                mean = None
            print(f"  - {k}: mean={mean} (n={len(vals)})")

    print("\n=== Per-task process scores ===")
    for tid, details in per_task_details.items():
        ps = details.get("process_scores") if isinstance(details, dict) else None
        if not ps:
            print(f" - task {tid}: (no process scores)")
            continue
        print(f" - task {tid}: tool_call_count={ps.get('tool_call_count')}, rounds={ps.get('rounds')}, tool_call_success_rate={ps.get('tool_call_success_rate')}")
        llm = ps.get("llm") if isinstance(ps, dict) else None
        if isinstance(llm, dict):
            numeric = ", ".join(f"{k}={v}" for k, v in llm.items() if isinstance(v, (int, float)))
            note = llm.get("note")
            print(f"    llm: {numeric}; note={note}")
