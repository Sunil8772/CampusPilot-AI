
import csv
from pathlib import Path
from datetime import datetime
def normalize_room(room):
    room = room.strip().upper()
    room = room.strip("()[]{}")
    room = " ".join(room.split())

    # Standardize confirmed formatting variations
    room_aliases = {
        "TB109": "TB-109",
        "IET AMPHI": "IET AMPHITHEATRE"
    }

    return room_aliases.get(room, room)

DATA_FILE = Path("../data/timetables/Master_Timetable.csv")

DAY_START = "09:00"
DAY_END = "17:00"


# -------------------------------
# Load master timetable
# -------------------------------

def load_timetable():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Master timetable not found: {DATA_FILE}"
        )

    with open(DATA_FILE, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def parse_time(value):
    return datetime.strptime(value.strip(), "%H:%M")


def overlaps(start1, end1, start2, end2):
    return start1 < end2 and end1 > start2


# -------------------------------
# Student timetable
# -------------------------------

def get_classes(program, semester, section, day, batch=None):
    classes = load_timetable()

    results = [
        row for row in classes
        if row["Program"].strip().lower() == program.strip().lower()
        and row["Semester"].strip() == str(semester).strip()
        and row["Section"].strip().lower() == section.strip().lower()
        and row["Day"].strip().lower() == day.strip().lower()
    ]

    # If batch is selected, include:
    # 1. Classes belonging to selected batch
    # 2. Common classes with blank batch

    if batch:
        selected_batch = batch.strip().upper()

        results = [
            row for row in results
            if row["Batch"].strip().upper() in ("", selected_batch)
        ]

    return sorted(
        results,
        key=lambda row: row["Start Time"]
    )


def show_day_timetable(program, semester, section, day, batch=None):
    classes = get_classes(
        program, semester, section, day, batch
    )

    print(f"\n{program} Semester {semester} - Section {section}")

    if batch:
        print(f"Batch: {batch}")

    print(f"Timetable for {day}\n")

    if not classes:
        print("No timetable entries found.")
        return

    for class_info in classes:
        print(
            f'{class_info["Start Time"]} - '
            f'{class_info["End Time"]} | '
            f'{class_info["Subject"]} | '
            f'Room: {class_info["Room"]} | '
            f'Batch: {class_info["Batch"] or "Common"}'
        )


# -------------------------------
# Student availability
# -------------------------------

def check_availability(
    program, semester, section, day,
    start_time, end_time, batch=None
):
    classes = get_classes(
        program, semester, section, day, batch
    )

    requested_start = parse_time(start_time)
    requested_end = parse_time(end_time)

    if requested_start >= requested_end:
        raise ValueError("End time must be after start time.")

    conflicts = []

    for class_info in classes:
        class_start = parse_time(class_info["Start Time"])
        class_end = parse_time(class_info["End Time"])

        if overlaps(
            requested_start, requested_end,
            class_start, class_end
        ):
            conflicts.append(class_info)

    return {
        "available": len(conflicts) == 0,
        "classes": conflicts
    }


# -------------------------------
# Student free slots
# -------------------------------

def find_free_slots(program, semester, section, day, batch=None):
    classes = get_classes(
        program, semester, section, day, batch
    )

    intervals = []

    for class_info in classes:
        start = parse_time(class_info["Start Time"])
        end = parse_time(class_info["End Time"])

        intervals.append((start, end))

    intervals.sort()

    current_time = parse_time(DAY_START)
    day_end = parse_time(DAY_END)

    free_slots = []

    for start, end in intervals:
        if start > current_time:
            free_slots.append((current_time, start))

        if end > current_time:
            current_time = end

    if current_time < day_end:
        free_slots.append((current_time, day_end))

    print(f"\nFree slots for {day}")

    if batch:
        print(f"Batch: {batch}")

    print()

    if not free_slots:
        print("No free slots found.")
        return

    for start, end in free_slots:
        print(
            start.strftime("%H:%M"),
            "-",
            end.strftime("%H:%M")
        )


# -------------------------------
# Classroom availability
# -------------------------------

def check_room_availability(day, room, start_time, end_time):
    classes = load_timetable()

    requested_start = parse_time(start_time)
    requested_end = parse_time(end_time)

    if requested_start >= requested_end:
        raise ValueError("End time must be after start time.")

    room = normalize_room(room)

    occupied_classes = []

    for class_info in classes:
        if (
            class_info["Day"].strip().lower() != day.strip().lower()
            or normalize_room(class_info["Room"]) != room
        ):
            continue

        class_start = parse_time(class_info["Start Time"])
        class_end = parse_time(class_info["End Time"])

        if overlaps(
            requested_start, requested_end,
            class_start, class_end
        ):
            occupied_classes.append(class_info)

    return {
        "available": len(occupied_classes) == 0,
        "classes": occupied_classes
    }


# -------------------------------
# Find available classrooms
# -------------------------------

def find_available_rooms(day, start_time, end_time):
    classes = load_timetable()

    requested_start = parse_time(start_time)
    requested_end = parse_time(end_time)

    if requested_start >= requested_end:
        raise ValueError("End time must be after start time.")

    all_rooms = set()
    occupied_rooms = set()

    for class_info in classes:
        room = normalize_room(class_info["Room"])

        if not room:
            continue

        all_rooms.add(room)

        if class_info["Day"].strip().lower() != day.strip().lower():
            continue

        class_start = parse_time(class_info["Start Time"])
        class_end = parse_time(class_info["End Time"])

        if overlaps(
            requested_start, requested_end,
            class_start, class_end
        ):
            occupied_rooms.add(room)

    available_rooms = sorted(all_rooms - occupied_rooms)

    print(f"\nAvailable classrooms on {day}")
    print(f"Time: {start_time} - {end_time}\n")

    if not available_rooms:
        print("No available classrooms found.")
        return

    for room in available_rooms:
        print("FREE:", room)

def find_room_for_student_free_time(
    program, semester, section, day,
    start_time, end_time, batch=None
):
    # First check whether student is free
    student_result = check_availability(
        program, semester, section, day,
        start_time, end_time, batch
    )

    if not student_result["available"]:
        print("\n❌ Student has a class during this time.")

        for class_info in student_result["classes"]:
            print("Subject:", class_info["Subject"])
            print("Room:", class_info["Room"])
            print(
                "Time:",
                class_info["Start Time"],
                "-",
                class_info["End Time"]
            )

        return

    print("\n✅ Student is free during this time.")
    print("Searching for available classrooms...")

    # Then find rooms available campus-wide
    find_available_rooms(day, start_time, end_time)
