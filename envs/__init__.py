"""CALM Environment module - contains environments for calendar scheduling evaluation."""

from typing import Optional, Union
from envs.base import Env
from envs.user import UserStrategy


def get_env(
    env_name: str,
    user_strategy: Union[str, UserStrategy],
    user_model: str,
    task_split: str,
    user_provider: Optional[str] = None,
    task_index: Optional[int] = None,
) -> Env:
    """
    Get an environment instance by name.
    
    Args:
        env_name: Name of the environment (e.g., "calendar")
        user_strategy: User simulation strategy
        user_model: Model to use for user simulation
        task_split: Task split to use (e.g., "test", "dev")
        user_provider: Model provider for user simulation
        task_index: Optional specific task index
        
    Returns:
        An initialized environment instance
    """
    if env_name == "calendar":
        from envs.calendar import CalendarDomainEnv

        return CalendarDomainEnv(
            user_strategy=user_strategy,
            user_model=user_model,
            task_split=task_split,
            user_provider=user_provider,
            task_index=task_index,
        )
    else:
        raise ValueError(f"Unknown environment: {env_name}")
