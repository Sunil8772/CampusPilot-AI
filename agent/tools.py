"""Backend adapters used by the Gemini request orchestrator.

PostgreSQL is the source of truth for resource availability. The extracted CSV
is intentionally not cross-checked here because its rows are marked Needs Review.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from services.availability import find_available_resources

CAMPUS_TZ = ZoneInfo("Asia/Kolkata")
_ALLOWED_TYPES = {"classroom", "lab", "amphitheatre", "guest_house", "parking"}
_TYPE_ALIASES = {
    "classrooms": "classroom",
    "lecture hall": "classroom",
    "lecture halls": "classroom",
    "amphitheater": "amphitheatre",
    "amphitheaters": "amphitheatre",
    "guest house": "guest_house",
    "guest houses": "guest_house",
    "guesthouse": "guest_house",
    "guesthouses": "guest_house",
    "parking slot": "parking",
    "parking slots": "parking",
    "parking space": "parking",
    "parking spaces": "parking",
}


def normalize_resource_type(value):
    """Convert natural-language resource labels to the database enum."""
    key = str(value or "").strip().lower().replace("-", " ").replace("_", " ")
    normalized = _TYPE_ALIASES.get(key, key.replace(" ", "_"))
    if normalized not in _ALLOWED_TYPES:
        raise ValueError(f"Unsupported resource type: {value!r}")
    return normalized


def _iso_datetime(day, clock):
    date_value = datetime.strptime(str(day), "%Y-%m-%d").date()
    time_value = datetime.strptime(str(clock), "%H:%M").time()
    return datetime.combine(date_value, time_value, tzinfo=CAMPUS_TZ).isoformat()


def check_resource_availability(request):
    """Check published timetable, blocked periods and bookings in PostgreSQL."""
    for field in ("date", "start_time", "end_time", "resource_type"):
        if request.get(field) in (None, ""):
            raise ValueError(f"Missing required availability field: {field}")

    start = datetime.strptime(str(request["start_time"]), "%H:%M").time()
    end = datetime.strptime(str(request["end_time"]), "%H:%M").time()
    if start >= end:
        raise ValueError("End time must be after start time.")

    capacity = int(request.get("capacity") or 1)
    if capacity < 1:
        raise ValueError("Capacity must be at least 1.")

    backend_request = {
        "resource_type": normalize_resource_type(request["resource_type"]),
        "start_datetime": _iso_datetime(request["date"], request["start_time"]),
        "end_datetime": _iso_datetime(request["date"], request["end_time"]),
        "capacity": capacity,
    }
    # Do not filter again against the unverified extracted CSV. The published
    # PostgreSQL timetable is the authoritative source for this application.
    return find_available_resources(backend_request)
