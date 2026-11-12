import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "timetables" / "Master_Timetable.csv"
DAY_START = "09:00"
DAY_END = "17:00"


def normalize_room(room):
    room = str(room or "").strip().upper().strip("()[]{}")
    room = " ".join(room.split())
    aliases = {
        "TB109": "TB-109", "TB114": "TB-114", "TB105": "TB-105",
        "TB106": "TB-106", "TB05": "TB-105",
        "IET AMPHI": "IET AMPHITHEATRE",
    }
    return aliases.get(room, room)


def load_timetable():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Master timetable not found: {DATA_FILE}")
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def parse_time(value):
    return datetime.strptime(str(value).strip(), "%H:%M")


def overlaps(start1, end1, start2, end2):
    return start1 < end2 and end1 > start2


def get_classes(program, semester, section, day, batch=None):
    rows = load_timetable()
    results = [
        row for row in rows
        if row.get("Program", "").strip().lower() == program.strip().lower()
        and row.get("Semester", "").strip() == str(semester).strip()
        and row.get("Section", "").strip().lower() == section.strip().lower()
        and row.get("Day", "").strip().lower() == day.strip().lower()
        and (not batch or row.get("Batch", "").strip().upper() in ("", batch.strip().upper()))
    ]
    return sorted(results, key=lambda row: row.get("Start Time", ""))


def show_day_timetable(program, semester, section, day, batch=None):
    classes = get_classes(program, semester, section, day, batch)
    return classes


def check_availability(program, semester, section, day, start_time, end_time, batch=None):
    start, end = parse_time(start_time), parse_time(end_time)
    if start >= end:
        raise ValueError("End time must be after start time.")
    conflicts = [
        row for row in get_classes(program, semester, section, day, batch)
        if overlaps(start, end, parse_time(row["Start Time"]), parse_time(row["End Time"]))
    ]
    return {"available": not conflicts, "classes": conflicts}


def find_free_slots(program, semester, section, day, batch=None):
    intervals = sorted(
        (parse_time(row["Start Time"]), parse_time(row["End Time"]))
        for row in get_classes(program, semester, section, day, batch)
    )
    current, day_end = parse_time(DAY_START), parse_time(DAY_END)
    slots = []
    for start, end in intervals:
        if start > current:
            slots.append({"start_time": current.strftime("%H:%M"), "end_time": start.strftime("%H:%M")})
        current = max(current, end)
    if current < day_end:
        slots.append({"start_time": current.strftime("%H:%M"), "end_time": day_end.strftime("%H:%M")})
    return slots


def check_room_availability(day, room, start_time, end_time):
    start, end = parse_time(start_time), parse_time(end_time)
    if start >= end:
        raise ValueError("End time must be after start time.")
    room = normalize_room(room)
    conflicts = [
        row for row in load_timetable()
        if row.get("Day", "").strip().lower() == day.strip().lower()
        and normalize_room(row.get("Room")) == room
        and overlaps(start, end, parse_time(row["Start Time"]), parse_time(row["End Time"]))
    ]
    return {"available": not conflicts, "classes": conflicts}


def find_available_rooms(day, start_time, end_time):
    start, end = parse_time(start_time), parse_time(end_time)
    if start >= end:
        raise ValueError("End time must be after start time.")
    rows = load_timetable()
    all_rooms = {normalize_room(row.get("Room")) for row in rows if normalize_room(row.get("Room"))}
    occupied = {
        normalize_room(row.get("Room")) for row in rows
        if row.get("Day", "").strip().lower() == day.strip().lower()
        and overlaps(start, end, parse_time(row["Start Time"]), parse_time(row["End Time"]))
    }
    return sorted(all_rooms - occupied)


def find_room_for_student_free_time(program, semester, section, day, start_time, end_time, batch=None):
    student = check_availability(program, semester, section, day, start_time, end_time, batch)
    if not student["available"]:
        return {"student_available": False, "conflicts": student["classes"], "available_rooms": []}
    return {
        "student_available": True,
        "conflicts": [],
        "available_rooms": find_available_rooms(day, start_time, end_time),
    }
