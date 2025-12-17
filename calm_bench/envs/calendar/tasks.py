"""Test tasks for calendar domain evaluation."""

from typing import List, Optional
from calm_bench.types import Task, Action
from calm_bench.envs.calendar.task_generator import generate_task, generate_task_batch


# ============================================================================
# Predefined Tasks (for specific test scenarios)
# ============================================================================

TASKS_PREDEFINED = [
    Task(
        user_id="graduate_student",
        instruction="""You are helping Alex Chen, a PhD Student in Computer Science. Their priorities are: research, coursework, fitness. On Monday they want to fit in a 60-minute workout. They already have daytime commitments, so please find a time that doesn't clash with anything else and isn't too late at night.""",
        actions=[],  # No predefined actions - use rule-based evaluation
        outputs=[]
    ),
    Task(
        user_id="working_parent",
        instruction="""You are helping Sarah Martinez, a Marketing Manager and Mother of Two. Their priorities are: family, work, health. On Tuesday they need a 45-minute video call slot in the evening. Any time after 8 pm is okay, as long as it doesn't end too close to their usual bedtime (10:30 pm).""",
        actions=[],
        outputs=[]
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction="""You are helping Mike Johnson, a Software Engineer and Gym Trainer. Their priorities are: fitness, work, meal_prep. On Wednesday they want to add a 30-minute meal prep session. Please schedule it after their main daytime commitments, but not starting later than 8 pm since they sleep early.""",
        actions=[],
        outputs=[]
    ),
]


# ============================================================================
# Task Generation Functions
# ============================================================================

def get_tasks(
    split: str = "test",
    count: Optional[int] = None,
    seed: Optional[int] = None,
    include_perturbations: bool = False
) -> List[Task]:
    """
    Get tasks for evaluation.
    
    Args:
        split: Task split type
            - "test": Full test set (generated tasks)
            - "dev": Small dev set (predefined tasks)
            - "predefined": Only predefined tasks
            - "random": Generate random tasks
        count: Number of tasks (for "test" and "random" splits)
        seed: Random seed for reproducibility
        include_perturbations: Include perturbation scenarios
    
    Returns:
        List of Task instances
    """
    if split == "predefined":
        return TASKS_PREDEFINED
    
    elif split == "dev":
        # Small set for development
        return TASKS_PREDEFINED[:2]
    
    elif split == "test":
        # Generate test tasks + predefined
        task_count = count or 10
        generated = generate_task_batch(
            count=task_count,
            include_perturbations=include_perturbations,
            seed=seed
        )
        return TASKS_PREDEFINED + generated
    
    elif split == "random":
        # Pure random generation
        task_count = count or 20
        return generate_task_batch(
            count=task_count,
            include_perturbations=include_perturbations,
            seed=seed
        )
    
    else:
        raise ValueError(f"Unknown task split: {split}. Available: predefined, dev, test, random")


def get_single_task(
    persona_id: Optional[str] = None,
    request_id: Optional[str] = None,
    day_of_week: Optional[str] = None,
    include_perturbation: bool = False,
    seed: Optional[int] = None
) -> Task:
    """
    Generate a single task with specific parameters.
    
    Useful for targeted testing.
    """
    return generate_task(
        persona_id=persona_id,
        request_id=request_id,
        day_of_week=day_of_week,
        include_perturbation=include_perturbation,
        seed=seed
    )
