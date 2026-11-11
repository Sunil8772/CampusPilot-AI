from datetime import datetime
from services.common import parse_datetime

def test_parse_datetime_keeps_timezone():
    value = parse_datetime("2026-11-12T14:00:00+05:30")
    assert value.utcoffset().total_seconds() == 19800

def test_parse_datetime_adds_campus_timezone_to_naive():
    value = parse_datetime(datetime(2026,11,12,14,0))
    assert value.tzinfo is not None
