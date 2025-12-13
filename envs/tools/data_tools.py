"""Data query tools for CALM environment using FastMCP."""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("calm-env-tools")

# Get the data directory path
DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(filename: str) -> dict:
    """Helper to load JSON data files."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def get_persona(persona_id: str) -> dict:
    """
    Get detailed information about a specific persona.
    
    Args:
        persona_id: The ID of the persona (e.g., "graduate_student", "working_parent", "fitness_enthusiast")
    
    Returns:
        A dictionary containing the persona's information including:
        - name, role, preferences, constraints, ideal_schedule_distribution, personality_traits
        
        Returns an error dict if persona not found.
    """
    data = _load_json("personas.json")
    personas = data.get("personas", [])
    
    for persona in personas:
        if persona.get("id") == persona_id:
            return persona
    
    return {"error": f"Persona '{persona_id}' not found", "available_personas": [p.get("id") for p in personas]}


@mcp.tool()
def get_venue_hours(venue_id: str, day: str) -> dict:
    """
    Query the operating hours of a venue on a specific day.
    
    Args:
        venue_id: The ID of the venue (e.g., "gym", "library", "cafeteria", "swimming_pool", "grocery_store")
        day: The day of the week in lowercase (e.g., "monday", "tuesday", etc.)
    
    Returns:
        A dictionary containing:
        - venue name and type
        - open and close times for the specified day
        - additional info like peak hours if available
        
        Returns an error dict if venue or day not found.
    """
    data = _load_json("external_constraints.json")
    venues = data.get("venues", {})
    
    if venue_id not in venues:
        return {"error": f"Venue '{venue_id}' not found", "available_venues": list(venues.keys())}
    
    venue = venues[venue_id]
    hours = venue.get("hours", {})
    
    day_lower = day.lower()
    if day_lower not in hours:
        return {"error": f"No hours found for '{day}' at '{venue_id}'", "available_days": list(hours.keys())}
    
    result = {
        "venue_id": venue_id,
        "name": venue.get("name"),
        "type": venue.get("type"),
        "day": day_lower,
        "hours": hours[day_lower]
    }
    
    # Add extra info if available
    if "peak_hours" in venue:
        result["peak_hours"] = venue["peak_hours"]
    if "facilities" in venue:
        result["facilities"] = venue["facilities"]
    
    return result


# For direct testing
if __name__ == "__main__":
    # Test get_persona
    print("Testing get_persona('graduate_student'):")
    print(json.dumps(get_persona("graduate_student"), indent=2))
    print()
    
    # Test get_venue_hours
    print("Testing get_venue_hours('gym', 'monday'):")
    print(json.dumps(get_venue_hours("gym", "monday"), indent=2))
    print()
    
    # Test error cases
    print("Testing get_persona('unknown'):")
    print(json.dumps(get_persona("unknown"), indent=2))

