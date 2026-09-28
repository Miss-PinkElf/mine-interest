"""B 站登录分类（Bilibili Auth Tests）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.auth import AuthError, BilibiliAuth, CredentialStore
from sourcehub.alerts import HEALTHY, LOGIN_REQUIRED, UNKNOWN


class BilibiliAuthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CredentialStore(Path(self.temp.name) / "credentials.json")
        self.auth = BilibiliAuth(self.store)
        self.credentials = {"SESSDATA": "private-cookie", "bili_jct": "csrf", "refresh_token": "old-token"}

    async def test_network_error_is_unknown(self):
        async def failed(*_args, **_kwargs):
            raise AuthError("DNS")
        self.auth._request = failed
        self.assertEqual(await self.auth.check(self.credentials), UNKNOWN)
        self.assertFalse(self.store.path.exists())

    async def test_explicit_invalid_cookie_requires_login(self):
        async def invalid(*_args, **_kwargs):
            return {"code": -101}, {}
        self.auth._request = invalid
        self.assertEqual(await self.auth.check(self.credentials), LOGIN_REQUIRED)

    async def test_success_response_without_login_flag_is_unknown(self):
        async def malformed(*_args, **_kwargs):
            return {"code": 0, "data": {}}, {}
        self.auth._request = malformed
        self.assertEqual(await self.auth.check(self.credentials), UNKNOWN)

    async def test_refresh_only_persists_complete_new_credentials(self):
        async def needs_refresh(*_args, **_kwargs):
            return {"code": 0, "data": {"refresh": True}}, {}
        async def refreshed(_credentials):
            return {**self.credentials, "SESSDATA": "new-cookie", "refresh_token": "new-token"}
        self.auth._request = needs_refresh
        self.auth._refresh = refreshed
        status, updated = await self.auth.refresh_if_needed(self.credentials)
        self.assertEqual(status, HEALTHY)
        self.assertEqual(updated["SESSDATA"], "new-cookie")
        self.assertEqual(self.store.load()["refresh_token"], "new-token")

    async def test_missing_refresh_token_keeps_valid_cookie(self):
        async def needs_refresh(*_args, **_kwargs):
            return {"code": 0, "data": {"refresh": True}}, {}
        self.auth._request = needs_refresh
        status, unchanged = await self.auth.refresh_if_needed({"SESSDATA": "old", "bili_jct": "csrf"})
        self.assertEqual(status, UNKNOWN)
        self.assertEqual(unchanged["SESSDATA"], "old")
        self.assertFalse(self.store.path.exists())

    async def test_qr_success_saves_own_credentials(self):
        async def qr_poll(*_args, **_kwargs):
            return {"data": {"code": 0, "url": "https://passport.bilibili.com/?SESSDATA=from-qr&bili_jct=csrf&DedeUserID=123456", "refresh_token": "new-token"}}, {}
        self.auth._request = qr_poll
        self.assertEqual(await self.auth.poll_qr("temporary-key"), "success")
        credentials = self.store.load()
        self.assertEqual(credentials["SESSDATA"], "from-qr")
        self.assertEqual(credentials["account_id"], "123456")
        self.assertEqual(credentials["refresh_token"], "new-token")


if __name__ == "__main__":
    unittest.main()
