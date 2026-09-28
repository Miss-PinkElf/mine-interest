"""QQ 状态证据与断线宽限（QQ Status Tests）。"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from integrations.astrbot.astrbot_plugin_sourcehub_inspector.qq_status import QQDisconnectGrace, probe_qq_status
from sourcehub.alerts import DISCONNECTED, HEALTHY, UNKNOWN


class QQStatusTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_onebot_status(self):
        class API:
            async def call_action(self, action):
                self.action = action
                return {"status": "ok", "data": {"online": False, "good": False}}
        class Client:
            api = API()
        class Platform:
            def get_client(self):
                return Client()
        class Context:
            def get_platform_inst(self, platform_id):
                self.platform_id = platform_id
                return Platform()
        context = Context()
        self.assertEqual(await probe_qq_status(context, "aiocqhttp"), DISCONNECTED)
        self.assertEqual(context.platform_id, "aiocqhttp")

    async def test_missing_or_failed_signal_is_unknown(self):
        class Context:
            def get_platform_inst(self, _platform_id):
                return None
        self.assertEqual(await probe_qq_status(Context(), "qq"), UNKNOWN)
        self.assertEqual(await probe_qq_status(Context(), ""), UNKNOWN)

    async def test_grace_requires_continuous_disconnection(self):
        start = datetime(2026, 9, 28, tzinfo=timezone.utc)
        grace = QQDisconnectGrace(60)
        self.assertEqual(grace.observe(DISCONNECTED, start), UNKNOWN)
        self.assertEqual(grace.observe(DISCONNECTED, start + timedelta(seconds=59)), UNKNOWN)
        self.assertEqual(grace.observe(DISCONNECTED, start + timedelta(seconds=60)), DISCONNECTED)
        self.assertEqual(grace.observe(HEALTHY, start + timedelta(seconds=61)), HEALTHY)
        self.assertEqual(grace.observe(DISCONNECTED, start + timedelta(seconds=62)), UNKNOWN)


if __name__ == "__main__":
    unittest.main()
