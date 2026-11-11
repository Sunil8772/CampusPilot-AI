# CampusPilot AI — Member 2 Backend

PostgreSQL database and Python services for resources, bookings, timetable storage,
role checks and audit logs.

## Add to the repository

Copy the contents of this package into the root of the existing `CampusPilot-AI`
repository. It adds `database/`, `services/`, `backend.py`, `init_db.py` and
`.env.example`. Do not replace the other members' `app.py`, `agent/`, `views/`
or timetable files.

## Requirements and setup

Use Python 3.10+ and PostgreSQL 14+.

Create a database once:
```sql
CREATE DATABASE campuspilot;
```

From the repository root:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the real password:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/campuspilot
```
Never commit `.env` or real credentials.

Create tables:
```bash
python init_db.py
```

## Demo users

Run from the project root:
```python
from services.permissions import upsert_user
admin = upsert_user("ADMIN-001","Campus Admin","admin@example.com","admin")
faculty = upsert_user("FAC-001","Demo Faculty","faculty@example.com","faculty")
student = upsert_user("STU-001","Demo Student","student@example.com","student")
print(admin,faculty,student)
```
Use the returned database IDs in the application. This helper is not an authentication
system; the frontend must supply verified user IDs from a trusted login/session.

## Add demo resources

```python
from services.resources import add_resource
add_resource("EB1-101","EB1-101","classroom",60,"EB1",["projector"],actor_id=ADMIN_ID)
add_resource("GH-01","Guest House Room 1","guest_house",2,"Guest House",actor_id=ADMIN_ID)
add_resource("PARK-A1","Visitor Parking A1","parking",1,"Main Gate",actor_id=ADMIN_ID)
```

## Function imports

```python
from backend import (
    get_resources, create_booking_request, get_user_bookings,
    get_pending_bookings, approve_booking, reject_booking, cancel_booking,
    find_available_resources, find_available_rooms,
    check_guest_house_availability, check_parking_availability,
    import_timetable_records, publish_timetable
)
```

Availability request:
```python
request = {
    "resource_type": "classroom",
    "start_datetime": "2026-11-12T14:00:00+05:30",
    "end_datetime": "2026-11-12T16:00:00+05:30",
    "capacity": 50
}
print(find_available_resources(request))
```

Booking request:
```python
booking = {
    "user_id": STUDENT_ID,
    "resource_id": RESOURCE_ID,
    "start_datetime": "2026-11-12T14:00:00+05:30",
    "end_datetime": "2026-11-12T16:00:00+05:30",
    "capacity": 50,
    "purpose": "Student workshop"
}
print(create_booking_request(booking))
```
A new request is `pending`, not confirmed. Admin actions:
```python
approve_booking(booking_id=BOOKING_ID,admin_id=ADMIN_ID)
reject_booking(booking_id=BOOKING_ID,admin_id=ADMIN_ID,reason="Resource unavailable")
```

## Import Member 1's timetable CSV

The supplied master CSV uses columns including `Program`, `Semester`, `Section`,
`Day`, `Start Time`, `End Time`, `Subject`, `Faculty`, `Room`, `Course Code`,
`Class Type` and `Batch`.

```python
import csv
from backend import import_timetable_records,publish_timetable

with open("data/timetables/Master_Timetable.csv",encoding="utf-8-sig",newline="") as f:
    rows = list(csv.DictReader(f))

# Import one program/semester at a time.
rows = [r for r in rows if r["Program"] == "BTech" and r["Semester"] == "1"]
draft = import_timetable_records(rows,"BTech",1,"2026-27",ADMIN_ID,
                                 "Master_Timetable.csv")
print(draft)
# Review the draft, then publish it:
publish_timetable(draft["import_id"],ADMIN_ID)
```

## Integration notes

- The function names match the Member 4 integration guide where possible.
- Member 3 must call `create_booking_request()` only after the user selects a resource
  and explicitly confirms. Remove/stop using Member 3's SQLite `save_booking()` path
  after this backend is integrated.
- Member 4 should call Python backend functions rather than writing directly to tables.
- Availability request fields: `resource_type`, `start_datetime`, `end_datetime`, `capacity`.
- Booking request fields: `user_id`, `resource_id`, `start_datetime`, `end_datetime`,
  `capacity`, `purpose`.
- Timetable CSV import creates a draft; publishing is a separate admin action.

## Safeguards and known limitations

- PostgreSQL exclusion constraint prevents overlapping pending/approved bookings for
  the same resource. Adjacent time slots are allowed.
- Backend functions enforce role checks for admin operations.
- Important booking, resource and timetable actions are written to `audit_logs`.
- Timetable versions are scoped by program, semester and academic year.
- Timetable conflict checking is based on weekly day/time entries and the requested
  date's weekday. Holiday calendars and one-off exceptions are not implemented.
- Timetable importer checks required fields and time ordering, but does not resolve
  every PDF parser warning or automatically create resource records.
- Room timetable matching compares normalised uppercase resource name/code against
  timetable room labels. Seed resource names consistently with Member 1's room names.
- Authentication itself is not implemented; the app must provide trusted user IDs.
- Multi-resource natural-language requests should be split into individual bookings
  after the user confirms each selected resource.

## Test before merging

1. Run `python init_db.py`.
2. Create demo users and resources.
3. Import a small timetable subset and publish it.
4. Create a pending booking and approve it as admin.
5. Attempt an overlapping booking for the same resource; it should be rejected.
6. Commit on your own branch and open a Pull Request to `main`.
