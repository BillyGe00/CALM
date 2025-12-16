"""Type definitions for CALM environment."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

RESPOND_ACTION_NAME = "respond"
RESPOND_ACTION_FIELD_NAME = "content"


class Action(BaseModel):
    """Represents an action taken by the agent."""
    name: str
    kwargs: Dict[str, Any]


class Task(BaseModel):
    """Represents a task/scenario for evaluation."""
    user_id: str
    actions: List[Action]
    instruction: str
    outputs: List[str] = []
    perturbation: Optional[Dict[str, Any]] = None  # For re-planning scenarios


class RewardOutputInfo(BaseModel):
    """Reward information based on expected outputs."""
    r_outputs: float
    outputs: Dict[str, bool]


class RewardActionInfo(BaseModel):
    """Reward information based on expected actions/state changes."""
    r_actions: float
    gt_data_hash: str


class CalendarRewardInfo(BaseModel):
    """
    Multi-dimensional reward information for calendar scheduling evaluation.
    Based on proposal success criteria:
    - Constraint Satisfaction
    - Persona Alignment
    - Balance Index
    - Re-Planning Robustness
    - External Feasibility
    """
    constraint_satisfaction: float = 1.0
    persona_alignment: float = 1.0
    balance_index: float = 1.0
    replanning_robustness: float = 1.0
    external_feasibility: float = 1.0
    
    weights: Dict[str, float] = {
        "constraint_satisfaction": 0.25,
        "persona_alignment": 0.25,
        "balance_index": 0.15,
        "external_feasibility": 0.20,
        "replanning_robustness": 0.15,
    }
    
    details: Dict[str, Any] = {}


class RewardResult(BaseModel):
    """Result of reward calculation."""
    reward: float
    info: Union[RewardOutputInfo, RewardActionInfo, CalendarRewardInfo]
    actions: List[Action]


class SolveResult(BaseModel):
    """Result of solving a task."""
    reward: float
    messages: List[Dict[str, Any]]
    info: Dict[str, Any]
    total_cost: Optional[float] = None


class EnvInfo(BaseModel):
    """Environment information returned with each step."""
    task: Task
    source: Optional[str] = None
    user_cost: Optional[float] = None
    reward_info: Optional[RewardResult] = None


class EnvResponse(BaseModel):
    """Response from environment step."""
    observation: str
    reward: float
    done: bool
    info: EnvInfo


class EnvResetResponse(BaseModel):
    """Response from environment reset."""
    observation: str
    info: EnvInfo


class EnvRunResult(BaseModel):
    """Result of running a complete task."""
    task_id: int
    reward: float
    info: Dict[str, Any]
    traj: List[Dict[str, Any]]
    trial: int


class RunConfig(BaseModel):
    """Configuration for running evaluations."""
    model_provider: str
    user_model_provider: str
    model: str
    user_model: str = "gpt-4o"
    num_trials: int = 1
    env: str = "calendar"
    agent_strategy: str = "tool-calling"
    temperature: float = 0.0
    task_split: str = "test"
    start_index: int = 0
    end_index: int = -1
    task_ids: Optional[List[int]] = None
    log_dir: str = "results"
    max_concurrency: int = 1
    seed: int = 10
    shuffle: int = 0
    user_strategy: str = "llm"
    few_shot_displays_path: Optional[str] = None

