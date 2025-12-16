"""Tool for removing calendar events."""

import json
from typing import Any, Dict
from envs.tool import Tool


class RemoveEvent(Tool):
    """Remove an event from a user's calendar."""
    
    @staticmethod
    def invoke(data: Dict[str, Any], user_id: str, event_id: str) -> str:
        """
        Remove an event from the calendar.
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            event_id: The ID of the event to remove
            
        Returns:
            JSON string with result or error message
        """
        calendars = data.get("calendars", {})
        
        if user_id not in calendars:
            return json.dumps({
                "error": f"No calendar found for user '{user_id}'"
            })
        
        events = calendars[user_id].get("events", [])
        
        # Find and remove the event
        for i, event in enumerate(events):
            if event.get("id") == event_id:
                removed_event = events.pop(i)
                return json.dumps({
                    "success": True,
                    "message": f"Event removed successfully",
                    "removed_event": removed_event
                }, indent=2)
        
        return json.dumps({
            "error": f"Event '{event_id}' not found in calendar"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_event",
                "description": "Remove an event from a user's calendar by event ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user/persona ID",
                        },
                        "event_id": {
                            "type": "string",
                            "description": "The ID of the event to remove",
                        },
                    },
                    "required": ["user_id", "event_id"],
                },
            },
        }
