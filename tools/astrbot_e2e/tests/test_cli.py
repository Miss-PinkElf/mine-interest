import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from astrbot_e2e.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / "config.local.json"
        self.config.write_text(json.dumps({
            "test_root": str(Path(self.tmp.name) / "root"),
            "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "pass"},
            "astrbot": {
                "command": "astrbot",
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": 6198,
                "reverse_ws_token": "token",
                "plugins": ["astrbot_plugin_e2e_probe"],
                "startup_timeout_seconds": 120,
            },
            "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "t"},
            "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "t"},
            "group_id": "123456789",
            "judge": {},
            "timeouts": {"message_seconds": 60, "reload_seconds": 120, "log_window_padding_seconds": 5},
        }), encoding="utf-8")

    def test_missing_config_returns_2(self):
        code = main(["doctor", "--config", str(Path(self.tmp.name) / "missing.json")])
        self.assertEqual(code, 2)

    @mock.patch("astrbot_e2e.cli._doctor", new_callable=mock.AsyncMock)
    def test_doctor_dispatches(self, doctor):
        doctor.return_value = 0
        code = main(["doctor", "--config", str(self.config)])
        self.assertEqual(code, 0)
        doctor.assert_called_once()
        cfg = doctor.call_args.args[0]
        self.assertEqual(cfg["bot"]["qq"], "10001")
        self.assertEqual(cfg["sender"]["qq"], "10002")
        self.assertEqual(
            cfg["test_root"], str((Path(self.tmp.name) / "root").resolve())
        )
