import json
from agent.request_parser import parse_user_request
from agent.tools import check_timetable, check_room_availability, book_room

def process_message(prompt):
    try:
        raw_response = parse_user_request(prompt)
        clean_json = raw_response.strip().replace("```json", "").replace("```", "")
        parsed_data = json.loads(clean_json)

        intent = parsed_data.get("intent", "book_room")

        if intent == "check_timetable":
            result = check_timetable(parsed_data.get("course_id"), parsed_data.get("date"))
            return result["message"]

        elif intent == "check_room":
            # Using 10:00 AM as a default time string if none is provided
            result = check_room_availability(parsed_data.get("room_id"), parsed_data.get("date"), "10:00 AM")
            return f"Room status: {result['message']}"

        else: # If intent is book_room
            missing = parsed_data.get("missing_fields", [])
            if missing:
                missing_str = ", ".join(missing).replace("_", " ")
                return f"I still need a few details: {missing_str}"
            else:
                # We now route the finalized booking straight to our new tools.py function!
                result = book_room(parsed_data.get("room_id"), parsed_data.get("date"), parsed_data.get("time"))
                return result["message"]

    except Exception as e:
        error_type = type(e).__name__
        return f"SYSTEM CRASH ({error_type}): {e}"