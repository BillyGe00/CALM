"""Tool for getting venue operating hours."""

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetVenueHours(Tool):
    """Query the operating hours of a venue on a specific day."""
    
    @staticmethod
    def invoke(data: Dict[str, Any], venue_id: str, day: str) -> str:
        """
        Get venue hours for a specific day.
        
        Args:
            data: Environment data dictionary
            venue_id: The ID of the venue
            day: The day of the week (e.g., "monday")
            
        Returns:
            JSON string with venue hours or error message
        """
        constraints = data.get("external_constraints", {})
        venues = constraints.get("venues", {})
        
        if venue_id not in venues:
            return json.dumps({
                "error": f"Venue '{venue_id}' not found",
                "available_venues": list(venues.keys())
            })
        
        venue = venues[venue_id]
        hours = venue.get("hours", {})
        
        day_lower = day.lower()
        if day_lower not in hours:
            return json.dumps({
                "error": f"No hours found for '{day}' at '{venue_id}'",
                "available_days": list(hours.keys())
            })
        
        result = {
            "venue_id": venue_id,
            "name": venue.get("name"),
            "type": venue.get("type"),
            "day": day_lower,
            "hours": hours[day_lower]
        }
        
        # Add extra info if available
        for key in ["peak_hours", "facilities", "quiet_hours", "meal_times", 
                    "lap_swim_hours", "busy_hours"]:
            if key in venue:
                result[key] = venue[key]
        
        return json.dumps(result, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_venue_hours",
                "description": "Query the operating hours of a venue on a specific day. Returns open/close times and additional info like peak hours.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "venue_id": {
                            "type": "string",
                            "description": "The ID of the venue (e.g., 'gym', 'library', 'cafeteria', 'swimming_pool', 'grocery_store')",
                        },
                        "day": {
                            "type": "string",
                            "description": "The day of the week in lowercase (e.g., 'monday', 'tuesday')",
                        },
                    },
                    "required": ["venue_id", "day"],
                },
            },
        }

