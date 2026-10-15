import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arrears.service import (  # noqa: E402
    LISTED,
    NOT_FOUND,
    NOT_LISTED,
    MockLookupService,
    normalize_business_number,
)


class NormalizeTest(unittest.TestCase):
    def test_hyphens_and_spaces(self):
        self.assertEqual(normalize_business_number(" 000-00-00003 "), "0000000003")

    def test_wrong_length(self):
        self.assertIsNone(normalize_business_number("000-00-0000"))
        self.assertIsNone(normalize_business_number(""))


class MockLookupTest(unittest.TestCase):
    def setUp(self):
        self.service = MockLookupService()

    def test_listed(self):
        r = self.service.lookup("0000000003")
        self.assertEqual(r.status, LISTED)
        self.assertEqual(r.business_number, "000-00-00003")
        self.assertTrue(r.records)
        self.assertTrue(r.is_mock)

    def test_requested_test_number(self):
        r = self.service.lookup("3644501374")
        self.assertEqual(r.status, LISTED)
        self.assertEqual(r.business_number, "364-45-01374")

    def test_not_listed(self):
        r = self.service.lookup("0000000001")
        self.assertEqual(r.status, NOT_LISTED)
        self.assertEqual(r.records, [])

    def test_not_found(self):
        self.assertEqual(self.service.lookup("0000000009").status, NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
