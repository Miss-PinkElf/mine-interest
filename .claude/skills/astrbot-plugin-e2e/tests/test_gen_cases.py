import json
import tempfile
import unittest
from pathlib import Path

from scripts.gen_cases import generate_cases


def _features():
    return {
        "plugin": "demo_plugin",
        "features": [
            {
                "id": "command-help",
                "title": "命令 /help",
                "kind": "command",
                "trigger": "/help",
                "testability": "text",
                "risk": "medium",
            },
            {
                "id": "command-cc",
                "title": "命令 /cc",
                "kind": "command",
                "trigger": "/cc",
                "testability": "text",
                "risk": "high",
            },
            {
                "id": "command-cd",
                "title": "命令 /cd",
                "kind": "command",
                "trigger": "/cd <目录>",
                "testability": "text",
                "risk": "high",
            },
            {
                "id": "command-resume",
                "title": "命令 /resume",
                "kind": "command",
                "trigger": "/resume",
                "testability": "text",
                "risk": "high",
            },
            {
                "id": "event-all",
                "title": "事件 ALL",
                "kind": "event",
                "trigger": "ALL",
                "testability": "manual",
                "risk": "medium",
            },
        ],
    }


class GenCasesTest(unittest.TestCase):
    def test_generates_safe_command_cases_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = generate_cases(_features(), out, timeout=30)
            self.assertEqual(result["generated"], 1)
            case = json.loads((out / "command-help.json").read_text(encoding="utf-8"))
        self.assertEqual(case["plugin"], "demo_plugin")
        self.assertEqual(case["send"]["text"], "/help")
        self.assertEqual(case["send"]["group_id"], "{{group_id}}")
        self.assertIn("messages", case["expect"])

    def test_records_skipped_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = generate_cases(_features(), out, timeout=30)
            skipped = (out / "SKIPPED.md").read_text(encoding="utf-8")
        self.assertEqual(result["skipped"], 4)
        self.assertIn("/cc", skipped)
        self.assertIn("/cd", skipped)
        self.assertIn("/resume", skipped)
        self.assertIn("事件", skipped)

    def test_skips_features_marked_rich_media(self):
        features = {
            "plugin": "demo_plugin",
            "features": [
                {
                    "id": "command-help",
                    "title": "命令 /help",
                    "kind": "command",
                    "trigger": "/help",
                    "testability": "rich_media",
                    "risk": "medium",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = generate_cases(features, out, timeout=30)
            skipped = (out / "SKIPPED.md").read_text(encoding="utf-8")
        self.assertEqual(result["generated"], 0)
        self.assertIn("rich_media", skipped)
