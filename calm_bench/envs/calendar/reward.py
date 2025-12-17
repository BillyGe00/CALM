"""
Reward calculation helpers for calendar scheduling evaluation.

Based on the proposal success criteria:
1. Constraint Satisfaction - No time conflicts, required events scheduled
2. Persona Alignment - Schedule reflects persona preferences
3. Balance Index - Work/rest/personal activity distribution
4. Re-Planning Robustness - Minimal disruption under perturbations
5. External Feasibility - Activities within venue operating hours
"""

from typing import Dict, List, Any, Optional


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM time string to minutes since midnight."""
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except (ValueError, AttributeError):
        return 0


def minutes_to_time(m: int) -> str:
    """Convert minutes since midnight to HH:MM."""
    return f"{m // 60:02d}:{m % 60:02d}"


def event_duration_minutes(event: Dict) -> int:
    """Calculate event duration in minutes."""
    start = time_to_minutes(event.get("start_time", "00:00"))
    end = time_to_minutes(event.get("end_time", "00:00"))
    return max(0, end - start)


def parse_time_range(time_range: str) -> tuple:
    """Parse time range string like '10:00-12:00' into (start, end)."""
    parts = time_range.split("-")
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "00:00", "23:59"


def get_all_busy_slots(
    persona: Dict,
    calendar_events: List[Dict],
    day_of_week: str
) -> List[Dict]:
    """
    Get all busy slots for a day, combining recurring and one-time events.
    
    Args:
        persona: Persona with constraints
        calendar_events: Events from calendar
        day_of_week: Day to check
    
    Returns:
        List of busy slots with start_time and end_time
    """
    busy_slots = []
    day_lower = day_of_week.lower()
    
    # Add recurring busy blocks from persona
    busy_blocks = persona.get("busy_blocks", [])
    
    for block in busy_blocks:
        days = [d.lower() for d in block.get("days", [])]
        if day_lower in days:
            time_range = block.get("time", "")
            start, end = parse_time_range(time_range)
            busy_slots.append({
                "start_time": start,
                "end_time": end,
                "type": "recurring"
            })
    
    # Add calendar events
    for event in calendar_events:
        event_day = event.get("day_of_week", "").lower()
        if event_day == day_lower:
            busy_slots.append({
                "start_time": event.get("start_time", ""),
                "end_time": event.get("end_time", ""),
                "type": "event"
            })
    
    return busy_slots


def has_time_conflicts(busy_slots: List[Dict]) -> bool:
    """
    Check if any busy slots have overlapping time.
    
    Returns:
        True if conflicts exist, False otherwise
    """
    if len(busy_slots) < 2:
        return False
    
    # Sort by start time
    sorted_slots = sorted(
        busy_slots,
        key=lambda e: time_to_minutes(e.get("start_time", "00:00"))
    )
    
    for i in range(len(sorted_slots) - 1):
        current_end = time_to_minutes(sorted_slots[i].get("end_time", "00:00"))
        next_start = time_to_minutes(sorted_slots[i + 1].get("start_time", "00:00"))
        if current_end > next_start:
            return True
    
    return False


def get_conflicts(busy_slots: List[Dict]) -> List[tuple]:
    """
    Find all conflicting slot pairs.
    
    Returns:
        List of (slot1, slot2) tuples that conflict
    """
    conflicts = []
    sorted_slots = sorted(
        busy_slots,
        key=lambda e: time_to_minutes(e.get("start_time", "00:00"))
    )
    
    for i in range(len(sorted_slots) - 1):
        current_end = time_to_minutes(sorted_slots[i].get("end_time", "00:00"))
        next_start = time_to_minutes(sorted_slots[i + 1].get("start_time", "00:00"))
        if current_end > next_start:
            conflicts.append((sorted_slots[i], sorted_slots[i + 1]))
    
    return conflicts


def check_constraint_satisfaction(
    all_busy_slots: List[Dict],
    persona: Dict
) -> tuple[float, Dict]:
    """
    Check hard constraint satisfaction.
    
    Checks:
    - No time conflicts between all busy slots
    - Events respect sleep hours
    
    Returns:
        (score, details) where score is 0.0-1.0
    """
    score = 1.0
    details = {"conflicts": [], "sleep_violations": []}
    
    # Check for time conflicts
    conflicts = get_conflicts(all_busy_slots)
    if conflicts:
        # Deduct based on number of conflicts
        score -= min(0.5, len(conflicts) * 0.25)
        details["conflicts"] = [
            f"Conflict: {c[0].get('start_time')}-{c[0].get('end_time')} "
            f"overlaps with {c[1].get('start_time')}-{c[1].get('end_time')}"
            for c in conflicts
        ]
    
    # Check sleep hour violations (only for newly added events)
    sleep_time = persona.get("sleep_time", "23:00")
    wake_time = persona.get("wake_time", "07:00")
    
    sleep_minutes = time_to_minutes(sleep_time)
    wake_minutes = time_to_minutes(wake_time)
    
    for slot in all_busy_slots:
        if slot.get("type") != "event":
            continue  # Only check newly added events
        
        event_start = time_to_minutes(slot.get("start_time", "00:00"))
        
        # Check if event is during sleep hours
        # Sleep period can be:
        # - Same day: sleep_time < wake_time (e.g., 01:00-08:00 for night owl)
        # - Cross midnight: sleep_time > wake_time (e.g., 22:00-06:00 for early bird)
        is_during_sleep = False
        if sleep_minutes < wake_minutes:
            # Sleep period is within the same day (e.g., 01:00-08:00)
            # Event violates if it starts during sleep period
            is_during_sleep = sleep_minutes <= event_start < wake_minutes
        else:
            # Sleep period crosses midnight (e.g., 22:00-06:00)
            # Event violates if it starts after sleep_time OR before wake_time
            is_during_sleep = event_start >= sleep_minutes or event_start < wake_minutes
        
        if is_during_sleep:
            score -= 0.2
            details["sleep_violations"].append(
                f"Event at {slot.get('start_time')} is during sleep hours ({sleep_time}-{wake_time})"
            )
    
    return max(0.0, score), details


def check_persona_alignment(
    new_events: List[Dict],
    persona: Dict
) -> tuple[float, Dict]:
    """
    Check if newly added events align with persona preferences.
    
    Checks:
    - Chronotype alignment (morning/evening person)
    - Sleep time boundaries
    
    Returns:
        (score, details) where score is 0.0-1.0
    """
    if not new_events:
        return 1.0, {"note": "No new events to check"}
    
    score = 1.0
    details = {"chronotype_issues": []}
    
    chronotype = persona.get("chronotype", "flexible")
    sleep_time = persona.get("sleep_time", "23:00")
    
    for event in new_events:
        event_start = time_to_minutes(event.get("start_time", "00:00"))
        
        # Check chronotype alignment
        if chronotype == "morning_person":
            # Morning people prefer activities before evening
            if event_start >= time_to_minutes("21:00"):
                score -= 0.15
                details["chronotype_issues"].append(
                    f"Event at {event.get('start_time')} is late for a morning person"
                )
        elif chronotype == "evening_person":
            # Evening people don't like early mornings
            if event_start < time_to_minutes("09:00"):
                score -= 0.15
                details["chronotype_issues"].append(
                    f"Event at {event.get('start_time')} is early for an evening person"
                )
    
    return max(0.0, score), details


def check_replanning_robustness(
    original_events: List[Dict],
    new_events: List[Dict]
) -> tuple[float, Dict]:
    """
    Check re-planning robustness under perturbations.
    
    Measures how minimally disruptive the changes are.
    
    Returns:
        (score, details) where score is 0.0-1.0
    """
    if not original_events:
        return 1.0, {"edit_distance": 0, "original_count": 0}
    
    original_ids = {e.get("id") for e in original_events if e.get("id")}
    new_ids = {e.get("id") for e in new_events if e.get("id")}
    
    added = len(new_ids - original_ids)
    removed = len(original_ids - new_ids)
    
    # Check for modified events
    modified_count = 0
    original_by_id = {e.get("id"): e for e in original_events if e.get("id")}
    for event in new_events:
        eid = event.get("id")
        if eid and eid in original_by_id:
            orig = original_by_id[eid]
            if (event.get("start_time") != orig.get("start_time") or
                event.get("end_time") != orig.get("end_time") or
                event.get("day_of_week") != orig.get("day_of_week")):
                modified_count += 1
    
    edit_distance = added + removed + modified_count
    
    # Score decreases with more changes
    max_changes = max(len(original_events), 1)
    score = max(0.0, 1.0 - (edit_distance / max_changes) * 0.5)
    
    return score, {
        "edit_distance": edit_distance,
        "added": added,
        "removed": removed,
        "modified": modified_count,
        "original_count": len(original_events),
        "new_count": len(new_events)
    }


def check_external_feasibility(
    new_events: List[Dict],
    venues: Dict,
    day_of_week: str = "monday"
) -> tuple[float, Dict]:
    """
    Check if events are feasible given external constraints (venue hours).
    
    Returns:
        (score, details) where score is 0.0-1.0
    """
    if not new_events:
        return 1.0, {"note": "No events with venue to check"}
    
    score = 1.0
    details = {"venue_violations": []}
    
    for event in new_events:
        location = event.get("location")
        if not location:
            continue
        
        venue = venues.get(location)
        if not venue:
            continue
        
        hours = venue.get("hours", {}).get(day_of_week.lower(), {})
        if not hours:
            continue
        
        venue_open = time_to_minutes(hours.get("open", "00:00"))
        venue_close = time_to_minutes(hours.get("close", "24:00"))
        
        event_start = time_to_minutes(event.get("start_time", "00:00"))
        event_end = time_to_minutes(event.get("end_time", "00:00"))
        
        if event_start < venue_open or event_end > venue_close:
            score -= 0.25
            details["venue_violations"].append({
                "venue": location,
                "event_time": f"{event.get('start_time')}-{event.get('end_time')}",
                "venue_hours": f"{hours.get('open')}-{hours.get('close')}"
            })
    
    return max(0.0, score), details


def calculate_calendar_reward(
    persona: Dict,
    calendar_events: List[Dict],
    external_constraints: Dict,
    day_of_week: str = "monday",
    original_events: Optional[List[Dict]] = None,
    weights: Optional[Dict[str, float]] = None
) -> tuple[float, Dict]:
    """
    Calculate the overall reward for a calendar scheduling result.
    
    Args:
        persona: User persona with preferences and constraints
        calendar_events: Events from the calendar (agent-added)
        external_constraints: Venue hours and other external data
        day_of_week: Day of week for evaluation
        original_events: Original events (for perturbation scenarios)
        weights: Custom weights for each dimension
    
    Returns:
        (total_reward, detailed_scores)
    """
    if weights is None:
        weights = {
            "constraint_satisfaction": 0.35,
            "persona_alignment": 0.30,
            "replanning_robustness": 0.20,
            "external_feasibility": 0.15,
        }
    
    # Get all busy slots (recurring + new events)
    all_busy_slots = get_all_busy_slots(persona, calendar_events, day_of_week)
    
    # Filter to just the newly added events
    new_events = [e for e in calendar_events if e.get("day_of_week", "").lower() == day_of_week.lower()]
    
    scores = {}
    details = {}
    
    # 1. Constraint Satisfaction
    cs_score, cs_details = check_constraint_satisfaction(all_busy_slots, persona)
    scores["constraint_satisfaction"] = cs_score
    details["constraint_satisfaction"] = cs_details
    
    # 2. Persona Alignment
    pa_score, pa_details = check_persona_alignment(new_events, persona)
    scores["persona_alignment"] = pa_score
    details["persona_alignment"] = pa_details
    
    # 3. Re-Planning Robustness
    if original_events is not None:
        rr_score, rr_details = check_replanning_robustness(original_events, calendar_events)
    else:
        rr_score, rr_details = 1.0, {"note": "No perturbation scenario"}
    scores["replanning_robustness"] = rr_score
    details["replanning_robustness"] = rr_details
    
    # 4. External Feasibility
    venues = external_constraints.get("venues", {})
    ef_score, ef_details = check_external_feasibility(new_events, venues, day_of_week)
    scores["external_feasibility"] = ef_score
    details["external_feasibility"] = ef_details
    
    # Calculate weighted total
    total_reward = sum(scores[k] * weights[k] for k in weights)
    
    return total_reward, {
        "scores": scores,
        "weights": weights,
        "details": details,
        "all_busy_slots": len(all_busy_slots),
        "new_events": len(new_events)
    }
