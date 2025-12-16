"""
Task generator for random combination of personas, requests, and perturbations.

This module generates evaluation tasks by randomly combining:
- Persona (user profile with preferences and constraints)
- Scheduling Request (what the user wants to schedule)
- Perturbation (optional schedule disruption)
"""

import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from envs.types import Task, Action
from envs.calendar.data import load_data


# Day name mapping
DAYS_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6
}

DAYS_LIST = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_target_date(day_of_week: str, base_date: Optional[datetime] = None) -> str:
    """
    Get the next occurrence of a given day of week.
    
    Args:
        day_of_week: Day name (e.g., "monday")
        base_date: Base date to calculate from (default: today)
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    if base_date is None:
        base_date = datetime.now()
    
    target_day = DAYS_MAP.get(day_of_week.lower(), 0)
    current_day = base_date.weekday()
    
    days_ahead = target_day - current_day
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    target_date = base_date + timedelta(days=days_ahead)
    return target_date.strftime("%Y-%m-%d")


def parse_time_range(time_range: str) -> tuple[str, str]:
    """
    Parse time range string like "10:00-12:00" into start and end times.
    
    Returns:
        (start_time, end_time) tuple
    """
    parts = time_range.split("-")
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "00:00", "23:59"


def get_busy_slots_for_day(persona: Dict, day_of_week: str) -> List[Dict]:
    """
    Get all busy time slots for a persona on a specific day.
    
    Args:
        persona: Persona dictionary
        day_of_week: Day name (e.g., "monday")
    
    Returns:
        List of busy slots with start_time and end_time
    """
    busy_slots = []
    busy_blocks = persona.get("busy_blocks", [])
    
    day_lower = day_of_week.lower()
    
    for block in busy_blocks:
        days = [d.lower() for d in block.get("days", [])]
        if day_lower in days:
            time_range = block.get("time", "")
            start, end = parse_time_range(time_range)
            busy_slots.append({
                "start_time": start,
                "end_time": end
            })
    
    return busy_slots


def find_free_slots(
    busy_slots: List[Dict],
    wake_time: str = "07:00",
    sleep_time: str = "23:00",
    min_duration_minutes: int = 30
) -> List[Dict]:
    """
    Find free time slots given busy slots and awake hours.
    
    Returns:
        List of free slots with start_time, end_time, and duration_minutes
    """
    def time_to_minutes(t: str) -> int:
        h, m = map(int, t.split(":"))
        return h * 60 + m
    
    def minutes_to_time(m: int) -> str:
        return f"{m // 60:02d}:{m % 60:02d}"
    
    # Sort busy slots by start time
    sorted_busy = sorted(busy_slots, key=lambda x: time_to_minutes(x["start_time"]))
    
    wake_minutes = time_to_minutes(wake_time)
    sleep_minutes = time_to_minutes(sleep_time)
    
    free_slots = []
    current_time = wake_minutes
    
    for slot in sorted_busy:
        slot_start = time_to_minutes(slot["start_time"])
        slot_end = time_to_minutes(slot["end_time"])
        
        # Check for free time before this busy slot
        if slot_start > current_time:
            duration = slot_start - current_time
            if duration >= min_duration_minutes:
                free_slots.append({
                    "start_time": minutes_to_time(current_time),
                    "end_time": minutes_to_time(slot_start),
                    "duration_minutes": duration
                })
        
        current_time = max(current_time, slot_end)
    
    # Check for free time after last busy slot until sleep time
    if current_time < sleep_minutes:
        duration = sleep_minutes - current_time
        if duration >= min_duration_minutes:
            free_slots.append({
                "start_time": minutes_to_time(current_time),
                "end_time": minutes_to_time(sleep_minutes),
                "duration_minutes": duration
            })
    
    return free_slots


def generate_instruction(
    persona: Dict,
    request: Dict,
    day_of_week: str
) -> str:
    """
    Generate a natural language instruction combining persona context and request.
    """
    persona_name = persona.get("name", "User")
    persona_role = persona.get("role", "")
    request_text = request.get("request", "")
    
    # Replace "Tomorrow" with specific day
    instruction = request_text.replace("Tomorrow", f"On {day_of_week.capitalize()}")
    instruction = instruction.replace("tomorrow", day_of_week.capitalize())
    
    # Add persona context
    context = f"You are helping {persona_name}, a {persona_role}. "
    
    chronotype = persona.get("chronotype", "flexible")
    if chronotype == "morning_person":
        context += "They prefer morning activities. "
    elif chronotype == "evening_person":
        context += "They prefer evening activities. "
    
    return context + instruction


def generate_task(
    persona_id: Optional[str] = None,
    request_id: Optional[str] = None,
    day_of_week: Optional[str] = None,
    include_perturbation: bool = False,
    seed: Optional[int] = None
) -> Task:
    """
    Generate a random task by combining persona, request, and optional perturbation.
    
    Args:
        persona_id: Specific persona ID (random if None)
        request_id: Specific request ID (random if None)
        day_of_week: Specific day (random weekday if None)
        include_perturbation: Whether to include a perturbation
        seed: Random seed for reproducibility
    
    Returns:
        Generated Task instance
    """
    if seed is not None:
        random.seed(seed)
    
    # Load data
    data = load_data()
    personas = data.get("personas", {})
    requests = data.get("scheduling_requests", {}).get("scheduling_requests", [])
    perturbations = data.get("perturbations", {}).get("perturbations", [])
    
    # Handle personas as either dict or list
    if isinstance(personas, dict) and "personas" in personas:
        personas_list = personas["personas"]
    elif isinstance(personas, list):
        personas_list = personas
    else:
        personas_list = list(personas.values()) if isinstance(personas, dict) else []
    
    # Select persona
    if persona_id:
        persona = next((p for p in personas_list if p.get("id") == persona_id), None)
        if not persona:
            persona = random.choice(personas_list) if personas_list else {}
    else:
        persona = random.choice(personas_list) if personas_list else {}
    
    # Select request
    if request_id:
        request = next((r for r in requests if r.get("id") == request_id), None)
        if not request:
            request = random.choice(requests) if requests else {}
    else:
        request = random.choice(requests) if requests else {}
    
    # Select day of week
    if not day_of_week:
        day_of_week = random.choice(DAYS_LIST[:5])  # Weekdays only by default
    
    # Generate instruction
    instruction = generate_instruction(persona, request, day_of_week)
    
    # Add perturbation to instruction if requested
    perturbation = None
    if include_perturbation and perturbations:
        perturbation = random.choice(perturbations)
        pert_desc = perturbation.get("description", "")
        if pert_desc:
            instruction += f" Additionally: {pert_desc}."
    
    # Build task
    task = Task(
        user_id=persona.get("id", "unknown"),
        instruction=instruction,
        actions=[],  # No predefined actions for rule-based evaluation
        outputs=[],  # No predefined outputs
        perturbation=perturbation
    )
    
    return task


def generate_task_batch(
    count: int,
    include_perturbations: bool = False,
    seed: Optional[int] = None
) -> List[Task]:
    """
    Generate a batch of random tasks.
    
    Args:
        count: Number of tasks to generate
        include_perturbations: Whether to include perturbations (randomly)
        seed: Random seed for reproducibility
    
    Returns:
        List of generated Task instances
    """
    if seed is not None:
        random.seed(seed)
    
    tasks = []
    for i in range(count):
        include_pert = include_perturbations and random.random() < 0.3  # 30% chance
        task = generate_task(
            include_perturbation=include_pert,
            seed=seed + i if seed else None
        )
        tasks.append(task)
    
    return tasks


def get_task_context(task: Task) -> Dict[str, Any]:
    """
    Get additional context for a task (persona info, busy slots, etc.)
    
    Useful for debugging and understanding task setup.
    """
    data = load_data()
    personas = data.get("personas", {})
    
    if isinstance(personas, dict) and "personas" in personas:
        personas_list = personas["personas"]
    else:
        personas_list = []
    
    persona = next((p for p in personas_list if p.get("id") == task.user_id), {})
    
    return {
        "persona": persona,
        "busy_slots": get_busy_slots_for_day(persona, "monday"),
        "chronotype": persona.get("chronotype", "flexible"),
        "wake_time": persona.get("wake_time", "07:00"),
        "sleep_time": persona.get("sleep_time", "23:00"),
    }

