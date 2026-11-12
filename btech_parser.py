
import re
import csv
from pathlib import Path
from openpyxl import load_workbook

DATA_FOLDER = Path(__file__).resolve().parent / "data" / "timetables"
INPUT_FILE = DATA_FOLDER / "JKLU_Timetables.xlsx"
OUTPUT_FILE = DATA_FOLDER / "BTech_classes.csv"

FIELDNAMES = [
    "Program", "Semester", "Section", "Day", "Start Time", "End Time",
    "Subject", "Faculty", "Room", "Source PDF Page", "Course Code",
    "Class Type", "Batch", "Group", "Section Home Room (PDF header)",
    "Verification Status",
]

TIME_SLOTS_SEM1 = {
    3: ("09:00", "09:50"),
    4: ("10:00", "10:50"),
    5: ("11:00", "11:50"),
    7: ("13:00", "13:50"),
    8: ("14:00", "14:50"),
    9: ("15:00", "15:50"),
    10: ("16:00", "16:50"),
}

TIME_SLOTS_OTHER = {
    3: ("09:00", "09:50"),
    4: ("10:00", "10:50"),
    5: ("11:00", "11:50"),
    6: ("12:00", "12:50"),
    8: ("14:00", "14:50"),
    9: ("15:00", "15:50"),
    10: ("16:00", "16:50"),

}

DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}

def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()

def parse_cell(text):
    if not text:
        return []

    # Separate stacked classes when there is a blank line
    blocks = re.split(r"\n\s*\n", str(text).strip())
    parsed = []

    for block in blocks:
        lines = [clean(x) for x in block.splitlines() if clean(x)]
        if not lines:
            continue

        original = "\n".join(lines)

        course_match = re.search(r"\(([A-Z]{2,4}\d{3,5})\)", original)
        course_code = course_match.group(1) if course_match else ""

        room_match = re.search(r"Room:\s*(.+)", original, re.I)
        room = clean(room_match.group(1)) if room_match else ""

        type_match = re.search(r"\(([LPT])(?:-([A-Z0-9]+))?\)", original, re.I)
        class_type = type_match.group(1).upper() if type_match else ""
        batch = type_match.group(2) if type_match and type_match.group(2) else ""

        faculty = ""
        for line in lines[1:]:
            if re.search(r"\b(Dr\.?|Mr\.?|Ms\.?|Mrs\.?)\b", line, re.I):
                faculty = re.sub(r"\s*\([LPT](?:-[A-Z0-9]+)?\)\s*", "", line, flags=re.I)
                break

        subject = lines[0]
        subject = re.sub(r"\s*\([A-Z]{2,4}\d{3,5}\)\s*", "", subject).strip()

        # Remove non-subject metadata
        subject = re.sub(r"\s*\(.*?\)\s*$", "", subject).strip()

        parsed.append({
            "Subject": subject,
            "Faculty": faculty,
            "Room": room,
            "Course Code": course_code,
            "Class Type": class_type,
            "Batch": batch,
        })

    return parsed

workbook = load_workbook(INPUT_FILE, data_only=True)
records = []

for sheet in workbook.worksheets:
    match = re.search(r"BTech Sem (\d+)", sheet.title)
    if not match:
        continue

    semester = match.group(1)

    for row in sheet.iter_rows(min_row=4, values_only=True):
        section_cell = clean(row[0])
        group_home = clean(row[1])
        day = clean(row[2])

        if day not in DAYS:
            continue

        section_match = re.search(r"\b([A-Z])\b", section_cell)
        section = section_match.group(1) if section_match else section_cell

        group = ""
        home_room = ""

        if "|" in group_home:
            group, home_room = [clean(x) for x in group_home.split("|", 1)]
        else:
            home_room = group_home

        if not home_room:
            room_match = re.search(r"\b(?:EB|TB)\d?-?\d+\b", group_home)
            home_room = room_match.group(0) if room_match else ""

        time_slots = TIME_SLOTS_SEM1 if semester == "1" else TIME_SLOTS_OTHER

        for col, (start, end) in time_slots.items():
            if col >= len(row):
                continue

            cell_value = row[col]
            if not cell_value:
                continue

            classes = parse_cell(cell_value)

            for item in classes:
                records.append({
                    "Program": "BTech",
                    "Semester": semester,
                    "Section": section,
                    "Day": day,
                    "Start Time": start,
                    "End Time": end,
                    "Subject": item["Subject"],
                    "Faculty": item["Faculty"],
                    "Room": item["Room"] or home_room,
                    "Source PDF Page": "",
                    "Course Code": item["Course Code"],
                    "Class Type": item["Class Type"],
                    "Batch": item["Batch"],
                    "Group": group,
                    "Section Home Room (PDF header)": home_room,
                    "Verification Status": "Needs Review",
                })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(records)

print("BTech timetable converted!")
print("Class entries:", len(records))
print("Output:", OUTPUT_FILE)
