import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables (API key)
load_dotenv()

# Initialize the new standard Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define the exact JSON structure you need Gemini to return
class BookingRequest(BaseModel):
    intent: str = Field(description="The user's goal, e.g., 'book_resource', 'cancel_booking', 'check_availability'")
    resource_type: List[str] = Field(description="List of requested resources, e.g., ['classroom', 'guest house', 'parking']")
    date: Optional[str] = Field(description="Event date in YYYY-MM-DD format")
    start_time: Optional[str] = Field(description="Start time in HH:MM 24-hour format")
    end_time: Optional[str] = Field(description="End time in HH:MM 24-hour format")
    capacity: Optional[int] = Field(description="Number of participants")
    purpose: Optional[str] = Field(description="The name or purpose of the event")
    missing_fields: List[str] = Field(description="List of strictly required fields (date, start_time, end_time, capacity) that the user forgot to provide")

def parse_user_request(user_message: str) -> str:
    """
    Takes a natural language prompt and returns a strict JSON string 
    matching the BookingRequest schema.
    """
    prompt = f"""
    Extract the booking details from the following user request. 
    If a critical piece of information (date, time, capacity) is missing, note it in 'missing_fields'.
    
    User request: "{user_message}"
    """
    
    response = client.models.generate_content(
       model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BookingRequest,
            temperature=0.1, # Keep temperature low for deterministic data extraction
        ),
    )
    
    return response.text

# --- Test the Parser ---
if __name__ == "__main__":
    # Test Case 1: Complete Request (Your demo scenario)
    msg_complete = "Organise an AI workshop for 60 students next Friday from 2 PM to 4 PM. Arrange one guest room for the speaker and parking for two cars."
    print("Test 1 (Complete):")
    print(parse_user_request(msg_complete))
    
    print("\n" + "-"*40 + "\n")
    
    # Test Case 2: Incomplete Request
    msg_incomplete = "Book a classroom tomorrow."
    print("Test 2 (Incomplete - should flag missing fields):")
    print(parse_user_request(msg_incomplete))