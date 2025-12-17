"""Calendar domain tools."""

from tau_bench.envs.calendar.tools.get_persona import GetPersona
from tau_bench.envs.calendar.tools.get_venue_hours import GetVenueHours
from tau_bench.envs.calendar.tools.get_calendar import GetCalendar
from tau_bench.envs.calendar.tools.get_busy_slots import GetBusySlots
from tau_bench.envs.calendar.tools.get_free_slots import GetFreeSlots
from tau_bench.envs.calendar.tools.add_event import AddEvent
from tau_bench.envs.calendar.tools.remove_event import RemoveEvent
from tau_bench.envs.calendar.tools.update_event import UpdateEvent

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

