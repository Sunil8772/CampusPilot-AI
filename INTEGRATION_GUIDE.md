# CampusPilot AI — Integration Guide

**Project:** JKLU AI Buildathon 2026  
**Problem Statement:** PS-02 — Smart Campus Venue, Guest House and Parking Management Agent  
**Team Size:** 4 Members

---

## 1. Project Architecture

CampusPilot AI is a Streamlit-based web application that uses an AI agent and backend services to manage campus resources.

Main workflow:

1. User submits a booking request.
2. AI agent understands the request.
3. AI agent identifies missing information.
4. Availability engine checks timetables and existing bookings.
5. Agent recommends suitable resources.
6. User confirms their selection.
7. Booking backend creates a pending request.
8. Admin approves or rejects the request.
9. Database and audit logs are updated.

## 2. Responsibilities

### Member 1 — Timetable Parser and Availability

Owns:
- PDF, Excel and CSV timetable parsing.
- Timetable normalisation and validation.
- Multi-semester timetable handling.
- Classroom availability checks.
- Booking conflict checks.
- Alternative resource recommendations.

Expected modules:
- timetable/parser.py
- timetable/normalizer.py
- timetable/validator.py
- services/availability.py
- services/alternatives.py

### Member 2 — Database and Backend

Owns:
- PostgreSQL database.
- Booking management.
- Resource management.
- Timetable draft storage and publishing.
- User roles and permissions.
- Audit logging.
- Double-booking protection.

Expected modules:
- database/db.py
- database/schema.sql
- services/booking.py
- services/resources.py
- services/timetable_storage.py
- services/permissions.py
- services/audit.py

### Member 3 — AI Agent

Owns:
- Gemini API integration.
- Natural-language request understanding.
- Missing-information detection.
- Agent planning and orchestration.
- Calling backend tools.
- Alternative recommendations.
- Confirmation and booking verification workflow.

Expected modules:
- agent/gemini_client.py
- agent/request_parser.py
- agent/orchestrator.py
- agent/tools.py
- agent/prompts.py

### Member 4 — Frontend and Integration

Owns:
- Streamlit application.
- Student, Faculty and Admin interfaces.
- AI assistant interface.
- Availability interface.
- My Bookings interface.
- Admin dashboard.
- Timetable and resource management interfaces.
- Reports, testing and documentation.

Expected modules:
- app.py
- views/student_dashboard.py
- views/faculty_dashboard.py
- views/admin_dashboard.py
- views/ai_assistant.py
- views/availability.py
- views/my_bookings.py

---

## 3. Common Data Formats

All members should use consistent field names.

### Availability request

```python
{
    "resource_type": "Classroom",
    "date": "2026-11-12",
    "start_time": "14:00",
    "end_time": "16:00",
    "capacity": 50,
    "purpose": "Faculty workshop"
}
```

### Availability response

```python
{
    "success": True,
    "available_resources": [
        {
            "resource_id": "R001",
            "name": "EB1-101",
            "capacity": 60,
            "location": "EB1"
        }
    ],
    "unavailable_resources": [],
    "message": "Availability check completed."
}
```

### Booking request

```python
{
    "user_id": "FAC-001",
    "resource_id": "R001",
    "start_datetime": "2026-11-12T14:00:00+05:30",
    "end_datetime": "2026-11-12T16:00:00+05:30",
    "capacity": 50,
    "purpose": "Faculty workshop"
}
```

### Booking response

```python
{
    "success": True,
    "booking_id": "BK-1001",
    "status": "pending",
    "message": "Booking request submitted."
}
```

These are proposed interface examples. Members must confirm the final function signatures and response formats before integration.

---

## 4. Expected Function Interfaces

### Member 1

```python
find_available_rooms(request)
get_alternatives(request)
check_timetable_conflict(request)
```

### Member 2

```python
get_resources(resource_type=None)
create_booking_request(request)
get_user_bookings(user_id)
approve_booking(booking_id, admin_id)
reject_booking(booking_id, admin_id, reason)
check_guest_house_availability(request)
check_parking_availability(request)
```

### Member 3

```python
process_user_request(user_message, user_id)
```

### Member 4

Frontend should call the functions provided by Members 1, 2 and 3.

Frontend must not directly modify database tables.

---

## 5. Important Integration Rules

1. All members must push code to their own GitHub branches.
2. Do not directly push to main.
3. Create Pull Requests for review.
4. Do not overwrite another member's modules.
5. Use the agreed request and response formats.
6. Keep API keys and database passwords in .env.
7. Never upload .env to GitHub.
8. Commit .env.example without real credentials.
9. Handle exceptions and unsuccessful responses.
10. Test every module independently before integration.

---

## 6. Security and Approval Rules

- Use synthetic users and demonstration data.
- Students and Faculty must not access Admin-only operations.
- Backend permissions must be enforced independently of frontend navigation.
- Booking requests must remain pending until admin approval.
- Recheck availability before approving a booking.
- Record important actions in audit logs.
- Preserve previous published timetable versions.
- Never silently cancel approved bookings after a timetable update.

---

## 7. Main Demonstration Workflow

Example:

A faculty member requests a classroom for 60 participants next Friday from 2 PM to 4 PM, guest accommodation for one speaker and parking for two visitor vehicles.

Expected agent workflow:

1. Understand the complete request.
2. Check whether any details are missing.
3. Plan classroom, guest house and parking checks.
4. Check timetable and booking conflicts.
5. Find available resources.
6. Recommend alternatives if necessary.
7. Ask the user to select and confirm.
8. Create pending booking requests.
9. Admin reviews and approves.
10. Verify booking status and display confirmation.

---

## 8. Final Integration Goal

All four modules should work together as one application.

The final demonstration must show:
- Natural-language understanding.
- Multi-step agent planning.
- Real availability checks against the demo database.
- Conflict detection.
- Alternative recommendations.
- Booking request creation.
- Admin approval.
- Database updates.
- Audit logging.
- Successful booking verification.

**Important:** Do not claim a booking is confirmed until the backend verifies its approved status.