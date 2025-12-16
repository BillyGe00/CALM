from tau_bench.types import Task, Action

TASKS_TEST = [
    Task(
        user_id="graduate_student",
        instruction="List all calendar events for Alex Chen (graduate_student) for today.",
        actions=[
            Action(
                name="get_calendar",
                kwargs={"user_id": "graduate_student"}
            )
        ],
        outputs=[],
    ),
]
