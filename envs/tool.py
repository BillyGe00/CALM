"""Tool base class for CALM environment."""

import abc
from typing import Any


class Tool(abc.ABC):
    """Abstract base class for environment tools."""
    
    @staticmethod
    def invoke(*args, **kwargs):
        """Execute the tool with given arguments."""
        raise NotImplementedError

    @staticmethod
    def get_info() -> dict[str, Any]:
        """Return tool metadata in OpenAI function calling format."""
        raise NotImplementedError

