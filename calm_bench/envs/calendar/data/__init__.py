"""Data loading utilities for calendar domain."""

import json
import os
from typing import Any

FOLDER_PATH = os.path.dirname(__file__)


def _load_json(filename: str) -> Any:
    """Load a JSON file from the data directory."""
    filepath = os.path.join(FOLDER_PATH, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_data() -> dict[str, Any]:
    """
    Load all calendar domain data.
    
    Returns:
        Dictionary containing:
        - personas: User persona definitions
        - calendars: Calendar event data
        - external_constraints: Venue hours, transportation, services
        - scheduling_requests: Scheduling request templates
        - perturbations: Schedule perturbation scenarios
    """
    return {
        "personas": _load_json("personas.json"),
        "calendars": _load_json("calendars.json"),
        "external_constraints": _load_json("external_constraints.json"),
        "scheduling_requests": _load_json("scheduling_requests.json"),
        "perturbations": _load_json("perturbations.json"),
    }

