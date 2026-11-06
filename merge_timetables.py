
import csv
from pathlib import Path

DATA_FOLDER = Path("../data/timetables")

BTECH_FILE = DATA_FOLDER / "BTech_classes.csv"
BBA_FILE = DATA_FOLDER / "BBA_classes.csv"
OUTPUT_FILE = DATA_FOLDER / "Master_Timetable.csv"

all_records = []

for file_path in [BTECH_FILE, BBA_FILE]:
    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        all_records.extend(reader)

if all_records:
    fieldnames = list(all_records[0].keys())

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

print("Master timetable created successfully!")
print("Total entries:", len(all_records))
print("Output:", OUTPUT_FILE)
