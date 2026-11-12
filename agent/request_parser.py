from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List
from pydantic import BaseModel, Field
from agent.gemini_client import generate_json
from agent.prompts import REQUEST_EXTRACTION_PROMPT

class ParsedCampusRequest(BaseModel):
    intent: str = Field(description="check_availability, check_timetable, or book_resources")
    resource_types: List[str] = Field(default_factory=list)
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    capacity: Optional[int] = None
    purpose: Optional[str] = None
    program: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    batch: Optional[str] = None
    room_name: Optional[str] = None
    missing_fields: List[str] = Field(default_factory=list)

def parse_user_request(user_message: str) -> ParsedCampusRequest:
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    prompt = REQUEST_EXTRACTION_PROMPT.format(today=today, message=user_message)
    return ParsedCampusRequest.model_validate_json(generate_json(prompt, ParsedCampusRequest))
