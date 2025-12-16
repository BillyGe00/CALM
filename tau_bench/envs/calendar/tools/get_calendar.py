"""Tool for getting calendar events."""

import json
from typing import Any, Dict, Optional
from envs.tool import Tool


class GetCalendar(Tool):
    """Get calendar events for a user."""
    
    @staticmethod
    def invoke(
        data: Dict[str, Any], 
        user_id: str, 
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Get calendar events for a user.
        
        Args:
            data: Environment data dictionary
            user_id: The user/persona ID
            date: Optional specific date (YYYY-MM-DD)
            start_date: Optional start of date range
            end_date: Optional end of date range
            
        Returns:
            JSON string with calendar events or error message
        """
        calendars = data.get("calendars", {})
        
        if user_id not in calendars:
            # Try to find by persona id
            user_calendar = calendars.get(user_id, {"events": []})
        else:
            user_calendar = calendars[user_id]
        
        events = user_calendar.get("events", [])
        
        # Filter by date if specified
        if date:
            events = [e for e in events if e.get("date") == date]
        elif start_date and end_date:
            events = [
                e for e in events 
                if start_date <= e.get("date", "") <= end_date
            ]
        
        return json.dumps({
            "user_id": user_id,
            "events": events,
            "count": len(events)
        }, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_calendar",
                "description": "Get calendar events for a user. Can filter by specific date or date range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user/persona ID (e.g., 'graduate_student')",
                        },
                        "date": {
                            "type": "string",
                            "description": "Optional specific date in YYYY-MM-DD format",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional start of date range in YYYY-MM-DD format",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional end of date range in YYYY-MM-DD format",
                        },
                    },
                    "required": ["user_id"],
                },
            },
        }

