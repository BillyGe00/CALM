from calm_bench.types import Task, Action

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
    Task(
        user_id="busy_person",
        instruction="List all calendar events for busy_person for today.",
        actions=[
            Action(
                name="get_calendar",
                kwargs={"user_id": "busy_person"}
            )
        ],
        outputs=[
            "Team Meeting from 09:00 to 10:00 at Conference Room A",
            "Project Deadline from 11:00 to 12:00 at Online",
            "Lunch with Client from 12:30 to 13:30 at Downtown Bistro",
            "Performance Review from 15:00 to 15:30 at Manager's Office"
        ],
    ),
    Task(
        user_id="busy_person",
        instruction="Find a free 1-hour slot for busy_person on Thursday and schedule a gym session.",
        actions=[
            Action(
                name="get_calendar",
                kwargs={"user_id": "busy_person"}
            ),
            Action(
                name="get_free_slots",
                kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 60}
            ),
            Action(
                name="add_event",
                kwargs={
                    "user_id": "busy_person",
                    "day_of_week": "thursday",
                    "start_time": "8:00",
                    "end_time": "9:00",
                    "location": "gym",
                    "priority": "medium",
                    "is_flexible": True
                }
            ),
            Action(
                name="get_calendar",
                kwargs={"user_id": "busy_person"}
            )
        ],
        outputs=[
            "08:00 to 09:00"
        ],
    ),
]
