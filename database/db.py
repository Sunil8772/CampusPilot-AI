import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

def get_connection():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is missing. Copy .env.example to .env and set it.")
    return psycopg.connect(dsn, row_factory=dict_row)

@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()
