import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wage import calc as wc  # noqa: E402


class MinimumWageTest(unittest.TestCase):
    def test_2026_hourly(self):
        self.assertEqual(wc.minimum_hourly(2026), 10320)

    def test_unknown_year(self):
        with self.assertRaises(ValueError):
            wc.minimum_hourly(1990)

    def test_2026_monthly_full_time(self):
        # 고시 기준: 10,320원 x 209시간 = 2,156,880원
        self.assertEqual(wc.monthly_standard_hours(40), 209)
        self.assertEqual(wc.minimum_monthly(2026), 2156880)


class WeeklyHolidayTest(unittest.TestCase):
    def test_under_15_hours(self):
        self.assertEqual(wc.weekly_holiday_hours(14), 0)

    def test_full_time(self):
        self.assertEqual(wc.weekly_holiday_hours(40), 8)

    def test_part_time(self):
        # 주 20시간 -> 주휴 4시간 -> 10,320 x 4
        self.assertEqual(wc.weekly_holiday_pay(10320, 20), 41280)


class CheckTest(unittest.TestCase):
    def test_hourly_violation(self):
        r = wc.check_hourly(2026, 10000)
        self.assertTrue(r.is_violation)
        self.assertEqual(r.shortfall_per_hour, 320)

    def test_hourly_ok(self):
        self.assertFalse(wc.check_hourly(2026, 10320).is_violation)

    def test_probation(self):
        r = wc.check_hourly(2026, 9300, probation=True)
        self.assertEqual(r.minimum_hourly, 9288)
        self.assertFalse(r.is_violation)

    def test_monthly_full_time_ok(self):
        self.assertFalse(wc.check_monthly(2026, 2156880, 40).is_violation)

    def test_monthly_full_time_violation(self):
        self.assertTrue(wc.check_monthly(2026, 2000000, 40).is_violation)

    def test_daily_construction_example(self):
        # 일당 9만 원, 하루 10시간, 5인 이상 -> 90,000 / (8 + 2 x 1.5) = 약 8,182원
        r = wc.check_daily(2026, 90000, 10)
        self.assertTrue(r.is_violation)
        self.assertAlmostEqual(r.converted_hourly, 8181.8, places=1)
        self.assertIn("근로기준법 제56조", r.laws)

    def test_daily_under_five(self):
        # 5인 미만이면 가산 없이 90,000 / 10 = 9,000원
        r = wc.check_daily(2026, 90000, 10, five_or_more=False)
        self.assertEqual(r.converted_hourly, 9000)

    def test_daily_ok(self):
        self.assertFalse(wc.check_daily(2026, 82560, 8).is_violation)

    def test_format_has_disclaimer(self):
        text = wc.format_result(wc.check_hourly(2026, 10000))
        self.assertIn("320원", text)
        self.assertIn("법률 판단이 아닙니다", text)


if __name__ == "__main__":
    unittest.main()
