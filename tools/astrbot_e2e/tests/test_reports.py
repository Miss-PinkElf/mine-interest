import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.assertions import contains
from astrbot_e2e.reports import create_run_dir, slugify, write_json, write_summary


class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_slugify(self):
        self.assertEqual(slugify("cc_qq /help 群聊回执"), "cc_qq-help")

    def test_create_run_dir_is_unique(self):
        first = create_run_dir(self.base, "case")
        second = create_run_dir(self.base, "case")
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_dir())

    def test_write_summary_contains_status(self):
        run_dir = create_run_dir(self.base, "case")
        summary = write_summary(run_dir, "case", "PASSED", [], 1.2, {"evidence": "x"})
        saved = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "PASSED")
        self.assertEqual(summary["duration_seconds"], 1.2)

    def test_write_summary_merges_extra(self):
        run_dir = create_run_dir(self.base, "case")
        summary = write_summary(run_dir, "case", "FAILED", [], 0.1, {"evidence": "x", "note": "y"})
        saved = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["evidence"], "x")
        self.assertEqual(saved["note"], "y")
        self.assertEqual(summary["note"], "y")

    def test_write_summary_serializes_assertion_results(self):
        run_dir = create_run_dir(self.base, "case")
        result = contains("hello world", ["hello"])
        write_summary(run_dir, "case", "PASSED", [result], 0.1)
        saved = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["assertions"][0]["kind"], "contains")
        self.assertTrue(saved["assertions"][0]["ok"])
        self.assertEqual(saved["assertions"][0]["detail"], "命中 1/1")

    def test_write_json(self):
        path = self.base / "a.json"
        write_json(path, {"ok": True})
        self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["ok"])
