import sqlite3

def init_db():
    # Creates the database file and the bookings table
    conn = sqlite3.connect("campus_pilot.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_type TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            capacity INTEGER,
            purpose TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_booking(booking_data):
    # Inserts the finalized JSON data into the table
    conn = sqlite3.connect("campus_pilot.db")
    cursor = conn.cursor()
    
    # Extract the first resource from the list safely
    resource_list = booking_data.get("resource_type", [])
    resource = resource_list[0] if resource_list else "unknown"
    
    cursor.execute('''
        INSERT INTO bookings (resource_type, date, start_time, end_time, capacity, purpose)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        resource,
        booking_data.get("date"),
        booking_data.get("start_time"),
        booking_data.get("end_time"),
        booking_data.get("capacity"),
        booking_data.get("purpose")
    ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and bookings table created successfully!")