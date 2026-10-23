"""B 站 GitHub 触发与登录状态展示测试。"""

from __future__ import annotations

import unittest

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.login_view import login_validity
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.poller import trigger_message
from sourcehub.alerts import HEALTHY, LOGIN_REQUIRED, UNKNOWN


class BilibiliGithubHookTests(unittest.TestCase):
    def test_trigger_message_prefers_expanded_comment(self):
        notification = {"item": {"source_content": "@bot /fork"}}
        raw = {"comments": {"trigger": {"content": {"message": "看看 /fork https://github.com/a/b"}}}}
        self.assertEqual(trigger_message(notification, raw), "看看 /fork https://github.com/a/b")

    def test_trigger_message_falls_back_to_source_content(self):
        notification = {"item": {"source_content": "@bot /fork"}}
        self.assertEqual(trigger_message(notification, {}), "@bot /fork")
        self.assertEqual(trigger_message({}, {}), "")


class BilibiliLoginValidityTests(unittest.TestCase):
    def test_healthy_cookie_is_valid(self):
        view = login_validity(HEALTHY, "2026-10-23T11:00:00+08:00")
        self.assertTrue(view["valid"])
        self.assertEqual(view["status"], HEALTHY)
        self.assertIn("有效", view["message"])

    def test_expired_cookie_is_invalid_and_mentions_rescan(self):
        view = login_validity(LOGIN_REQUIRED, "2026-10-23T11:00:00+08:00")
        self.assertFalse(view["valid"])
        self.assertIn("失效", view["message"])
        self.assertIn("扫码", view["message"])

    def test_unknown_network_is_not_reported_as_expired(self):
        view = login_validity(UNKNOWN, "2026-10-23T11:00:00+08:00")
        self.assertIsNone(view["valid"])
        self.assertNotIn("失效", view["message"])

    def test_missing_credentials_are_invalid(self):
        view = login_validity("missing", "2026-10-23T11:00:00+08:00")
        self.assertFalse(view["valid"])
        self.assertIn("还没有登录凭证", view["message"])

    def test_unrecognized_status_falls_back_to_unknown(self):
        view = login_validity("something-new", "2026-10-23T11:00:00+08:00")
        self.assertEqual(view["status"], UNKNOWN)
        self.assertIsNone(view["valid"])


if __name__ == "__main__":
    unittest.main()
