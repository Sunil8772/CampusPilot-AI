"""Insert clearly synthetic demo users, resources and timetable rows."""
from dotenv import load_dotenv

from services.permissions import upsert_user
from services.resources import get_resources, add_resource
from services.timetable_storage import (
    get_published_timetable,
    import_timetable_records,
    publish_timetable,
)

load_dotenv()


def main():
    admin = upsert_user(
        "demo-admin",
        "CampusPilot Demo Admin",
        "admin@example.local",
        "admin",
    )
    admin_id = admin["id"]

    existing = {r["resource_code"] for r in get_resources(include_inactive=True)}
    demo_resources = [
        ("DEMO-EB1-101", "EB1-101", "classroom", 60, "Academic Block"),
        ("DEMO-EB1-102", "EB1-102", "classroom", 40, "Academic Block"),
        ("DEMO-IET-AMPHI", "IET Amphitheatre", "amphitheatre", 200, "Main Campus"),
        ("DEMO-LAB-01", "Computer Lab 1", "lab", 40, "Academic Block"),
        ("DEMO-GH-01", "Guest House Room 1", "guest_house", 2, "Guest House"),
        ("DEMO-GH-02", "Guest House Room 2", "guest_house", 2, "Guest House"),
        ("DEMO-PARK-01", "Visitor Parking Slot 1", "parking", 1, "Visitor Parking"),
        ("DEMO-PARK-02", "Visitor Parking Slot 2", "parking", 1, "Visitor Parking"),
    ]
    for code, name, kind, capacity, location in demo_resources:
        if code not in existing:
            add_resource(code, name, kind, capacity, location, actor_id=admin_id)

    # This is synthetic timetable data for the demonstration only. EB1-101 is
    # occupied from 14:00-16:00 on weekdays; the other demo rooms remain free
    # unless a booking or a published timetable record blocks them.
    if not get_published_timetable("DEMO", 1, "2026-27"):
        rows = [
            {
                "Program": "DEMO",
                "Semester": 1,
                "Section": "A",
                "Day": weekday,
                "Start Time": "14:00",
                "End Time": "16:00",
                "Subject": "Synthetic scheduled class",
                "Room": "EB1-101",
                "Faculty": "Demo Faculty",
                "Course Code": "DEMO101",
                "Class Type": "Lecture",
                "Batch": "",
            }
            for weekday in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
        ]
        imported = import_timetable_records(
            rows,
            program="DEMO",
            semester=1,
            academic_year="2026-27",
            uploaded_by=admin_id,
            source_filename="synthetic_demo_timetable.csv",
        )
        if not imported.get("success"):
            raise RuntimeError(imported.get("message", "Demo timetable import failed."))
        published = publish_timetable(imported["import_id"], admin_id)
        if not published.get("success"):
            raise RuntimeError(published.get("message", "Demo timetable publish failed."))

    print("Synthetic demo resources and timetable are ready.")
    print("Demo admin database ID:", admin_id)


if __name__ == "__main__":
    main()
