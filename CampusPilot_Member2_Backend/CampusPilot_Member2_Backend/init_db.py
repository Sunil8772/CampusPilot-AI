from pathlib import Path
from dotenv import load_dotenv
from database.db import get_connection

load_dotenv()
schema = Path("database/schema.sql").read_text(encoding="utf-8")
conn = get_connection()
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute(schema)
    print("CampusPilot database schema created successfully.")
finally:
    conn.close()
