Calendar test catalog
=====================

This file documents the tests defined in `tasks_test.py` for the calendar environment.
Indices below are zero-based and correspond to positions in `TASKS_TEST`.

0. graduate_student — list today's events
1. busy_person — list today's events
2. busy_person — find 1-hour slot on Thursday and schedule gym (08:00-09:00)
3. graduate_student — find 30-min slot before 10am (09:00-09:30)
4. working_parent — schedule meal-prep (20:00-21:00)
5. fitness_enthusiast — schedule workout (07:30-08:30)
6. busy_person — art class at 14:00 (expect cannot schedule due to conflict/buffer)
7. fully_booked — fully blocked day attempt (expect cannot schedule)
8. busy_person — attempt sleep-window 00:30-01:00 (expect cannot schedule/refusal)
9. busy_person — conflict during work hours 10:30-11:30 (expect cannot schedule)
10. fitness_enthusiast — gym outside-hours 02:00-03:30 (expect cannot schedule)
11. graduate_student — try 10:30-11:00 during busy block (expect cannot schedule)
12. working_parent — 07:45-08:15 during commute (expect cannot schedule)
13. fitness_enthusiast — 4-hour training 09:00-13:00 (expect cannot schedule)
14. busy_person — late-evening flexible meeting 22:00-22:30 (expected to succeed)
15. fully_booked — another attempt 09:00-09:30 (expect cannot schedule)
16. working_parent — high-priority 10:00-11:00 (expect conflict handling)
17. busy_person — late slot 23:00-23:59 (expected to succeed)
18. fitness_enthusiast — early busy block 06:00-07:30 (expect cannot schedule)
19. professor_morning — 30-minute student meeting (morning slot)
20. professor_evening — evening seminar / guest talk (venue/conflict check)
21. pet_owner_dog — grooming appointment after dog walk
22. pet_owner_cat — vet follow-up (afternoon)
23. writer_nightowl — morning scheduling attempt (chronotype mismatch)
24. corporate_remote — schedule all-hands at 09:00 (timezone/remote check)
25. corporate_onsite — on-site meeting with room booking (venue-hours)
26. driver_day — schedule driving shift at 07:00 (conflict with commute)
27. driver_night — schedule night shift at 22:30 (should be allowed for night driver)
28. fully_booked_variant — half-day fully booked attempt (expect cannot schedule)

Notes:
- "cannot schedule" indicates the test expects the agent to refuse or report a conflict; depending on agent behavior, the evaluator will record reward components accordingly.
- Tests mix venue checks, persona/chronotype constraints, busy blocks, fully-booked calendars, and priority/flexibility flags.
- Adjust `personas.json` and `calendars.json` if you want different constraints (e.g., different sleep/wake times or venue hours).

Sample task index usage:

Run the developer test-runner for a single task index to inspect per-dimension reward details:

```bash
PYTHONPATH=. python tools/run_all_tests.py --task_id 19 --model_provider openai --model gpt-4o
```

Replace `--task_id` with any index above to target that scenario.
