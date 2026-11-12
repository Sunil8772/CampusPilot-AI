import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your local .env file.")
    return genai.Client(api_key=api_key)

def generate_json(prompt, response_schema):
    client = get_gemini_client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config={"response_mime_type": "application/json", "response_schema": response_schema, "temperature": 0.1},
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text
