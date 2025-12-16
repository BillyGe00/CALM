"""Calendar domain environment."""

from typing import Optional, Union, List, Dict, Any

from envs.base import Env
from envs.user import UserStrategy
from envs.types import (
    Action,
    RewardResult,
    CalendarRewardInfo,
    RESPOND_ACTION_NAME,
)
from envs.calendar.data import load_data
from envs.calendar.tools import ALL_TOOLS
from envs.calendar.wiki import WIKI
from envs.calendar.rules import RULES
from envs.calendar.tasks import get_tasks
from envs.calendar.reward import calculate_calendar_reward


class CalendarDomainEnv(Env):
    """
    Calendar scheduling domain environment.
    
    This environment simulates a calendar scheduling assistant that helps
    users manage their time by scheduling events, respecting constraints,
    and handling schedule perturbations.
    """
    
    def __init__(
        self,
        user_strategy: Union[str, UserStrategy] = UserStrategy.LLM,
        user_model: str = "gpt-4o",
        user_provider: Optional[str] = None,
        task_split: str = "test",
        task_index: Optional[int] = None,
    ):
        """
        Initialize the calendar domain environment.
        
        Args:
            user_strategy: Strategy for user simulation (llm, human, react, etc.)
            user_model: Model to use for LLM-based user simulation
            user_provider: Provider for the user model
            task_split: Which task split to use (test, dev, random)
            task_index: Specific task index to use (optional)
        """
        tasks = get_tasks(task_split)
        
        super().__init__(
            data_load_func=load_data,
            tools=ALL_TOOLS,
            tasks=tasks,
            wiki=WIKI,
            rules=RULES,
            user_strategy=user_strategy,
            user_model=user_model,
            user_provider=user_provider,
            task_index=task_index,
        )
        
        # Define tools that terminate the episode when called
        self.terminate_tools = []
        
        # Store original events for perturbation scenarios
        self._original_events: Optional[List[Dict[str, Any]]] = None
    
    def reset(self, task_index: Optional[int] = None):
        """Reset environment and store original events for perturbation tracking."""
        response = super().reset(task_index)
        
        # Store original events for re-planning robustness evaluation
        user_id = self.task.user_id if self.task else None
        if user_id and "calendars" in self.data:
            events = self.data["calendars"].get(user_id, {}).get("events", [])
            self._original_events = [e.copy() for e in events]
        else:
            self._original_events = []
        
        return response
    
    def _get_current_events(self) -> List[Dict[str, Any]]:
        """Get current events for the task user from calendar."""
        if not self.task:
            return []
        user_id = self.task.user_id
        if "calendars" in self.data:
            return self.data["calendars"].get(user_id, {}).get("events", [])
        return []
    
    def _get_persona(self) -> Dict[str, Any]:
        """Get persona for the task user."""
        if not self.task:
            return {}
        user_id = self.task.user_id
        
        personas = self.data.get("personas", {})
        
        # Handle both dict and list formats
        if isinstance(personas, dict) and "personas" in personas:
            personas_list = personas["personas"]
        elif isinstance(personas, list):
            personas_list = personas
        else:
            personas_list = []
        
        # Find matching persona
        for p in personas_list:
            if p.get("id") == user_id:
                return p
        
        return {}
    
    def _get_external_constraints(self) -> Dict[str, Any]:
        """Get external constraints (venues, etc.)."""
        return self.data.get("external_constraints", {})
    
    def _extract_day_from_instruction(self) -> str:
        """Try to extract day of week from task instruction."""
        if not self.task:
            return "monday"
        
        instruction = self.task.instruction.lower()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for day in days:
            if day in instruction:
                return day
        
        return "monday"  # Default
    
    def calculate_reward(self) -> RewardResult:
        """
        Calculate reward using multi-dimensional calendar-specific metrics.
        
        Based on proposal success criteria:
        1. Constraint Satisfaction - No conflicts, required events scheduled
        2. Persona Alignment - Schedule matches user preferences
        3. Re-Planning Robustness - Minimal changes under perturbations
        4. External Feasibility - Activities within venue hours
        """
        # Get current state
        calendar_events = self._get_current_events()
        persona = self._get_persona()
        external_constraints = self._get_external_constraints()
        
        # Extract day from instruction
        day_of_week = self._extract_day_from_instruction()
        
        # Check if this is a perturbation scenario
        task_has_perturbation = (
            self.task and 
            hasattr(self.task, 'perturbation') and 
            self.task.perturbation
        )
        original_events = self._original_events if task_has_perturbation else None
        
        # Calculate multi-dimensional reward
        total_reward, reward_details = calculate_calendar_reward(
            persona=persona,
            calendar_events=calendar_events,
            external_constraints=external_constraints,
            day_of_week=day_of_week,
            original_events=original_events,
        )
        
        # Build reward info
        scores = reward_details.get("scores", {})
        info = CalendarRewardInfo(
            constraint_satisfaction=scores.get("constraint_satisfaction", 1.0),
            persona_alignment=scores.get("persona_alignment", 1.0),
            balance_index=1.0,  # Not used in simplified version
            replanning_robustness=scores.get("replanning_robustness", 1.0),
            external_feasibility=scores.get("external_feasibility", 1.0),
            weights=reward_details.get("weights", {}),
            details=reward_details.get("details", {}),
        )
        
        # Get non-respond actions for logging
        actions = [
            action for action in self.actions 
            if action.name != RESPOND_ACTION_NAME
        ]
        
        return RewardResult(
            reward=total_reward,
            info=info,
            actions=actions,
        )
