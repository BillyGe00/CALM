from calm_bench.types import Task, Action

TASKS_TRAIN = [
    Task(
        user_id="working_parent",
        instruction="Add a calendar event for Sarah Martinez (working_parent) on Tuesday from 20:00 to 21:00 at the library.",
        actions=[
            Action(
                name="add_event",
                kwargs={
                    "user_id": "working_parent",
                    "day_of_week": "tuesday",
                    "start_time": "20:00",
                    "end_time": "21:00",
                    "location": "library"
                }
            )
        ],
        outputs=[],
    ),
]
