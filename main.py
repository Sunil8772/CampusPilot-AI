
from availability_engine import (
    show_day_timetable,
    check_availability,
    find_free_slots,
    check_room_availability,
    find_available_rooms,
    find_room_for_student_free_time
)


def get_student_details():
    program = input("Program (BTech/BBA): ")
    semester = input("Semester: ")
    section = input("Section: ")
    day = input("Day (Monday-Friday): ")

    batch = input("Batch (G1/G2 or press Enter if not applicable): ")

    if not batch.strip():
        batch = None

    return program, semester, section, day, batch


print("\n===== CampusPilot AI =====")
print("1. View Day Timetable")
print("2. Check Student Availability")
print("3. Find Student Free Slots")
print("4. Check Classroom Availability")
print("5. Find Available Classrooms")
print("6. Find Rooms During Student Free Time")

choice = input("\nChoose option (1-5): ")


# --------------------------------
# Option 1: Student timetable
# --------------------------------

if choice == "1":
    program, semester, section, day, batch = get_student_details()

    show_day_timetable(
        program, semester, section, day, batch
    )


# --------------------------------
# Option 2: Student availability
# --------------------------------

elif choice == "2":
    program, semester, section, day, batch = get_student_details()

    start_time = input("Start time (HH:MM): ")
    end_time = input("End time (HH:MM): ")

    result = check_availability(
        program, semester, section, day,
        start_time, end_time, batch
    )

    if result["available"]:
        print("\n✅ Student is FREE during this time.")

    else:
        print("\n❌ Student has class during this time.")

        for class_info in result["classes"]:
            print("Subject:", class_info["Subject"])
            print("Room:", class_info["Room"])
            print("Time:", class_info["Start Time"], "-", class_info["End Time"])


# --------------------------------
# Option 3: Student free slots
# --------------------------------

elif choice == "3":
    program, semester, section, day, batch = get_student_details()

    find_free_slots(
        program, semester, section, day, batch
    )


# --------------------------------
# Option 4: Check one classroom
# --------------------------------

elif choice == "4":
    day = input("Day (Monday-Friday): ")
    room = input("Room (e.g. EB2-106): ")
    start_time = input("Start time (HH:MM): ")
    end_time = input("End time (HH:MM): ")

    result = check_room_availability(
        day, room, start_time, end_time
    )

    if result["available"]:
        print("\n✅ Classroom is FREE.")

    else:
        print("\n❌ Classroom is OCCUPIED.")

        for class_info in result["classes"]:
            print("Program:", class_info["Program"])
            print("Semester:", class_info["Semester"])
            print("Section:", class_info["Section"])
            print("Subject:", class_info["Subject"])
            print("Time:", class_info["Start Time"], "-", class_info["End Time"])


# --------------------------------
# Option 5: Find available rooms
# --------------------------------

elif choice == "5":
    day = input("Day (Monday-Friday): ")
    start_time = input("Start time (HH:MM): ")
    end_time = input("End time (HH:MM): ")

    find_available_rooms(
        day, start_time, end_time
    )

elif choice == "6":
    program, semester, section, day, batch = get_student_details()

    start_time = input("Start time (HH:MM): ")
    end_time = input("End time (HH:MM): ")

    find_room_for_student_free_time(
        program, semester, section, day,
        start_time, end_time, batch
    )


else:
    print("Invalid option.")
