from datetime import timedelta, time
from psycopg.errors import ExclusionViolation, ForeignKeyViolation
from database.db import get_cursor
from services.common import parse_datetime, result
from services.permissions import require_role
from services.audit import log_action

def create_booking_request(request):
    user_id = request.get("user_id")
    require_role(user_id,["student","faculty","admin"])
    resource_id = request.get("resource_id")
    start_dt = parse_datetime(request["start_datetime"])
    end_dt = parse_datetime(request["end_datetime"])
    capacity = int(request.get("capacity",1))
    purpose = str(request.get("purpose","")).strip()
    if end_dt <= start_dt:
        raise ValueError("end_datetime must be after start_datetime")
    if capacity < 1:
        raise ValueError("capacity must be at least 1")
    if not purpose:
        raise ValueError("purpose is required")
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id,capacity,is_active FROM resources WHERE id=%s FOR UPDATE",
                        (resource_id,))
            resource = cur.fetchone()
            if not resource or not resource["is_active"]:
                return result(False,"Resource not found or inactive.")
            if capacity > resource["capacity"]:
                return result(False,"Requested capacity exceeds resource capacity.")
            cur.execute(
                """INSERT INTO bookings(user_id,resource_id,start_datetime,end_datetime,
                                        requested_capacity,purpose,status)
                   VALUES (%s,%s,%s,%s,%s,%s,'pending') RETURNING *""",
                (user_id,resource_id,start_dt,end_dt,capacity,purpose),
            )
            booking = cur.fetchone()
            log_action(user_id,"booking_created","booking",booking["id"],
                       {"status":"pending","resource_id":resource_id},cur)
        return result(True,"Booking request submitted for admin approval.",
                      booking=booking,booking_id=booking["id"],status="pending")
    except ExclusionViolation:
        return result(False,"This resource is already reserved for part or all of that time.")
    except ForeignKeyViolation:
        return result(False,"Invalid user or resource ID.")

def get_user_bookings(user_id):
    require_role(user_id,["student","faculty","admin"])
    with get_cursor() as cur:
        cur.execute(
            """SELECT b.*,r.name AS resource_name,r.resource_type
               FROM bookings b JOIN resources r ON r.id=b.resource_id
               WHERE b.user_id=%s ORDER BY b.created_at DESC""",(user_id,))
        return cur.fetchall()

def get_pending_bookings(admin_id):
    require_role(admin_id,["admin"])
    with get_cursor() as cur:
        cur.execute(
            """SELECT b.*,r.name AS resource_name,u.full_name,u.email
               FROM bookings b JOIN resources r ON r.id=b.resource_id
               JOIN users u ON u.id=b.user_id
               WHERE b.status='pending' ORDER BY b.created_at"""
        )
        return cur.fetchall()

def _decide_booking(booking_id,actor_id,status,reason=None):
    require_role(actor_id,["admin"])
    with get_cursor() as cur:
        cur.execute("SELECT * FROM bookings WHERE id=%s FOR UPDATE",(booking_id,))
        booking = cur.fetchone()
        if not booking:
            return result(False,"Booking not found.")
        if booking["status"] != "pending":
            return result(False,f"Only pending bookings can be {status}.")
        if status == "approved":
            cur.execute(
                """SELECT 1 FROM room_blocks WHERE resource_id=%s
                   AND tstzrange(start_datetime,end_datetime,'[)') &&
                       tstzrange(%s,%s,'[)') LIMIT 1""",
                (booking["resource_id"],booking["start_datetime"],booking["end_datetime"]),
            )
            if cur.fetchone():
                return result(False,"The resource has a maintenance/blocked period.")

            # Recheck the latest published timetable at approval time.
            cur.execute("SELECT name,resource_code,resource_type FROM resources WHERE id=%s",
                        (booking["resource_id"],))
            resource = cur.fetchone()
            if resource and resource["resource_type"] in ("classroom","lab","amphitheatre"):
                start_dt, end_dt = booking["start_datetime"], booking["end_datetime"]
                day_cursor = start_dt.date()
                last_day = (end_dt - timedelta(microseconds=1)).date()
                while day_cursor <= last_day:
                    day_start = start_dt.time() if day_cursor == start_dt.date() else time.min
                    day_end = end_dt.time() if day_cursor == end_dt.date() else time.max
                    cur.execute(
                        """SELECT 1 FROM timetable_entries te
                           JOIN timetable_versions tv ON tv.id=te.version_id AND tv.is_published=TRUE
                           WHERE te.day_of_week=%s
                             AND upper(trim(te.room_name)) IN (upper(trim(%s)),upper(trim(%s)))
                             AND te.start_time < %s AND te.end_time > %s
                           LIMIT 1""",
                        (day_cursor.weekday(), resource["name"], resource["resource_code"],
                         day_end, day_start),
                    )
                    if cur.fetchone():
                        return result(False,"The latest published timetable now conflicts with this booking. Please review availability.")
                    day_cursor += timedelta(days=1)
        cur.execute(
            """UPDATE bookings SET status=%s,decision_by=%s,decision_at=NOW(),
                                  decision_reason=%s,updated_at=NOW()
               WHERE id=%s RETURNING *""",(status,actor_id,reason,booking_id))
        updated = cur.fetchone()
        log_action(actor_id,f"booking_{status}","booking",booking_id,{"reason":reason},cur)
    return result(True,f"Booking {status}.",booking=updated,status=status)

def approve_booking(booking_id,admin_id):
    return _decide_booking(booking_id,admin_id,"approved")

def reject_booking(booking_id,admin_id,reason):
    return _decide_booking(booking_id,admin_id,"rejected",reason)

def cancel_booking(booking_id,user_id):
    require_role(user_id,["student","faculty","admin"])
    with get_cursor() as cur:
        cur.execute("SELECT * FROM bookings WHERE id=%s FOR UPDATE",(booking_id,))
        booking = cur.fetchone()
        if not booking:
            return result(False,"Booking not found.")
        if booking["user_id"] != user_id:
            require_role(user_id,["admin"])
        if booking["status"] not in ("pending","approved"):
            return result(False,"Only pending or approved bookings can be cancelled.")
        cur.execute(
            """UPDATE bookings SET status='cancelled',updated_at=NOW()
               WHERE id=%s RETURNING *""",(booking_id,))
        updated = cur.fetchone()
        log_action(user_id,"booking_cancelled","booking",booking_id,{},cur)
    return result(True,"Booking cancelled.",booking=updated,status="cancelled")

def get_booking_by_id(booking_id, actor_id):
    """Fetch a booking for an authorized admin to verify a decision in PostgreSQL."""
    require_role(actor_id, ["admin"])
    with get_cursor() as cur:
        cur.execute(
            """SELECT b.*,r.name AS resource_name,r.resource_type,
                      u.full_name,u.email
               FROM bookings b
               JOIN resources r ON r.id=b.resource_id
               JOIN users u ON u.id=b.user_id
               WHERE b.id=%s""",
            (booking_id,),
        )
        return cur.fetchone()
