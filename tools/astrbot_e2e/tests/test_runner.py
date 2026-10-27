import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from astrbot_e2e.assertions import AssertionResult
from astrbot_e2e.runner import _status_from_results, run_case


def _config(root: Path) -> Dict[str, Any]:
    return {
        "test_root": str(root),
        "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "pass"},
        "astrbot": {
            "command": "astrbot",
            "reverse_ws_host": "127.0.0.1",
            "reverse_ws_port": 6198,
            "reverse_ws_token": "token",
            "plugins": ["astrbot_plugin_e2e_probe"],
            "startup_timeout_seconds": 1,
        },
        "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "t"},
        "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "t"},
        "group_id": "123456789",
        "judge": {},
        "timeouts": {"message_seconds": 1},
    }


class StatusFromResultsTest(unittest.TestCase):
    def test_all_passed(self):
        results = [AssertionResult("contains", True, "x", "x", "命中 1/1")]
        self.assertEqual(_status_from_results(results), "PASSED")

    def test_any_failure(self):
        results = [AssertionResult("contains", False, "x", "y", "命中 0/1")]
        self.assertEqual(_status_from_results(results), "FAILED")

    def test_only_skipped(self):
        results = [
            AssertionResult("semantic", False, "criteria", "", "SKIPPED: LLM 判定未配置")
        ]
        self.assertEqual(_status_from_results(results), "SKIPPED")

    def test_failure_takes_precedence_over_skipped(self):
        results = [
            AssertionResult("contains", False, "x", "y", "命中 0/1"),
            AssertionResult("semantic", False, "criteria", "", "SKIPPED: LLM 判定未配置"),
        ]
        self.assertEqual(_status_from_results(results), "FAILED")

    def test_empty_results(self):
        self.assertEqual(_status_from_results([]), "FAILED")


class RunCaseErrorTest(unittest.IsolatedAsyncioTestCase):
    async def test_missing_case_returns_error_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            summary = await run_case(
                _config(tmp_path / "root"),
                str(tmp_path / "missing.json"),
                reports_dir=str(tmp_path / "reports"),
            )
            self.assertEqual(summary["status"], "ERROR")
            self.assertIn("error", summary)
            run_dir = Path(summary["run_dir"])
            self.assertIn("invalid-case", run_dir.name)
            self.assertTrue((run_dir / "assertions.json").exists())
            data = json.loads(
                (run_dir / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(data["status"], "ERROR")
            self.assertIn("error", data)

    async def test_invalid_json_case_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            case_path = tmp_path / "case.json"
            case_path.write_text("{not json", encoding="utf-8")
            summary = await run_case(
                _config(tmp_path / "root"),
                str(case_path),
                reports_dir=str(tmp_path / "reports"),
            )
            self.assertEqual(summary["status"], "ERROR")
            data = json.loads(
                (Path(summary["run_dir"]) / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(data["status"], "ERROR")

    async def test_uncreatable_reports_dir_returns_error_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            blocker = tmp_path / "not-a-dir"
            blocker.write_text("x", encoding="utf-8")
            summary = await run_case(
                _config(tmp_path / "root"),
                str(tmp_path / "missing.json"),
                reports_dir=str(blocker),
            )
            self.assertEqual(summary["status"], "ERROR")
            self.assertIsNone(summary["run_dir"])
            self.assertIn("error", summary)


class RunCaseHistoryFallbackTest(unittest.IsolatedAsyncioTestCase):
    @mock.patch("astrbot_e2e.runner.prepare_instance")
    @mock.patch("astrbot_e2e.runner.AstrBotInstance")
    @mock.patch("astrbot_e2e.runner.OneBotClient")
    @mock.patch("astrbot_e2e.runner.collect_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.history_bot_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.time.time", return_value=1234567890)
    async def test_history_fallback_uses_send_started_at(
        self, time_mock, history, collect, client_cls, instance_cls, prepare
    ):
        def make_client(user_id):
            client = mock.MagicMock()
            client.connect = mock.AsyncMock()
            client.close = mock.AsyncMock()

            async def call(action, params):
                if action == "get_login_info":
                    return {"user_id": user_id}
                if action == "send_group_msg":
                    return {"message_id": 7}
                raise AssertionError("unexpected action: {}".format(action))

            client.call = mock.AsyncMock(side_effect=call)
            return client

        bot_client = make_client("10001")
        sender_client = make_client("10002")
        client_cls.side_effect = [bot_client, sender_client]

        instance = mock.MagicMock()
        instance.is_running.return_value = False
        instance.start.return_value = mock.MagicMock(pid=4242)
        instance.wait_ready = mock.AsyncMock()
        instance.stop = mock.MagicMock()
        instance_cls.return_value = instance

        collect.return_value = []
        history.return_value = [{"text": "pong", "raw": {}}]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            case_path = tmp_path / "case.json"
            case_path.write_text(
                json.dumps(
                    {
                        "name": "history-fallback",
                        "plugin": "astrbot_plugin_e2e_probe",
                        "send": {"group_id": "123456789", "text": "ping"},
                        "expect": {"messages": [{"contains": ["pong"]}]},
                    }
                ),
                encoding="utf-8",
            )
            summary = await run_case(
                _config(tmp_path / "root"),
                str(case_path),
                reports_dir=str(tmp_path / "reports"),
            )

        self.assertEqual(summary["status"], "PASSED")
        collect.assert_awaited_once()
        history.assert_awaited_once()
        args, kwargs = history.await_args
        self.assertIs(args[0], sender_client)
        self.assertEqual(args[1], "10001")
        self.assertEqual(args[2], "123456789")
        self.assertEqual(kwargs.get("since_time"), 1234567890 - 1)
        prepare.assert_called_once()
        instance.stop.assert_called_once()
