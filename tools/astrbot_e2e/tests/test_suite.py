import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from astrbot_e2e.suite import run_suite


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


def _write_case(path: Path, name: str, text: str) -> None:
    path.write_text(
        json.dumps(
            {
                "name": name,
                "plugin": "astrbot_plugin_e2e_probe",
                "send": {"group_id": "{{group_id}}", "text": text},
                "expect": {"messages": [{"contains": ["ok"]}]},
            }
        ),
        encoding="utf-8",
    )


class RunSuiteTest(unittest.IsolatedAsyncioTestCase):
    @mock.patch("astrbot_e2e.suite.prepare_instance")
    @mock.patch("astrbot_e2e.suite.AstrBotInstance")
    @mock.patch("astrbot_e2e.suite.OneBotClient")
    @mock.patch("astrbot_e2e.suite.execute_case", new_callable=mock.AsyncMock)
    async def test_runs_all_cases_with_one_instance(
        self, execute, client_cls, instance_cls, prepare
    ):
        execute.return_value = (
            [mock.MagicMock(kind="x", ok=True, expected="", actual="", detail="")],
            [{"step": 1, "status": "PASSED", "results": []}],
        )

        def make_client(user_id):
            client = mock.MagicMock()
            client.connect = mock.AsyncMock()
            client.close = mock.AsyncMock()

            async def call(action, params):
                if action == "get_login_info":
                    return {"user_id": user_id}
                raise AssertionError("unexpected action: {}".format(action))

            client.call = mock.AsyncMock(side_effect=call)
            return client

        client_cls.side_effect = [make_client("10001"), make_client("10002")]
        instance = mock.MagicMock()
        instance.is_running.return_value = False
        instance.start.return_value = mock.MagicMock(pid=4242)
        instance.wait_ready = mock.AsyncMock()
        instance.stop = mock.MagicMock()
        instance_cls.return_value = instance

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_dir = tmp_path / "cases"
            cases_dir.mkdir()
            _write_case(cases_dir / "01.json", "case-1", "/help")
            _write_case(cases_dir / "02.json", "case-2", "/info")
            suite = await run_suite(
                _config(tmp_path / "root"),
                [str(cases_dir / "01.json"), str(cases_dir / "02.json")],
                reports_dir=str(tmp_path / "reports"),
            )
            # 临时目录在 with 块结束时清理，文件断言必须在此之前完成。
            self.assertTrue((Path(suite["suite_dir"]) / "report.json").exists())
            self.assertTrue((Path(suite["suite_dir"]) / "report.md").exists())

        self.assertEqual(suite["status"], "PASSED")
        self.assertEqual(len(suite["cases"]), 2)
        self.assertEqual(execute.await_count, 2)
        instance.start.assert_called_once()
        instance.stop.assert_called_once()
        prepare.assert_called_once()

    async def test_rejects_mixed_plugins(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            first = tmp_path / "01.json"
            second = tmp_path / "02.json"
            _write_case(first, "case-1", "/help")
            second.write_text(
                json.dumps(
                    {
                        "name": "case-2",
                        "plugin": "other_plugin",
                        "send": {"group_id": "{{group_id}}", "text": "/info"},
                        "expect": {"messages": [{"contains": ["ok"]}]},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "同一插件"):
                await run_suite(
                    _config(tmp_path / "root"),
                    [str(first), str(second)],
                    reports_dir=str(tmp_path / "reports"),
                )
