from datetime import datetime, time
from zoneinfo import ZoneInfo

CAMPUS_TZ = ZoneInfo("Asia/Kolkata")

def parse_datetime(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CAMPUS_TZ)
    return dt

def parse_time(value):
    if isinstance(value, time):
        return value
    return time.fromisoformat(str(value))

def result(success, message, **kwargs):
    return {"success": success, "message": message, **kwargs}
