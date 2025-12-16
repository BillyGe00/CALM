"""Rules for calendar domain evaluation."""

RULES = [
    "Never schedule events during the user's sleep hours.",
    "Always check venue hours before scheduling location-dependent activities.",
    "Respect existing non-flexible (is_flexible=false) events.",
    "For high-priority requests, flexible events may be moved or dropped.",
    "Always confirm with the user before making changes to their calendar.",
    "Include buffer time between events at different locations.",
    "Honor the user's chronotype preferences when possible.",
    "Do not exceed the user's maximum work hours per day.",
    "Maintain minimum sleep hours as specified in user constraints.",
]

