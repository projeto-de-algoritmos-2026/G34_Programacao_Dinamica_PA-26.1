import unittest
from interval_scheduling import (
    Activity,
    schedule_activities,
    weighted_schedule_activities,
    find_conflicting_activity,
    parse_time,
    parse_duration,
    format_time,
)


class TestIntervalScheduling(unittest.TestCase):
    def test_parse_time(self):
        self.assertEqual(parse_time("08:30"), 8 * 60 + 30)
        self.assertEqual(parse_time("00:00"), 0)
        self.assertEqual(parse_time("23:59"), 23 * 60 + 59)
        with self.assertRaises(ValueError):
            parse_time("24:00")
        with self.assertRaises(ValueError):
            parse_time("12:60")
        with self.assertRaises(ValueError):
            parse_time("abc")

    def test_parse_duration(self):
        self.assertEqual(parse_duration("1.5", "h"), 90)
        self.assertEqual(parse_duration("30", "m"), 30)
        self.assertEqual(parse_duration("2,5", "horas"), 150)
        with self.assertRaises(ValueError):
            parse_duration("-5", "m")
        with self.assertRaises(ValueError):
            parse_duration("10", "invalid_unit")

    def test_format_time(self):
        self.assertEqual(format_time(510), "08:30")
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(1439), "23:59")

    def test_schedule_activities_greedy(self):
        # Overlapping activities
        # A: 08:00 - 09:00
        # B: 08:30 - 09:30
        # C: 09:00 - 10:00
        act_a = Activity("A", 480, 60)
        act_b = Activity("B", 510, 60)
        act_c = Activity("C", 540, 60)

        selected, rejected = schedule_activities([act_a, act_b, act_c])
        self.assertEqual(selected, [act_a, act_c])
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0][0], act_b)
        self.assertEqual(rejected[0][1], act_a)  # Conflicted with act_a

    def test_weighted_schedule_activities_dp(self):
        # Weighted scheduling test case
        # A: 08:00 - 09:30, weight 10
        # B: 08:30 - 10:00, weight 2
        # C: 09:00 - 11:00, weight 5
        act_a = Activity("A", 480, 90, 10.0)
        act_b = Activity("B", 510, 90, 2.0)
        act_c = Activity("C", 540, 120, 5.0)

        # Optimal selection should be just A (weight 10), because if we pick C (weight 5),
        # we can't pick A (ends at 9:30, overlaps with C starting at 9:00).
        # If we pick B and C, total weight is 7, which is < 10.
        selected, rejected, total_weight = weighted_schedule_activities([act_a, act_b, act_c])
        self.assertEqual(selected, [act_a])
        self.assertEqual(set(rejected), {act_b, act_c})
        self.assertEqual(total_weight, 10.0)

        # Another case where DP selects multiple compatible items
        # A: 08:00 - 09:00, weight 50
        # B: 08:30 - 10:00, weight 100
        # C: 09:30 - 11:00, weight 60
        act_a = Activity("A", 480, 60, 50.0)
        act_b = Activity("B", 510, 90, 100.0)
        act_c = Activity("C", 570, 90, 60.0)
        selected, rejected, total_weight = weighted_schedule_activities([act_a, act_b, act_c])
        # We can pick A (50) and C (60) since they don't overlap (A ends at 9:00, C starts at 9:30). Total weight = 110.
        # Or B (100). Max weight is 110.
        self.assertEqual(selected, [act_a, act_c])
        self.assertEqual(rejected, [act_b])
        self.assertEqual(total_weight, 110.0)

    def test_find_conflicting_activity(self):
        act_a = Activity("A", 480, 60)
        act_b = Activity("B", 510, 60)
        selected = [act_a]
        self.assertEqual(find_conflicting_activity(act_b, selected), act_a)

        act_c = Activity("C", 600, 60)
        self.assertIsNone(find_conflicting_activity(act_c, selected))


if __name__ == "__main__":
    unittest.main()
