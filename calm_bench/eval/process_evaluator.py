"""Simple rule-based process evaluator for agent traces.

This module implements a minimal, deterministic scorer that computes a few
process-level metrics from the compact `trace` entries emitted by agents.

The implementation is intentionally small and safe: it requires only the
trace shape we added and uses simple heuristics (counts, rates). More
advanced scorers (LLM-based, semantic similarity) can be added later behind
flags.
"""
from typing import List, Dict, Any, Optional
import json
from litellm import completion


def score_trace(trace: List[Dict[str, Any]], reward_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return simple process-level scores derived from `trace`.

    Outputs include:
      - tool_call_count: number of non-respond actions observed
      - model_response_count: number of model responses recorded
      - env_response_count: number of env responses recorded
      - tool_call_success_rate: fraction of tool calls that produced a non-empty observation
    """
    if not trace:
        return {
            "tool_call_count": 0,
            "model_response_count": 0,
            "env_response_count": 0,
            "tool_call_success_rate": None,
        }

    tool_calls = 0
    tool_call_successes = 0
    model_responses = 0
    env_responses = 0

    tool_names = set()
    for entry in trace:
        t = entry.get("type")
        payload = entry.get("payload") or {}
        if t == "model_response":
            model_responses += 1
        elif t == "env_response":
            env_responses += 1
            action = payload.get("action")
            if action and action != "respond":
                tool_calls += 1
                tool_names.add(action)
                obs = payload.get("observation")
                if obs is not None and str(obs).strip() != "":
                    tool_call_successes += 1

    success_rate = None
    if tool_calls > 0:
        success_rate = tool_call_successes / tool_calls

    # expected rounds heuristic: one round per unique tool called, plus one for planning/response
    expected_rounds = max(1, len(tool_names) + (1 if tool_calls > 0 else 0))
    actual_rounds = env_responses
    rounds_efficiency = None
    if actual_rounds and actual_rounds > 0:
        rounds_efficiency = min(1.0, expected_rounds / actual_rounds)

    # process-level constraint checks using reward_info when available
    constraint_ok_fraction = None
    if reward_info and isinstance(reward_info, dict):
        try:
            ri = reward_info if isinstance(reward_info, dict) else {}
            ri_inner = ri.get("info") if isinstance(ri.get("info"), dict) else ri.get("info")
            cs_details = ri_inner.get("details", {}).get("constraint_satisfaction", {}) if isinstance(ri_inner, dict) else {}
            conflicts = cs_details.get("conflicts") if isinstance(cs_details, dict) else None
            if conflicts is not None and isinstance(conflicts, list):
                # fraction of steps without conflicts: simple heuristic
                total_checks = max(1, len(conflicts) + 1)
                constraint_ok_fraction = 1.0 - (len(conflicts) / total_checks)
        except Exception:
            constraint_ok_fraction = None

    return {
        "tool_call_count": tool_calls,
        "tool_names": list(tool_names),
        "model_response_count": model_responses,
        "env_response_count": env_responses,
        "tool_call_success_rate": success_rate,
        "rounds": actual_rounds,
        "expected_rounds": expected_rounds,
        "rounds_efficiency": rounds_efficiency,
        "constraint_ok_fraction": constraint_ok_fraction,
    }


def llm_score_trace(trace: List[Dict[str, Any]], model: str = "gpt-4o", provider: str = "openai") -> Dict[str, Any]:
    """Ask an LLM to rate the process trace according to a short rubric.

    Returns a dict with keys similar to final reward dims (0-1 floats) and a short
    `note` string explaining the scores. This function is intentionally best-effort
    and wrapped in try/except to avoid breaking the harness if the LLM call fails.
    """
    try:
        # build a compact prompt
        system = {
            "role": "system",
            "content": (
                "You are an evaluator. Given a compact agent trace, rate the agent's process "
                "on the following dimensions (0.0-1.0): constraint_satisfaction, persona_alignment, "
                "replanning_robustness, external_feasibility. Return a JSON object with these fields "
                "and a short 'note'. Be concise."
            ),
        }
        user = {"role": "user", "content": json.dumps({"trace": trace})}
        res = completion(messages=[system, user], model=model, custom_llm_provider=provider, temperature=0.0)
        content = res.choices[0].message.content
        # expect JSON output; attempt to find JSON object in response
        text = content.strip()
        # try parse directly
        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            # try to extract json substring
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(text[start : end + 1])
                except Exception:
                    parsed = {"note": text}
        if not isinstance(parsed, dict):
            parsed = {"note": text}
        return parsed
    except Exception as e:
        return {"note": f"llm scoring failed: {str(e)}"}
