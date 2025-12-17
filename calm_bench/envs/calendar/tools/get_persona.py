"""Tool for getting persona information."""

import json
from typing import Any, Dict
from calm_bench.envs.tool import Tool


class GetPersona(Tool):
    """Get detailed information about a specific persona."""
    
    @staticmethod
    def invoke(data: Dict[str, Any], persona_id: str) -> str:
        """
        Get persona details by ID.
        
        Args:
            data: Environment data dictionary
            persona_id: The ID of the persona (e.g., "graduate_student")
            
        Returns:
            JSON string with persona information or error message
        """
        personas_data = data.get("personas", {})
        personas = personas_data.get("personas", [])
        
        for persona in personas:
            if persona.get("id") == persona_id:
                return json.dumps(persona, indent=2)
        
        available = [p.get("id") for p in personas]
        return json.dumps({
            "error": f"Persona '{persona_id}' not found",
            "available_personas": available
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_persona",
                "description": "Get detailed information about a specific persona including their preferences, constraints, and ideal schedule distribution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "persona_id": {
                            "type": "string",
                            "description": "The ID of the persona (e.g., 'graduate_student', 'working_parent', 'fitness_enthusiast')",
                        },
                    },
                    "required": ["persona_id"],
                },
            },
        }

