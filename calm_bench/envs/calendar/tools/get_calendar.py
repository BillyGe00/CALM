"""Tool for getting calendar events."""

import json
from typing import Any, Dict, Optional
from calm_bench.envs.tool import Tool


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
            return json.dumps({
                "error": f"No calendar found for user_id '{user_id}'",
                "user_id": user_id,
                "events": [],
                "count": 0
            }, indent=2)
        
        user_calendar = calendars[user_id]
        events = user_calendar.get("events", [])
        
        # Filter by date if specified
        if date:
            def event_matches_date(e):
                # Prefer explicit 'date' field, else extract from 'start'
                if "date" in e:
                    return e["date"] == date
                if "start" in e and isinstance(e["start"], str) and len(e["start"]) >= 10:
                    return e["start"].split("T")[0] == date
                return False
            events = [e for e in events if event_matches_date(e)]
        elif start_date and end_date:
            def event_in_range(e):
                # Prefer explicit 'date' field, else extract from 'start'
                if "date" in e:
                    d = e["date"]
                elif "start" in e and isinstance(e["start"], str) and len(e["start"]) >= 10:
                    d = e["start"].split("T")[0]
                else:
                    return False
                return start_date <= d <= end_date
            events = [e for e in events if event_in_range(e)]
        
        # Format a user-friendly summary if events are found
        if events:
            event_lines = []
            for idx, e in enumerate(events, 1):
                title = e.get("title", "(No Title)")
                start = e.get("start", "?")
                end = e.get("end", "?")
                # Extract just the time portion, drop seconds
                start_time = start.split("T")[1][:5] if "T" in start else start[:5]
                end_time = end.split("T")[1][:5] if "T" in end else end[:5]
                location = e.get("location", "(No Location)")
                event_lines.append(f"{idx}. **{title}**\n   - Time: {start_time} - {end_time}\n   - Location: {location}")
            summary = f"Here is the list of today's events for {user_id}:\n\n" + "\n\n".join(event_lines)
        else:
            summary = f"No events found for {user_id} on this date."
        return json.dumps({
            "user_id": user_id,
            "events": events,
            "count": len(events),
            "summary": summary
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

