"""Tool for finding free time slots in a user's schedule."""

import json
from typing import Any, Dict, List
from calm_bench.envs.tool import Tool


def time_to_minutes(t: str) -> int:
    """Convert HH:MM to minutes since midnight."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def minutes_to_time(m: int) -> str:
    """Convert minutes since midnight to HH:MM."""
    return f"{m // 60:02d}:{m % 60:02d}"


def parse_time_range(time_range: str) -> tuple:
    """Parse time range string like '10:00-12:00' into (start, end)."""
    parts = time_range.split("-")
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "00:00", "23:59"


class GetFreeSlots(Tool):
    """Find free time slots in a user's schedule."""
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        day_of_week: str,
        min_duration_minutes: int = 30
    ) -> str:
        """
        Find free time slots for a user on a specific day.
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            day_of_week: Day of week (e.g., "monday")
            min_duration_minutes: Minimum slot duration to return
            
        Returns:
            JSON string with free slots
        """
        day_lower = day_of_week.lower()
        
        # Get persona info
        personas = data.get("personas", {})
        if isinstance(personas, dict) and "personas" in personas:
            personas_list = personas["personas"]
        elif isinstance(personas, list):
            personas_list = personas
        else:
            personas_list = []
        
        persona = next((p for p in personas_list if p.get("id") == user_id), None)
        
        if not persona:
            return json.dumps({"error": f"Persona '{user_id}' not found"})
        
        wake_time = persona.get("wake_time", "07:00")
        sleep_time = persona.get("sleep_time", "23:00")
        
        # Collect all busy slots
        busy_slots: List[Dict] = []
        
        # From persona busy_blocks
        busy_blocks = persona.get("busy_blocks", [])
        
        for block in busy_blocks:
            days = [d.lower() for d in block.get("days", [])]
            if day_lower in days:
                time_range = block.get("time", "")
                start, end = parse_time_range(time_range)
                busy_slots.append({"start": start, "end": end})
        
        # From calendar events
        calendars = data.get("calendars", {})
        user_calendar = calendars.get(user_id, {})
        events = user_calendar.get("events", [])
        
        for event in events:
            event_day = event.get("day_of_week", "").lower()
            if event_day == day_lower:
                busy_slots.append({
                    "start": event.get("start_time", ""),
                    "end": event.get("end_time", "")
                })
        
        # Sort busy slots by start time
        busy_slots.sort(key=lambda x: time_to_minutes(x["start"]))
        
        # Find free slots
        free_slots: List[Dict] = []
        wake_minutes = time_to_minutes(wake_time)
        sleep_minutes = time_to_minutes(sleep_time)
        current_time = wake_minutes
        
        for slot in busy_slots:
            slot_start = time_to_minutes(slot["start"])
            slot_end = time_to_minutes(slot["end"])
            
            if slot_start > current_time:
                duration = slot_start - current_time
                if duration >= min_duration_minutes:
                    free_slots.append({
                        "start_time": minutes_to_time(current_time),
                        "end_time": minutes_to_time(slot_start),
                        "duration_minutes": duration
                    })
            
            current_time = max(current_time, slot_end)
        
        # Check for free time after last busy slot
        if current_time < sleep_minutes:
            duration = sleep_minutes - current_time
            if duration >= min_duration_minutes:
                free_slots.append({
                    "start_time": minutes_to_time(current_time),
                    "end_time": minutes_to_time(sleep_minutes),
                    "duration_minutes": duration
                })
        
        return json.dumps({
            "user_id": user_id,
            "day": day_of_week,
            "free_slots": free_slots,
            "wake_time": wake_time,
            "sleep_time": sleep_time,
            "min_duration_requested": min_duration_minutes
        }, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_free_slots",
                "description": "Find available free time slots in a user's schedule for a specific day. Considers both recurring commitments and scheduled events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user/persona ID",
                        },
                        "day_of_week": {
                            "type": "string",
                            "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                            "description": "Day of week to check",
                        },
                        "min_duration_minutes": {
                            "type": "integer",
                            "description": "Minimum duration of free slot to return (default: 30)",
                        },
                    },
                    "required": ["user_id", "day_of_week"],
                },
            },
        }
