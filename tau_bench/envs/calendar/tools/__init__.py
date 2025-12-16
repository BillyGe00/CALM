"""Calendar domain tools."""

from envs.calendar.tools.get_persona import GetPersona
from envs.calendar.tools.get_venue_hours import GetVenueHours
from envs.calendar.tools.get_calendar import GetCalendar
from envs.calendar.tools.get_busy_slots import GetBusySlots
from envs.calendar.tools.get_free_slots import GetFreeSlots
from envs.calendar.tools.add_event import AddEvent
from envs.calendar.tools.remove_event import RemoveEvent
from envs.calendar.tools.update_event import UpdateEvent

ALL_TOOLS = [
    GetPersona,
    GetVenueHours,
    GetCalendar,
    GetBusySlots,
    GetFreeSlots,
    AddEvent,
    RemoveEvent,
    UpdateEvent,
]

__all__ = ["ALL_TOOLS"] + [tool.__name__ for tool in ALL_TOOLS]

