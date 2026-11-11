"""Insert clearly synthetic demo users/resources for local judging."""
from dotenv import load_dotenv
from services.permissions import upsert_user
from services.resources import get_resources, add_resource

load_dotenv()

def main():
    admin = upsert_user("demo-admin", "CampusPilot Demo Admin", "admin@example.local", "admin")
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
    print("Synthetic demo resources are ready. Demo admin database ID:", admin_id)

if __name__ == "__main__":
    main()
