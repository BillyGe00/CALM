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
    Task(
        user_id="graduate_student",
        instruction="Find a free 30-minute slot for graduate_student on Thursday before 10am and schedule a journaling block.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "graduate_student", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "graduate_student",
                "day_of_week": "thursday",
                "start_time": "09:00",
                "end_time": "09:30",
                "location": "library",
                "priority": "low",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "graduate_student"})
        ],
        outputs=[
            "09:00 to 09:30"
        ],
    ),
    Task(
        user_id="working_parent",
        instruction="Schedule a 60-minute meal-prep block for working_parent on Thursday evening after work.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "working_parent",
                "day_of_week": "thursday",
                "start_time": "20:00",
                "end_time": "21:00",
                "location": "home",
                "priority": "medium",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "working_parent"})
        ],
        outputs=[
            "20:00 to 21:00"
        ],
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction="Find a 60-minute slot for fitness_enthusiast on Monday morning and schedule a workout at the gym.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "fitness_enthusiast",
                "day_of_week": "monday",
                "start_time": "07:30",
                "end_time": "08:30",
                "location": "gym",
                "priority": "medium",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fitness_enthusiast"})
        ],
        outputs=[
            "07:30 to 08:30"
        ],
    ),
    Task(
        user_id="busy_person",
        instruction=(
            "An art class is offered only at 14:00 at the library."
            " Your job: check venue hours and availability and schedule it only if it does not conflict with existing commitments."
            " Include a 15-minute buffer when considering travel between locations; if the class conflicts with work or can't be scheduled, explicitly say you cannot schedule it."
        ),
        actions=[
            Action(name="get_venue_hours", kwargs={"venue_id": "library", "day": "thursday"}),
            Action(name="get_free_slots", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"})
        ],
        outputs=[
            "cannot schedule",
        ],
    ),
]
