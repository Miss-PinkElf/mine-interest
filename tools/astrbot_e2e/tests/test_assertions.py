import unittest

from astrbot_e2e.assertions import contains, evaluate_logs, evaluate_messages, regex


class AssertionsTest(unittest.TestCase):
    def test_contains_all(self):
        result = contains("hello world", ["hello", "world"])
        self.assertTrue(result.ok)

    def test_contains_any(self):
        result = contains("hello", ["hello", "missing"], mode="any")
        self.assertTrue(result.ok)

    def test_contains_failure_keeps_actual(self):
        result = contains("hello", ["missing"])
        self.assertFalse(result.ok)
        self.assertIn("hello", result.actual)

    def test_contains_rejects_empty_needles(self):
        with self.assertRaises(ValueError):
            contains("hello", [])

    def test_contains_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            contains("hello", ["hello"], mode="none")

    def test_regex(self):
        self.assertTrue(regex("id=42", r"id=\d+").ok)
        self.assertFalse(regex("id=x", r"id=\d+").ok)

    def test_evaluate_logs(self):
        results = evaluate_logs("line one\nline two", [{"contains": ["line two"]}])
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].ok)

    def test_evaluate_messages_stops_after_failure(self):
        results = evaluate_messages(
            ["hello"],
            [
                {"contains": ["hello"]},
                {"contains": ["missing"]},
                {"contains": ["never-checked"]},
            ],
        )
        self.assertEqual(len(results), 2)
        self.assertFalse(results[1].ok)
