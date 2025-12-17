"""Tool for getting busy time slots for a user on a specific day."""

import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


def parse_time_range(time_range: str) -> tuple:
    """Parse time range string like '10:00-12:00' into (start, end)."""
    parts = time_range.split("-")
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "00:00", "23:59"


class GetBusySlots(Tool):
    """Get all busy time slots for a user on a specific day."""
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        day_of_week: str
    ) -> str:
        """
        Get busy time slots for a user on a specific day of week.
        
        Combines:
        - Recurring busy blocks from persona
        - One-time events from calendar
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            day_of_week: Day of week (e.g., "monday", "tuesday")
            
        Returns:
            JSON string with busy slots
        """
        busy_slots: List[Dict] = []
        day_lower = day_of_week.lower()
        
        # Get persona's recurring busy blocks
        personas = data.get("personas", {})
        
        # Handle both dict and list formats
        if isinstance(personas, dict) and "personas" in personas:
            personas_list = personas["personas"]
        elif isinstance(personas, list):
            personas_list = personas
        else:
            personas_list = []
        
        persona = next((p for p in personas_list if p.get("id") == user_id), None)
        
        if persona:
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
        
        # Get one-time events from calendar
        calendars = data.get("calendars", {})
        user_calendar = calendars.get(user_id, {})
        events = user_calendar.get("events", [])
        
        for event in events:
            event_day = event.get("day_of_week", "").lower()
            if event_day == day_lower:
                busy_slots.append({
                    "start_time": event.get("start_time", ""),
                    "end_time": event.get("end_time", ""),
                    "type": "event"
                })
        
        # Sort by start time
        busy_slots.sort(key=lambda x: x.get("start_time", ""))
        
        # Get persona's wake/sleep times for context
        wake_time = persona.get("wake_time", "07:00") if persona else "07:00"
        sleep_time = persona.get("sleep_time", "23:00") if persona else "23:00"
        
        return json.dumps({
            "user_id": user_id,
            "day": day_of_week,
            "busy_slots": busy_slots,
            "wake_time": wake_time,
            "sleep_time": sleep_time,
            "available_hours": f"{wake_time} to {sleep_time}"
        }, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_busy_slots",
                "description": "Get all busy time slots for a user on a specific day of week. Returns both recurring commitments and scheduled events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user/persona ID (e.g., 'graduate_student')",
                        },
                        "day_of_week": {
                            "type": "string",
                            "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                            "description": "Day of week to check",
                        },
                    },
                    "required": ["user_id", "day_of_week"],
                },
            },
        }
