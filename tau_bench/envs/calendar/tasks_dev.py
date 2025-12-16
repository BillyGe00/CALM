from tau_bench.types import Task, Action

TASKS_DEV = [
    Task(
        user_id="fitness_enthusiast",
        instruction="Get persona information for Mike Johnson (fitness_enthusiast).",
        actions=[
            Action(
                name="get_persona",
                kwargs={"persona_id": "fitness_enthusiast"}
            )
        ],
        outputs=[],
    ),
]
