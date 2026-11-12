import pdfplumber
import csv
import re
from pathlib import Path

DATA_FOLDER = Path(__file__).resolve().parent / "data" / "timetables"
PDF_PATH = DATA_FOLDER / "BBA_Timetable.pdf"
OUTPUT_PATH = DATA_FOLDER / "BBA_classes.csv"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# PDF column -> session name and time
SESSIONS = {
    2: ("Session 1", "09:00", "09:50"),
    3: ("Session 2", "10:00", "10:50"),
    4: ("Session 3", "11:00", "11:50"),
    5: ("Session 4", "12:00", "12:50"),
    6: ("Lunch", "13:00", "14:00"),
    7: ("Session 5", "14:00", "14:50"),
    8: ("Session 6", "15:00", "15:50"),
    9: ("Session 7", "16:00", "16:50"),
}

FIELDNAMES = [
    "Program",
    "Semester",
    "Section",
    "Day",
    "Start Time",
    "End Time",
    "Subject",
    "Faculty",
    "Room",
    "Source PDF Page",
    "Course Code",
    "Class Type",
    "Batch",
    "Group",
    "Section Home Room (PDF header)",
    "Verification Status",
]


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def get_programme_info(programme_text):
    text = programme_text.upper()

    semester = ""
    section = ""
    batch = ""

    if re.search(r"BBA\s*[- ]*I(?:\s|$)", text):
        semester = "1"
    elif re.search(r"BBA\s*[- ]*III", text):
        semester = "3"
    elif re.search(r"BBA\s*[- ]*V(?:\s|$)", text):
        semester = "5"

    if "SECTION A" in text:
        section = "A"
    elif "SECTION B" in text:
        section = "B"
    elif "SECTION C" in text:
        section = "C"
    elif "FINTECH" in text:
        section = "Fintech"
    elif semester == "3":
        section = "General"
    elif semester == "5":
        section = "General"

    batch = f"BBA Sem {semester}" if semester else ""

    return semester, section, batch


def extract_room(text):
    match = re.search(
        r"Room No\.?\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE
    )
    return match.group(1) if match else ""


def parse_class_details(details, home_room):
    details = clean(details)

    course_match = re.search(
        r"\b([A-Z]{1,3}\s?\d{3,5})\b",
        details
    )

    course_code = clean(course_match.group(1)) if course_match else ""

    faculty_match = re.search(
        r"(Dr\.?\s+[A-Za-z][A-Za-z .'-]+|"
        r"Ms\.?\s+[A-Za-z][A-Za-z .'-]+|"
        r"Mr\.?\s+[A-Za-z][A-Za-z .'-]+)",
        details
    )

    faculty = clean(faculty_match.group(1)) if faculty_match else ""

    # Keep the full details as Subject initially.
    # This avoids losing information when PDF text layout is complex.
    subject = details

    class_type = "Lecture"

    if "MENTORING" in details.upper():
        class_type = "Mentoring"
    elif "OPEN ELECTIVE" in details.upper():
        class_type = "Elective"
    elif "PRACTICAL" in details.upper() or "LAB" in details.upper():
        class_type = "Practical"

    room = extract_room(details) or home_room

    return subject, faculty, course_code, class_type, room


records = []

with pdfplumber.open(PDF_PATH) as pdf:

    for page_number, page in enumerate(pdf.pages, start=1):

        tables = page.extract_tables()

        if not tables:
            continue

        table = tables[0]

        # Each weekday block is 8 rows
        for block_start in range(5, len(table), 8):

            block = table[block_start:block_start + 8]

            day = next(
                (
                    row[0]
                    for row in block
                    if row[0] in DAYS
                ),
                None
            )

            if not day:
                continue

            current_programme = ""
            home_room = ""
            class_cells = {}

            def save_programme():
                if not current_programme:
                    return

                semester, section, batch = get_programme_info(
                    current_programme
                )

                for column, details_list in class_cells.items():

                    details = "\n".join(
                        clean(item)
                        for item in details_list
                        if clean(item)
                    )

                    if not details:
                        continue

                    session, start_time, end_time = SESSIONS[column]

                    subject, faculty, course_code, class_type, room = (
                        parse_class_details(details, home_room)
                    )

                    records.append({
                        "Program": "BBA",
                        "Semester": semester,
                        "Section": section,
                        "Day": day,
                        "Start Time": start_time,
                        "End Time": end_time,
                        "Subject": subject,
                        "Faculty": faculty,
                        "Room": room,
                        "Source PDF Page": page_number,
                        "Course Code": course_code,
                        "Class Type": class_type,
                        "Batch": batch,
                        "Group": "",
                        "Section Home Room (PDF header)": home_room,
                        "Verification Status": "Needs Review",
                    })

            for row in block:

                programme_cell = row[1] if len(row) > 1 else None

                # New programme starts
                if programme_cell:

                    save_programme()

                    current_programme = programme_cell
                    home_room = extract_room(programme_cell)

                    class_cells = {}

                if not current_programme:
                    continue

                # Collect session content, including continuation rows
                for column in SESSIONS:

                    if column >= len(row):
                        continue

                    value = clean(row[column])

                    if value:
                        class_cells.setdefault(column, []).append(value)

            # Save final programme in the block
            save_programme()


with open(
    OUTPUT_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(records)

print("BBA timetable converted to master format!")
print("Class entries:", len(records))
print("Output:", OUTPUT_PATH)