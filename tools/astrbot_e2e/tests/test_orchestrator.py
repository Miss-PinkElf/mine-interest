import asyncio
import socket
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from astrbot_e2e.orchestrator import (
    AstrBotInstance,
    _wait_ports_free,
    pid_is_astrbot,
    port_open,
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class FakeBotClient:
    async def call(self, action, params):
        return {"user_id": "10001"}


class OrchestratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        self.root.mkdir()
        (self.root / ".astrbot").write_text("", encoding="utf-8")
        self.fake = Path(self.tmp.name) / "fake_astrbot"
        # 保留脚本名在 ps 中，避免 exec 后进程名变为 sleep，导致无法识别属主。
        self.fake.write_text(
            "#!/bin/sh\nwhile true; do sleep 0.2; done\n", encoding="utf-8"
        )
        self.fake.chmod(0o755)
        self.cfg = {
            "test_root": str(self.root),
            "webui": {"port": _free_port()},
            "astrbot": {
                "command": str(self.fake),
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": _free_port(),
            },
        }

    def test_start_writes_pid_and_stop_terminates(self):
        instance = AstrBotInstance(self.cfg, Path(self.tmp.name))
        instance.start()
        pid_file = self.root / "astrbot-e2e.pid"
        self.assertTrue(pid_file.exists())
        pid = int(pid_file.read_text(encoding="utf-8"))
        self.assertTrue(pid_is_astrbot(pid))
        instance.stop()
        self.assertFalse(pid_file.exists())

    def test_port_open_detects_closed_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        self.assertFalse(port_open("127.0.0.1", port, timeout=0.1))

    def test_start_waits_for_ports_to_be_released(self):
        instance = AstrBotInstance(self.cfg, Path(self.tmp.name))
        with mock.patch(
            "astrbot_e2e.orchestrator.port_open",
            side_effect=[True, True, False, False],
        ):
            instance.start()
        self.addCleanup(instance.stop)
        self.assertIsNotNone(instance.proc)

    def test_wait_ports_free_polls_until_released(self):
        responses = iter([True, False])
        started = time.monotonic()
        busy = _wait_ports_free(
            [("127.0.0.1", 1)],
            timeout=5.0,
            interval=0.05,
            probe=lambda host, port: next(responses),
        )
        self.assertEqual(busy, [])
        self.assertGreaterEqual(time.monotonic() - started, 0.05)

    def test_wait_ports_free_reports_busy_after_timeout(self):
        busy = _wait_ports_free(
            [("127.0.0.1", 1)], timeout=0.0, probe=lambda host, port: True
        )
        self.assertEqual(busy, [("127.0.0.1", 1)])


class PortEndpointsTest(unittest.TestCase):
    def test_exposes_port_endpoints(self):
        cfg = {
            "test_root": "/tmp/test-root",
            "webui": {"host": "127.0.0.1", "port": 6186},
            "astrbot": {"reverse_ws_host": "127.0.0.1", "reverse_ws_port": 6198},
        }
        instance = AstrBotInstance(cfg, Path("/tmp/run"))
        endpoints = instance.port_endpoints()
        self.assertEqual(
            [(label, port) for label, _, port in endpoints],
            [("WebUI", 6186), ("OneBot 反向 WS", 6198)],
        )


class WaitReadyLogMarkTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        self.root.mkdir()
        (self.root / ".astrbot").write_text("", encoding="utf-8")
        self.fake = Path(self.tmp.name) / "fake_astrbot"
        self.fake.write_text(
            "#!/bin/sh\nwhile true; do sleep 0.2; done\n", encoding="utf-8"
        )
        self.fake.chmod(0o755)
        self.cfg = {
            "test_root": str(self.root),
            "webui": {"port": _free_port()},
            "astrbot": {
                "command": str(self.fake),
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": _free_port(),
            },
            "bot": {"qq": "10001"},
        }
        self.instance = AstrBotInstance(self.cfg, Path(self.tmp.name))
        await asyncio.to_thread(self.instance.start)
        self.addAsyncCleanup(self._stop_instance)

    async def _stop_instance(self):
        await asyncio.to_thread(self.instance.stop)

    async def test_wait_ready_reuses_start_log_mark(self):
        log_path = self.root / "data" / "logs" / "astrbot.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("适配器已连接\n")
        with mock.patch("astrbot_e2e.orchestrator.port_open", return_value=True):
            await self.instance.wait_ready(FakeBotClient(), timeout=2.0)
            await self.instance.wait_ready(FakeBotClient(), timeout=2.0)
