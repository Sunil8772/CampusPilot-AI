import json
from agent.request_parser import parse_user_request
from database.db_manager import save_booking
# Later today, you will add: from tools import check_timetable, check_room

def process_message(prompt):
    """
    Takes the user's prompt from the UI, gets the structured JSON from Gemini,
    and decides what action to take (ask for missing fields or save booking).
    """
    try:
        # Fetch and forcefully clean Gemini's response
        raw_response = parse_user_request(prompt)
        clean_json = raw_response.strip().replace("```json", "").replace("```", "")

        # Load data
        booking_data = json.loads(clean_json)
        missing = booking_data.get("missing_fields", [])

        if missing:
            missing_str = ", ".join(missing).replace("_", " ")
            bot_reply = f"I still need a few details: {missing_str}"
        else:
            save_booking(booking_data)
            bot_reply = "Perfect! Your classroom is officially booked and saved to the database."
            
        return bot_reply

    except Exception as e:
        # Expose the exact failure point
        error_type = type(e).__name__
        return f"SYSTEM CRASH ({error_type}): {e}"