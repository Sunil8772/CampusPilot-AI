import unittest
from datetime import datetime

from services.common import parse_datetime


class CommonDateTimeTests(unittest.TestCase):
    def test_parse_datetime_keeps_timezone(self):
        value = parse_datetime("2026-11-12T14:00:00+05:30")
        self.assertEqual(value.utcoffset().total_seconds(), 19800)

    def test_parse_datetime_adds_campus_timezone_to_naive(self):
        value = parse_datetime(datetime(2026, 11, 12, 14, 0))
        self.assertIsNotNone(value.tzinfo)
        self.assertEqual(value.utcoffset().total_seconds(), 19800)


if __name__ == "__main__":
    unittest.main()
