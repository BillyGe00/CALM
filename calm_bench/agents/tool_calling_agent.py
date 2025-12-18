# Copyright Sierra

import json
from litellm import completion
from typing import List, Optional, Dict, Any

from calm_bench.agents.base import Agent
from calm_bench.envs.base import Env
from calm_bench.types import SolveResult, Action, RESPOND_ACTION_NAME


class ToolCallingAgent(Agent):
    def __init__(
        self,
        tools_info: List[Dict[str, Any]],
        wiki: str,
        model: str,
        provider: str,
        temperature: float = 0.0,
        emit_trace: bool = False,
    ):
        super().__init__(emit_trace=emit_trace)
        self.tools_info = tools_info
        self.wiki = wiki
        self.model = model
        self.provider = provider
        self.temperature = temperature

    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 30
    ) -> SolveResult:
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0
        # Build initial messages; include a short system constraint that
        # forces the model to always use the task's `user_id` when calling tools
        task = info.get("task") if isinstance(info, dict) else None
        user_id = None
        if task and isinstance(task, dict):
            user_id = task.get("user_id")

        messages: List[Dict[str, Any]] = [{"role": "system", "content": self.wiki}]
        if user_id:
            system_constraint = (
                "System constraint: When calling tools (e.g., get_calendar, get_free_slots, add_event), "
                f"always pass the task's user_id value '{user_id}' as the `user_id` argument. "
                "Do not substitute defaults like 'default_user'."
            )
            messages.append({"role": "system", "content": system_constraint})
        messages.append({"role": "user", "content": obs})
        self.emit_trace("reset", {"observation": obs, "task_index": task_index})
        for _ in range(max_num_steps):
            res = completion(
                messages=messages,
                model=self.model,
                custom_llm_provider=self.provider,
                tools=self.tools_info,
                temperature=self.temperature,
            )
            next_message = res.choices[0].message.model_dump()
            # emit a compact model response trace (avoid storing full prompts)
            self.emit_trace("model_response", {"tool_calls": [tc.get("function", {}).get("name") for tc in (next_message.get("tool_calls") or [])], "content_len": len(next_message.get("content") or "")})
            total_cost += res._hidden_params["response_cost"] or 0
            action = message_to_action(next_message)
            env_response = env.step(action)
            self.emit_trace("env_response", {"action": action.name, "action_kwargs": action.kwargs, "observation": env_response.observation, "reward": env_response.reward, "done": env_response.done})
            reward = env_response.reward
            info = {**info, **env_response.info.model_dump()}
            if action.name != RESPOND_ACTION_NAME:
                next_message["tool_calls"] = next_message["tool_calls"][:1]
                messages.extend(
                    [
                        next_message,
                        {
                            "role": "tool",
                            "tool_call_id": next_message["tool_calls"][0]["id"],
                            "name": next_message["tool_calls"][0]["function"]["name"],
                            "content": env_response.observation,
                        },
                    ]
                )
            else:
                messages.extend(
                    [
                        next_message,
                        {"role": "user", "content": env_response.observation},
                    ]
                )
            if env_response.done:
                break
        return SolveResult(
            reward=reward,
            info=info,
            messages=messages,
            total_cost=total_cost,
            trace=self._trace,
        )


def message_to_action(
    message: Dict[str, Any],
) -> Action:
    if "tool_calls" in message and message["tool_calls"] is not None and len(message["tool_calls"]) > 0 and message["tool_calls"][0]["function"] is not None:
        tool_call = message["tool_calls"][0]
        return Action(
            name=tool_call["function"]["name"],
            kwargs=json.loads(tool_call["function"]["arguments"]),
        )
    else:
        return Action(name=RESPOND_ACTION_NAME, kwargs={"content": message["content"]})
