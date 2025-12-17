"""Calendar domain tools."""

from calm_bench.envs.calendar.tools.get_persona import GetPersona
from calm_bench.envs.calendar.tools.get_venue_hours import GetVenueHours
from calm_bench.envs.calendar.tools.get_calendar import GetCalendar
from calm_bench.envs.calendar.tools.get_busy_slots import GetBusySlots
from calm_bench.envs.calendar.tools.get_free_slots import GetFreeSlots
from calm_bench.envs.calendar.tools.add_event import AddEvent
from calm_bench.envs.calendar.tools.remove_event import RemoveEvent
from calm_bench.envs.calendar.tools.update_event import UpdateEvent

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

