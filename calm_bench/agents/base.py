# Copyright Sierra

import abc
from typing import Optional
from calm_bench.envs.base import Env
from calm_bench.types import SolveResult


class Agent(abc.ABC):
    def __init__(self, emit_trace: bool = False) -> None:
        self._emit_trace = emit_trace
        self._trace: list[dict] = []

    def emit_trace(self, entry_type: str, payload: dict) -> None:
        if not self._emit_trace:
            return
        from datetime import datetime

        self._trace.append({
            "ts": datetime.utcnow().isoformat() + "Z",
            "type": entry_type,
            "payload": payload,
        })

    @abc.abstractmethod
    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 30
    ) -> SolveResult:
        raise NotImplementedError
