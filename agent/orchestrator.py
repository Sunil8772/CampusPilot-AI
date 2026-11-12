"""Request orchestration for CampusPilot AI.

The agent can interpret a request and check availability. It never approves a
booking. A booking request is created only after the user explicitly selects
an option and confirms in the frontend.
"""
from datetime import datetime

from agent.request_parser import parse_user_request
from agent.tools import check_resource_availability, normalize_resource_type
from agent.recommendations import format_availability_result

REQUIRED_AVAILABILITY_FIELDS = ("date", "start_time", "end_time", "resource_types")
REQUIRED_BOOKING_FIELDS = REQUIRED_AVAILABILITY_FIELDS + ("capacity", "purpose")


def process_user_request(user_message, user_id=None):
    """Parse a user request, ask for missing details, and check availability."""
    if not str(user_message or "").strip():
        return {"status": "needs_clarification", "message": "Please describe the campus resource you need."}

    try:
        parsed = parse_user_request(user_message)
        data = parsed.model_dump()
        intent = str(data.get("intent") or "").strip().lower()

        if intent not in ("check_availability", "check_timetable", "book_resources"):
            return {
                "status": "needs_clarification",
                "message": "Please clarify whether you want to check availability or request a booking.",
            }

        if intent == "check_timetable":
            return {
                "status": "needs_clarification",
                "parsed_request": data,
                "message": "Timetable lookup needs a program, semester, section and day. This demo currently supports resource availability and booking requests.",
            }

        missing = list(data.get("missing_fields") or [])
        required = REQUIRED_BOOKING_FIELDS if intent == "book_resources" else REQUIRED_AVAILABILITY_FIELDS
        for field in required:
            value = data.get(field)
            if value in (None, "", []):
                if field not in missing:
                    missing.append(field)

        if intent == "check_availability" and data.get("capacity") is None:
            data["capacity"] = 1

        if missing:
            return {
                "status": "needs_clarification",
                "parsed_request": data,
                "message": "Please provide: " + ", ".join(
                    field.replace("_", " ") for field in missing
                ) + ".",
            }

        # Validate date/time before contacting the database.
        datetime.strptime(data["date"], "%Y-%m-%d")
        start = datetime.strptime(data["start_time"], "%H:%M").time()
        end = datetime.strptime(data["end_time"], "%H:%M").time()
        if end <= start:
            return {
                "status": "needs_clarification",
                "parsed_request": data,
                "message": "The end time must be later than the start time. Please provide a valid time range.",
            }

        normalized_types = []
        for resource_type in data["resource_types"]:
            normalized = normalize_resource_type(resource_type)
            if normalized not in normalized_types:
                normalized_types.append(normalized)
        data["resource_types"] = normalized_types

        results = []
        for resource_type in normalized_types:
            request = dict(data, resource_type=resource_type)
            result = check_resource_availability(request)
            results.append({
                "resource_type": resource_type,
                "result": result,
                "summary": format_availability_result(result, resource_type),
            })

        options_found = any(
            item["result"].get("success")
            and item["result"].get("available_resources")
            for item in results
        )
        if intent == "book_resources":
            message = (
                "I found available options. Select one and explicitly confirm the booking request below. "
                "It will remain pending until an authorized admin approves it."
                if options_found else
                "No matching resource is currently available. No booking was created."
            )
        else:
            message = "Availability results are shown below. Nothing has been booked."

        return {
            "status": "availability_checked",
            "intent": intent,
            "parsed_request": data,
            "results": results,
            "can_submit_request": intent == "book_resources" and options_found,
            "message": message,
        }
    except (ValueError, TypeError) as exc:
        return {"status": "needs_clarification", "message": str(exc)}
    except Exception as exc:
        # Keep technical details useful for local debugging without claiming
        # any booking state or exposing secrets.
        return {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
