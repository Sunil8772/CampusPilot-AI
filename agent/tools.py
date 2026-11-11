from datetime import datetime
from zoneinfo import ZoneInfo
from availability_engine import check_room_availability
from services.availability import find_available_resources

def _iso_datetime(day, clock):
    date_value = datetime.strptime(day, "%Y-%m-%d").date()
    time_value = datetime.strptime(clock, "%H:%M").time()
    return datetime.combine(date_value, time_value).replace(tzinfo=ZoneInfo("Asia/Kolkata")).isoformat()

def check_resource_availability(request):
    day, start, end = request["date"], request["start_time"], request["end_time"]
    if datetime.strptime(start, "%H:%M").time() >= datetime.strptime(end, "%H:%M").time():
        raise ValueError("End time must be after start time.")
    resource_type = request.get("resource_type")
    result = find_available_resources({
        "resource_type": resource_type,
        "start_datetime": _iso_datetime(day, start),
        "end_datetime": _iso_datetime(day, end),
        "capacity": int(request.get("capacity") or 1),
    })
    if not result.get("success"):
        return result
    candidates = result.get("available_resources", [])
    if resource_type in ("classroom", "lab", "amphitheatre"):
        still_free = []
        for item in candidates:
            room = item.get("name") or item.get("resource_code")
            try:
                check = check_room_availability(datetime.strptime(day, "%Y-%m-%d").strftime("%A"), room, start, end)
                if check["available"]:
                    still_free.append(item)
            except FileNotFoundError:
                still_free.append(item)
        result["available_resources"] = still_free
        result["message"] = "Checked database availability and available CSV timetable data."
    return result
