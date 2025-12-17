"""Tool for adding calendar events."""

import json
import uuid
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


DAYS_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6
}

# Valid locations that can be checked against external_constraints
VALID_LOCATIONS = ["gym", "library", "cafeteria", "swimming_pool", "grocery_store"]


class AddEvent(Tool):
    """Add an event to a user's calendar."""
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        day_of_week: str,
        start_time: str,
        end_time: str,
        location: Optional[str] = None,
        is_flexible: Optional[bool] = True,
        priority: Optional[str] = "medium",
    ) -> str:
        """
        Add an event to the calendar.
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            day_of_week: Day of week (monday, tuesday, etc.)
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            location: Optional venue (gym, library, cafeteria, swimming_pool, grocery_store)
            is_flexible: Whether the event can be moved
            priority: Priority level ('low', 'medium', 'high')
            
        Returns:
            JSON string with created event or error message
        """
        # Validate time format
        try:
            start_h, start_m = map(int, start_time.split(":"))
            end_h, end_m = map(int, end_time.split(":"))
            if not (0 <= start_h < 24 and 0 <= start_m < 60):
                return json.dumps({"error": f"Invalid start_time: {start_time}"})
            if not (0 <= end_h < 24 and 0 <= end_m < 60):
                return json.dumps({"error": f"Invalid end_time: {end_time}"})
        except ValueError:
            return json.dumps({"error": "Time must be in HH:MM format"})
        
        # Validate day_of_week
        if not day_of_week or day_of_week.lower() not in DAYS_MAP:
            return json.dumps({"error": f"Invalid day_of_week: {day_of_week}"})
        
        # Initialize calendars if needed
        if "calendars" not in data:
            data["calendars"] = {}
        if user_id not in data["calendars"]:
            data["calendars"][user_id] = {"events": []}
        
        # Create the event
        event = {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "day_of_week": day_of_week.lower(),
            "start_time": start_time,
            "end_time": end_time,
            "priority": priority,
            "is_flexible": is_flexible,
        }
        
        # Add location if provided
        if location:
            event["location"] = location.lower()
        
        # Add to calendar
        data["calendars"][user_id]["events"].append(event)
        
        msg = f"Event added for {day_of_week} {start_time}-{end_time}"
        if location:
            msg += f" at {location}"
        
        return json.dumps({
            "success": True,
            "message": msg,
            "event": event
        }, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_event",
                "description": "Add a new event to a user's calendar for a specific day of week. Optionally specify a location (venue) for the event.",
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
                            "description": "Day of week for the event",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in HH:MM format (24-hour)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time in HH:MM format (24-hour)",
                        },
                        "location": {
                            "type": "string",
                            "enum": ["gym", "library", "cafeteria", "swimming_pool", "grocery_store"],
                            "description": "Optional venue for the event. Use get_venue_hours to check opening hours.",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Priority level of the event",
                        },
                        "is_flexible": {
                            "type": "boolean",
                            "description": "Whether the event can be moved/rescheduled",
                        },
                    },
                    "required": ["user_id", "day_of_week", "start_time", "end_time"],
                },
            },
        }
