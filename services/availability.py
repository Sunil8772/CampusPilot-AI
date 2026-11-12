from database.db import get_cursor
from services.common import parse_datetime, result

def find_available_resources(request):
    resource_type = request.get("resource_type")
    start_dt = parse_datetime(request["start_datetime"])
    end_dt = parse_datetime(request["end_datetime"])
    capacity = int(request.get("capacity",1))
    if end_dt <= start_dt:
        raise ValueError("end_datetime must be after start_datetime")
    if capacity < 1:
        raise ValueError("capacity must be at least 1")
    with get_cursor() as cur:
        cur.execute(
            """SELECT r.* FROM resources r
               WHERE r.is_active=TRUE AND (%s::text IS NULL OR r.resource_type=%s)
                 AND r.capacity >= %s
                 AND NOT EXISTS (
                   SELECT 1 FROM bookings b WHERE b.resource_id=r.id
                     AND b.status IN ('pending','approved')
                     AND tstzrange(b.start_datetime,b.end_datetime,'[)') &&
                         tstzrange(%s,%s,'[)')
                 )
                 AND NOT EXISTS (
                   SELECT 1 FROM room_blocks rb WHERE rb.resource_id=r.id
                     AND tstzrange(rb.start_datetime,rb.end_datetime,'[)') &&
                         tstzrange(%s,%s,'[)')
                 )
               ORDER BY r.capacity,r.name""",
            (resource_type,resource_type,capacity,start_dt,end_dt,start_dt,end_dt),
        )
        rows = cur.fetchall()

    if resource_type in (None,"classroom","lab","amphitheatre"):
        weekday = start_dt.weekday()
        with get_cursor() as cur:
            cur.execute(
                """SELECT DISTINCT room_name FROM timetable_entries te
                   JOIN timetable_versions tv ON tv.id=te.version_id AND tv.is_published=TRUE
                   WHERE te.day_of_week=%s AND te.start_time < %s AND te.end_time > %s""",
                (weekday,end_dt.time(),start_dt.time()),
            )
            occupied = {r["room_name"].strip().upper() for r in cur.fetchall()}
        rows = [
            r for r in rows
            if r["resource_type"] not in ("classroom","lab","amphitheatre")
            or (r["name"].strip().upper() not in occupied
                and r["resource_code"].strip().upper() not in occupied)
        ]
    return result(True,"Availability check completed.",
                  available_resources=rows,unavailable_resources=[])

def find_available_rooms(request):
    data = dict(request)
    data.setdefault("resource_type","classroom")
    return find_available_resources(data)

def check_guest_house_availability(request):
    data = dict(request)
    data["resource_type"] = "guest_house"
    return find_available_resources(data)

def check_parking_availability(request):
    data = dict(request)
    data["resource_type"] = "parking"
    return find_available_resources(data)
