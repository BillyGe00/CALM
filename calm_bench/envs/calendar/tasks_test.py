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
    # Additional diverse tests to increase coverage
    Task(
        user_id="professor_morning",
        instruction="Schedule a 30-minute student meeting on Thursday morning before the lecture.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "professor_morning", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "professor_morning",
                "day_of_week": "thursday",
                "start_time": "08:30",
                "end_time": "09:00",
                "location": "Office",
                "priority": "medium",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "professor_morning"})
        ],
        outputs=["08:30 to 09:00"],
    ),
    Task(
        user_id="professor_evening",
        instruction="Attempt to schedule a 60-minute guest talk at 18:30 on Thursday evening (conflicts with seminar).",
        actions=[
            Action(name="get_venue_hours", kwargs={"venue_id": "library", "day": "thursday"}),
            Action(name="get_free_slots", kwargs={"user_id": "professor_evening", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "professor_evening",
                "day_of_week": "thursday",
                "start_time": "18:30",
                "end_time": "19:30",
                "location": "Seminar Room",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "professor_evening"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="corporate_remote",
        instruction="Find a 90-minute deep-focus block for Dana during the afternoon and schedule it.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "corporate_remote", "day_of_week": "thursday", "min_duration_minutes": 90}),
            Action(name="add_event", kwargs={
                "user_id": "corporate_remote",
                "day_of_week": "thursday",
                "start_time": "15:00",
                "end_time": "16:30",
                "location": "Home Office",
                "priority": "medium",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "corporate_remote"})
        ],
        outputs=["15:00 to 16:30"],
    ),
    Task(
        user_id="corporate_onsite",
        instruction="Schedule a 60-minute client call at 10:30 on Thursday (should conflict with Team Sync).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "corporate_onsite",
                "day_of_week": "thursday",
                "start_time": "10:30",
                "end_time": "11:30",
                "location": "Conference Room B",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "corporate_onsite"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="pet_owner_dog",
        instruction="Book a 45-minute grooming slot for the dog on Thursday morning after the usual walk.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "pet_owner_dog", "day_of_week": "thursday", "min_duration_minutes": 45}),
            Action(name="add_event", kwargs={
                "user_id": "pet_owner_dog",
                "day_of_week": "thursday",
                "start_time": "09:15",
                "end_time": "10:00",
                "location": "Pet Groomers",
                "priority": "medium",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "pet_owner_dog"})
        ],
        outputs=["09:15 to 10:00"],
    ),
    Task(
        user_id="pet_owner_cat",
        instruction="Schedule a 30-minute check-in call at 08:00 on Thursday (should respect evening chronotype).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "pet_owner_cat", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "pet_owner_cat",
                "day_of_week": "thursday",
                "start_time": "08:00",
                "end_time": "08:30",
                "location": "Phone",
                "priority": "low",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "pet_owner_cat"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="writer_nightowl",
        instruction="Try to schedule a 60-minute morning draft session at 07:00 (chronotype mismatch expected).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "writer_nightowl", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "writer_nightowl",
                "day_of_week": "thursday",
                "start_time": "07:00",
                "end_time": "08:00",
                "location": "Home",
                "priority": "low",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "writer_nightowl"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="driver_day",
        instruction="Attempt to add a 30-minute personal errand at 08:30 (during day shift).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "driver_day", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "driver_day",
                "day_of_week": "thursday",
                "start_time": "08:30",
                "end_time": "09:00",
                "location": "Errand",
                "priority": "medium",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "driver_day"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="driver_night",
        instruction="Schedule a 30-minute check-in at 23:00 during the night shift (should conflict).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "driver_night", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "driver_night",
                "day_of_week": "thursday",
                "start_time": "23:00",
                "end_time": "23:30",
                "location": "Phone",
                "priority": "low",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "driver_night"})
        ],
        outputs=["cannot schedule"],
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
    Task(
        user_id="fully_booked",
        instruction=(
            "Attempt to schedule any 30-minute meeting for `fully_booked` on Thursday — the user is fully booked all day, so scheduling should be impossible."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "fully_booked"}),
            Action(name="get_free_slots", kwargs={"user_id": "fully_booked", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "fully_booked",
                "day_of_week": "thursday",
                "start_time": "14:00",
                "end_time": "14:30",
                "location": "office",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fully_booked"})
        ],
        outputs=[
            "cannot schedule",
        ],
    ),
    Task(
        user_id="busy_person",
        instruction=(
            "Intentionally attempt to schedule a 30-minute block during busy_person's sleep window (00:30-01:00 on Thursday)."
            " This should violate persona sleep constraints — expect the agent to refuse or report a conflict."
        ),
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "busy_person",
                "day_of_week": "thursday",
                "start_time": "00:30",
                "end_time": "01:00",
                "location": "home",
                "priority": "low",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"})
        ],
        outputs=[
            "cannot schedule",
        ],
    ),
    Task(
        user_id="busy_person",
        instruction=(
            "Attempt to schedule a 60-minute meeting at 10:30 on Thursday (during working hours 09:00-17:00)."
            " This should conflict with existing busy blocks — expect the agent to refuse or report a conflict."
        ),
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "busy_person",
                "day_of_week": "thursday",
                "start_time": "10:30",
                "end_time": "11:30",
                "location": "office",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"})
        ],
        outputs=[
            "cannot schedule",
        ],
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction=(
            "Try to schedule a 90-minute gym session at 02:00 on Monday when the gym is closed."
            " Expect the agent to check venue hours and refuse or propose an alternative."
        ),
        actions=[
            Action(name="get_venue_hours", kwargs={"venue_id": "gym", "day": "monday"}),
            Action(name="get_free_slots", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "min_duration_minutes": 90}),
            Action(name="add_event", kwargs={
                "user_id": "fitness_enthusiast",
                "day_of_week": "monday",
                "start_time": "02:00",
                "end_time": "03:30",
                "location": "gym",
                "priority": "medium",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fitness_enthusiast"})
        ],
        outputs=[
            "cannot schedule",
        ],
    ),
    Task(
        user_id="graduate_student",
        instruction="Try scheduling 10:30-11:00 on Thursday (conflicts with a busy block).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "graduate_student", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "graduate_student",
                "day_of_week": "thursday",
                "start_time": "10:30",
                "end_time": "11:00",
                "location": "library",
                "priority": "low",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "graduate_student"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="working_parent",
        instruction="Attempt a 30-minute meeting at 07:45 on Thursday (during commute/busy morning).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "working_parent",
                "day_of_week": "thursday",
                "start_time": "07:45",
                "end_time": "08:15",
                "location": "car",
                "priority": "medium",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "working_parent"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction="Try to schedule a 4-hour training block 09:00-13:00 on Monday (overlaps work).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "min_duration_minutes": 240}),
            Action(name="add_event", kwargs={
                "user_id": "fitness_enthusiast",
                "day_of_week": "monday",
                "start_time": "09:00",
                "end_time": "13:00",
                "location": "gym",
                "priority": "low",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fitness_enthusiast"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="busy_person",
        instruction="Schedule a late-evening flexible meeting 22:00-22:30 on Thursday (should succeed).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "busy_person",
                "day_of_week": "thursday",
                "start_time": "22:00",
                "end_time": "22:30",
                "location": "online",
                "priority": "low",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"})
        ],
        outputs=["22:00 to 22:30"],
    ),
    Task(
        user_id="fully_booked",
        instruction="Try another time for `fully_booked` (09:00-09:30) — still impossible.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "fully_booked", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={
                "user_id": "fully_booked",
                "day_of_week": "thursday",
                "start_time": "09:00",
                "end_time": "09:30",
                "location": "office",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fully_booked"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="working_parent",
        instruction="High-priority meeting requested at 10:00-11:00 on Thursday (during work hours) — expect conflict handling.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={
                "user_id": "working_parent",
                "day_of_week": "thursday",
                "start_time": "10:00",
                "end_time": "11:00",
                "location": "office",
                "priority": "high",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "working_parent"})
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="busy_person",
        instruction="Attempt 23:00-23:59 meeting on Thursday (late night slot; should succeed if free).",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "min_duration_minutes": 59}),
            Action(name="add_event", kwargs={
                "user_id": "busy_person",
                "day_of_week": "thursday",
                "start_time": "23:00",
                "end_time": "23:59",
                "location": "online",
                "priority": "low",
                "is_flexible": True
            }),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"})
        ],
        outputs=["23:00 to 23:59"],
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction="Try to schedule 06:00-07:30 on Monday (matches their early busy block) — expect cannot schedule.",
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "min_duration_minutes": 90}),
            Action(name="add_event", kwargs={
                "user_id": "fitness_enthusiast",
                "day_of_week": "monday",
                "start_time": "06:00",
                "end_time": "07:30",
                "location": "gym",
                "priority": "medium",
                "is_flexible": False
            }),
            Action(name="get_calendar", kwargs={"user_id": "fitness_enthusiast"})
        ],
        outputs=["cannot schedule"],
    ),
    # --- Appended challenging tests ---
    Task(
        user_id="corporate_onsite",
        instruction=(
            "Schedule two back-to-back meetings for corporate_onsite on Thursday: 09:30-10:00 in Building A, "
            "then 10:00-10:45 at Offsite Center. Include travel buffer; refuse if impossible."
        ),
        actions=[
            Action(name="get_venue_hours", kwargs={"venue_id": "Conference Room A", "day": "thursday"}),
            Action(name="get_venue_hours", kwargs={"venue_id": "Offsite Center", "day": "thursday"}),
            Action(name="get_free_slots", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "start_time": "09:30", "end_time": "10:00", "location": "Conference Room A", "priority": "high", "is_flexible": False}),
            Action(name="add_event", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "start_time": "10:00", "end_time": "10:45", "location": "Offsite Center", "priority": "high", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "corporate_onsite"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="working_parent",
        instruction=(
            "Schedule a 30-minute high-priority doctor appointment at 14:00 on Thursday; if a low-priority meal-prep occupies that slot, reschedule it rather than canceling."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "working_parent"}),
            Action(name="get_free_slots", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "start_time": "14:00", "end_time": "14:30", "location": "Clinic", "priority": "high", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "working_parent"}),
        ],
        outputs=["14:00 to 14:30"],
    ),
    Task(
        user_id="corporate_remote",
        instruction=(
            "Schedule a 30-minute sync at 09:00 for Dana in EST while Dana's calendar is stored in PST — ensure correct timezone conversion and avoid conflicts."
        ),
        actions=[
            Action(name="get_persona", kwargs={"user_id": "corporate_remote"}),
            Action(name="get_calendar", kwargs={"user_id": "corporate_remote"}),
            Action(name="get_free_slots", kwargs={"user_id": "corporate_remote", "day_of_week": "thursday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={"user_id": "corporate_remote", "day_of_week": "thursday", "start_time": "09:00", "end_time": "09:30", "location": "Video Call", "priority": "medium", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "corporate_remote"}),
        ],
        outputs=["09:00 to 09:30"],
    ),
    Task(
        user_id="graduate_student",
        instruction=(
            "Create a weekly recurring 1-hour reading group on Thursdays at 17:00 for 4 weeks, avoiding conflicts with existing classes."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "graduate_student"}),
            Action(name="get_free_slots", kwargs={"user_id": "graduate_student", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={"user_id": "graduate_student", "day_of_week": "thursday", "start_time": "17:00", "end_time": "18:00", "location": "Seminar Room", "priority": "low", "is_flexible": True, "recurrence": {"freq": "weekly", "count": 4}}),
            Action(name="get_calendar", kwargs={"user_id": "graduate_student"}),
        ],
        outputs=["17:00 to 18:00 (recurs 4 times)"],
    ),
    Task(
        user_id="driver_day",
        instruction=(
            "Attempt to schedule an event at 02:30 on the day of a daylight savings forward shift (non-existent time)."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "driver_day"}),
            Action(name="get_free_slots", kwargs={"user_id": "driver_day", "day_of_week": "sunday", "min_duration_minutes": 30}),
            Action(name="add_event", kwargs={"user_id": "driver_day", "day_of_week": "sunday", "start_time": "02:30", "end_time": "03:00", "location": "Home", "priority": "low", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "driver_day"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="fully_booked",
        instruction=(
            "Attempt to add an all-day event on Thursday; verify the agent refuses if calendar is already full of all-day reservations."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "fully_booked"}),
            Action(name="add_event", kwargs={"user_id": "fully_booked", "day_of_week": "thursday", "start_time": "00:00", "end_time": "23:59", "location": "Conference", "priority": "high", "is_flexible": False, "all_day": True}),
            Action(name="get_calendar", kwargs={"user_id": "fully_booked"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="busy_person",
        instruction=(
            "Schedule a 20-minute follow-up that must occur after an existing 30-minute meeting; the agent must chain events so the follow-up starts after the first meeting ends."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "busy_person"}),
            Action(name="add_event", kwargs={"user_id": "busy_person", "day_of_week": "thursday", "start_time": "11:00", "end_time": "11:20", "location": "Phone", "priority": "medium", "is_flexible": True}),
            Action(name="get_calendar", kwargs={"user_id": "busy_person"}),
        ],
        outputs=["11:00 to 11:20"],
    ),
    Task(
        user_id="corporate_onsite",
        instruction=(
            "Schedule three short 20-minute checkpoints between 09:00 and 12:00 with at least 15 minutes buffer between them; tests multi-event batching and buffer enforcement."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "corporate_onsite"}),
            Action(name="get_free_slots", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "min_duration_minutes": 20}),
            Action(name="add_event", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "start_time": "09:00", "end_time": "09:20", "location": "Huddle Room", "priority": "low", "is_flexible": True}),
            Action(name="add_event", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "start_time": "09:35", "end_time": "09:55", "location": "Huddle Room", "priority": "low", "is_flexible": True}),
            Action(name="add_event", kwargs={"user_id": "corporate_onsite", "day_of_week": "thursday", "start_time": "10:10", "end_time": "10:30", "location": "Huddle Room", "priority": "low", "is_flexible": True}),
            Action(name="get_calendar", kwargs={"user_id": "corporate_onsite"}),
        ],
        outputs=["09:00 to 09:20, 09:35 to 09:55, 10:10 to 10:30"],
    ),
    Task(
        user_id="fitness_enthusiast",
        instruction=(
            "Request a long 8-hour focus block but only 6 continuous hours are free; the agent should propose alternatives rather than incorrectly scheduling beyond availability."
        ),
        actions=[
            Action(name="get_free_slots", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "min_duration_minutes": 480}),
            Action(name="add_event", kwargs={"user_id": "fitness_enthusiast", "day_of_week": "monday", "start_time": "08:00", "end_time": "16:00", "location": "Home", "priority": "medium", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "fitness_enthusiast"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="working_parent",
        instruction=(
            "Two high-priority meetings requested at the same time for working_parent; the agent must not schedule both and should ask for clarification or prioritize correctly."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "working_parent"}),
            Action(name="get_free_slots", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "min_duration_minutes": 60}),
            Action(name="add_event", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "start_time": "10:00", "end_time": "11:00", "location": "Office", "priority": "high", "is_flexible": False}),
            Action(name="add_event", kwargs={"user_id": "working_parent", "day_of_week": "thursday", "start_time": "10:00", "end_time": "11:00", "location": "School", "priority": "high", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "working_parent"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="pet_owner_dog",
        instruction=(
            "Request a long 10-hour volunteer shift that would span midnight; the agent should not schedule across the user's sleep boundary and should propose splitting or refuse."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "pet_owner_dog"}),
            Action(name="get_free_slots", kwargs={"user_id": "pet_owner_dog", "day_of_week": "thursday", "min_duration_minutes": 600}),
            Action(name="add_event", kwargs={"user_id": "pet_owner_dog", "day_of_week": "thursday", "start_time": "18:00", "end_time": "04:00", "location": "Shelter", "priority": "medium", "is_flexible": False}),
            Action(name="get_calendar", kwargs={"user_id": "pet_owner_dog"}),
        ],
        outputs=["cannot schedule"],
    ),
    Task(
        user_id="writer_nightowl",
        instruction=(
            "Schedule a 90-minute late-night session that starts at 23:30 and ends after midnight; ensure it respects the persona's sleep window and does not violate constraints."
        ),
        actions=[
            Action(name="get_calendar", kwargs={"user_id": "writer_nightowl"}),
            Action(name="get_free_slots", kwargs={"user_id": "writer_nightowl", "day_of_week": "thursday", "min_duration_minutes": 90}),
            Action(name="add_event", kwargs={"user_id": "writer_nightowl", "day_of_week": "thursday", "start_time": "23:30", "end_time": "01:00", "location": "Home", "priority": "medium", "is_flexible": True}),
            Action(name="get_calendar", kwargs={"user_id": "writer_nightowl"}),
        ],
        outputs=["23:30 to 01:00"],
    ),
]
