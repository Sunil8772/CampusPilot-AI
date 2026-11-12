import unittest
from availability_engine import normalize_room, parse_time, overlaps, find_free_slots

class AvailabilityEngineTests(unittest.TestCase):
    def test_room_alias_normalization(self):
        self.assertEqual(normalize_room("TB109"), "TB-109")
        self.assertEqual(normalize_room(" IET AMPHI "), "IET AMPHITHEATRE")

    def test_overlap_uses_half_open_intervals(self):
        self.assertTrue(overlaps(parse_time("10:00"), parse_time("11:00"),
                                 parse_time("10:30"), parse_time("11:30")))
        self.assertFalse(overlaps(parse_time("10:00"), parse_time("11:00"),
                                  parse_time("11:00"), parse_time("12:00")))

    def test_free_slots_returns_structured_values(self):
        slots = find_free_slots("BTech", 1, "A", "Monday")
        self.assertIsInstance(slots, list)
        if slots:
            self.assertIn("start_time", slots[0])
            self.assertIn("end_time", slots[0])

if __name__ == "__main__":
    unittest.main()
