"""Tool for updating calendar events."""

import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateEvent(Tool):
    """Update an existing event in a user's calendar."""
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        event_id: str,
        title: Optional[str] = None,
        date: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        is_flexible: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Update an existing event.
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            event_id: The ID of the event to update
            title: New title (optional)
            date: New date (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            category: New category (optional)
            priority: New priority (optional)
            is_flexible: New flexibility status (optional)
            notes: New notes (optional)
            
        Returns:
            JSON string with updated event or error message
        """
        calendars = data.get("calendars", {})
        
        if user_id not in calendars:
            return json.dumps({
                "error": f"No calendar found for user '{user_id}'"
            })
        
        events = calendars[user_id].get("events", [])
        
        # Find the event
        for event in events:
            if event.get("id") == event_id:
                # Update fields if provided
                if title is not None:
                    event["title"] = title
                if date is not None:
                    event["date"] = date
                if start_time is not None:
                    event["start_time"] = start_time
                if end_time is not None:
                    event["end_time"] = end_time
                if category is not None:
                    event["category"] = category
                if priority is not None:
                    event["priority"] = priority
                if is_flexible is not None:
                    event["is_flexible"] = is_flexible
                if notes is not None:
                    event["notes"] = notes
                
                return json.dumps({
                    "success": True,
                    "message": f"Event '{event.get('title')}' updated successfully",
                    "event": event
                }, indent=2)
        
        return json.dumps({
            "error": f"Event '{event_id}' not found in calendar"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_event",
                "description": "Update an existing event in a user's calendar. Only provided fields will be updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user/persona ID",
                        },
                        "event_id": {
                            "type": "string",
                            "description": "The ID of the event to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the event",
                        },
                        "date": {
                            "type": "string",
                            "description": "New date in YYYY-MM-DD format",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "New start time in HH:MM format (24-hour)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "New end time in HH:MM format (24-hour)",
                        },
                        "category": {
                            "type": "string",
                            "description": "New event category",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "New priority level",
                        },
                        "is_flexible": {
                            "type": "boolean",
                            "description": "Whether the event can be moved/rescheduled",
                        },
                        "notes": {
                            "type": "string",
                            "description": "New notes for the event",
                        },
                    },
                    "required": ["user_id", "event_id"],
                },
            },
        }

