import json
from agent.request_parser import parse_user_request
from database.db_manager import save_booking
from agent.tools import check_timetable, check_room_availability 

def process_message(prompt):
    try:
        raw_response = parse_user_request(prompt)
        clean_json = raw_response.strip().replace("```json", "").replace("```", "")
        parsed_data = json.loads(clean_json)
        
        intent = parsed_data.get("intent", "book_room") 

        # Check intent FIRST, before asking for missing booking fields
        if intent == "check_timetable":
            result = check_timetable(parsed_data.get("course_id"), parsed_data.get("date"))
            return result["message"]
            
        elif intent == "check_room":
            result = check_room_availability(parsed_data.get("room_id"), parsed_data.get("date"), "10:00")
            return f"Room status: {result['status']}"
            
        else: # If intent is book_room, then we check for missing fields
            missing = parsed_data.get("missing_fields", [])
            if missing:
                missing_str = ", ".join(missing).replace("_", " ")
                return f"I still need a few details: {missing_str}"
            else:
                save_booking(parsed_data)
                return "Perfect! Your classroom is officially booked and saved to the database."
            
    except Exception as e:
        error_type = type(e).__name__
        return f"SYSTEM CRASH ({error_type}): {e}"
    