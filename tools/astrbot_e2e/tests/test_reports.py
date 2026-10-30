import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.assertions import contains
from astrbot_e2e.reports import (
    create_run_dir,
    render_markdown,
    sanitize,
    slugify,
    write_json,
    write_summary,
)


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


class SanitizeTest(unittest.TestCase):
    def test_masks_qq_tokens_and_long_text(self):
        cfg = {
            "bot": {"qq": "3254276668", "token": "bot-token"},
            "sender": {"qq": "1961618848", "token": "sender-token"},
            "webui": {"password": "secret-pass"},
            "judge": {"api_key": "judge-key"},
            "astrbot": {"reverse_ws_token": "reverse-token"},
        }
        data = {
            "message": "机器人 3254276668 与发送者 1961618848 通信",
            "token": "bot-token",
            "nested": {
                "password": "secret-pass",
                "reverse_ws_token": "reverse-token",
                "long": "x" * 900,
            },
        }
        result = sanitize(data, cfg)
        text = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("3254276668", text)
        self.assertNotIn("1961618848", text)
        self.assertNotIn("bot-token", text)
        self.assertNotIn("secret-pass", text)
        self.assertNotIn("reverse-token", text)
        self.assertIn("***", text)
        self.assertIn("truncated", text)

    def test_redact_false_keeps_original(self):
        cfg = {"bot": {"qq": "3254276668", "token": "bot-token"}}
        data = {"message": "3254276668", "token": "bot-token"}
        self.assertEqual(sanitize(data, cfg, redact=False), data)


class RenderMarkdownTest(unittest.TestCase):
    def test_includes_summary_cases_failures_and_ops(self):
        suite = {
            "plugin": "cc_qq",
            "status": "FAILED",
            "started_at": "2026-10-30 10:00:00",
            "duration_seconds": 12.5,
            "cases": [
                {
                    "case": "help",
                    "status": "FAILED",
                    "run_dir": "/tmp/run/help",
                    "steps": [
                        {
                            "step": 1,
                            "status": "FAILED",
                            "results": [
                                {"kind": "contains", "ok": False, "detail": "命中 0/1"}
                            ],
                        }
                    ],
                },
                {
                    "case": "ping",
                    "status": "PASSED",
                    "run_dir": "/tmp/run/ping",
                    "steps": [],
                },
            ],
            "ops": ["2026-10-30 10:00:00 已启动测试实例 PID 123"],
        }
        text = render_markdown(suite)
        self.assertIn("## 摘要（Summary）", text)
        self.assertIn("## 用例结果（Cases）", text)
        self.assertIn("## 失败摘要（Failures）", text)
        self.assertIn("## 操作记录（Ops）", text)
        self.assertIn("已启动测试实例 PID 123", text)
        self.assertIn("命中 0/1", text)
