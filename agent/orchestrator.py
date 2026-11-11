from agent.request_parser import parse_user_request
from agent.tools import check_resource_availability
from agent.recommendations import format_availability_result

REQUIRED_AVAILABILITY_FIELDS = ("date", "start_time", "end_time", "resource_types")
REQUIRED_BOOKING_FIELDS = REQUIRED_AVAILABILITY_FIELDS + ("capacity", "purpose")

def process_user_request(user_message, user_id=None):
    """Understand and validate the request, then check availability only.
    No booking is created or approved by the AI agent.
    """
    try:
        parsed = parse_user_request(user_message)
        data = parsed.model_dump()
        intent = data["intent"]
        if intent not in ("check_availability", "check_timetable", "book_resources"):
            return {"status": "needs_clarification", "message": "Please clarify whether you want to check availability or request a booking."}
        missing = list(data.get("missing_fields") or [])
        required = REQUIRED_BOOKING_FIELDS if intent == "book_resources" else REQUIRED_AVAILABILITY_FIELDS
        if intent in ("book_resources", "check_availability"):
            for field in required:
                if data.get(field) in (None, "", []):
                    if field not in missing:
                        missing.append(field)
        if intent == "check_availability" and data.get("capacity") is None:
            data["capacity"] = 1
        if missing:
            return {"status": "needs_clarification", "parsed_request": data,
                    "message": "Please provide: " + ", ".join(x.replace("_", " ") for x in missing) + "."}
        if intent == "check_timetable":
            return {"status": "needs_clarification", "parsed_request": data,
                    "message": "Please provide program, semester, section and the day/time range for a timetable check."}
        results = []
        for resource_type in data["resource_types"]:
            request = dict(data, resource_type=resource_type)
            result = check_resource_availability(request)
            results.append({"resource_type": resource_type, "result": result,
                            "summary": format_availability_result(result, resource_type)})
        return {"status": "availability_checked", "parsed_request": data, "results": results,
                "message": "Availability results are shown below. Nothing has been booked; submit a request and wait for admin approval."}
    except Exception as exc:
        return {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
