import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agent.orchestrator import process_user_request
from agent.tools import normalize_resource_type, _iso_datetime


def parsed_request(**updates):
    data = {
        "intent": "book_resources",
        "resource_types": ["Classroom"],
        "date": "2026-11-20",
        "start_time": "14:00",
        "end_time": "16:00",
        "capacity": 60,
        "purpose": "Faculty workshop",
        "missing_fields": [],
    }
    data.update(updates)
    return SimpleNamespace(model_dump=lambda: data)


class CampusPilotAgentTests(unittest.TestCase):
    @patch("agent.orchestrator.parse_user_request")
    def test_missing_details_are_requested_before_availability_call(self, parse):
        parse.return_value = parsed_request(date=None, missing_fields=["date"])
        with patch("agent.orchestrator.check_resource_availability") as availability:
            result = process_user_request("Book a room tomorrow")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("date", result["message"])
        availability.assert_not_called()

    @patch("agent.orchestrator.parse_user_request")
    def test_invalid_time_range_is_rejected(self, parse):
        parse.return_value = parsed_request(start_time="16:00", end_time="14:00")
        with patch("agent.orchestrator.check_resource_availability") as availability:
            result = process_user_request("Book a classroom")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("end time", result["message"].lower())
        availability.assert_not_called()

    @patch("agent.orchestrator.parse_user_request")
    @patch("agent.orchestrator.check_resource_availability")
    def test_booking_intent_checks_availability_but_does_not_create_booking(self, availability, parse):
        parse.return_value = parsed_request()
        availability.return_value = {
            "success": True,
            "message": "Availability check completed.",
            "available_resources": [
                {"id": 7, "name": "DEMO-EB1-101", "capacity": 60, "location": "Academic Block"}
            ],
        }
        result = process_user_request("Book a classroom for a workshop")
        self.assertEqual(result["status"], "availability_checked")
        self.assertTrue(result["can_submit_request"])
        self.assertIn("pending", result["message"].lower())
        availability.assert_called_once()
        # The orchestrator has no booking-write dependency by design.

    def test_resource_type_aliases(self):
        self.assertEqual(normalize_resource_type("Guest House"), "guest_house")
        self.assertEqual(normalize_resource_type("Classrooms"), "classroom")
        self.assertEqual(normalize_resource_type("Parking slots"), "parking")
        with self.assertRaises(ValueError):
            normalize_resource_type("Hotel ballroom")

    def test_datetime_uses_india_timezone(self):
        self.assertEqual(
            _iso_datetime("2026-11-20", "14:00"),
            "2026-11-20T14:00:00+05:30",
        )


if __name__ == "__main__":
    unittest.main()
