"""QQ GitHub 自动化准入与回复测试（GitHub Gate Tests）。"""

from __future__ import annotations

import unittest

from integrations.astrbot.astrbot_plugin_sourcehub_inspector.github_gate import (
    compose_github_reply,
    is_github_authorized,
    message_plain_text,
)
from sourcehub.github_actions import ActionResult


class FakeEvent:
    def __init__(self, sender: str = "", admin: bool = False, text: str = ""):
        self.sender = sender
        self.admin = admin
        self.text = text

    def is_admin(self) -> bool:
        return self.admin

    def get_sender_id(self) -> str:
        return self.sender

    def get_message_str(self) -> str:
        return self.text


class GithubGateTests(unittest.TestCase):
    def test_astrbot_admin_is_authorized(self):
        event = FakeEvent(sender="999", admin=True)
        self.assertTrue(is_github_authorized(event, {}))

    def test_configured_owner_and_admin_ids_are_authorized(self):
        config = {
            "github_owner_qq_ids": ["1961618848"],
            "github_admin_qq_ids": ["2844973553"],
        }
        self.assertTrue(is_github_authorized(FakeEvent(sender="1961618848"), config))
        self.assertTrue(is_github_authorized(FakeEvent(sender="2844973553"), config))

    def test_member_is_not_authorized(self):
        config = {"github_owner_qq_ids": ["1961618848"]}
        self.assertFalse(is_github_authorized(FakeEvent(sender="123456"), config))
        self.assertFalse(is_github_authorized(FakeEvent(sender=""), config))

    def test_plain_text_and_reply(self):
        self.assertEqual(message_plain_text(FakeEvent(text="  /fork https://github.com/a/b ")),
                         "/fork https://github.com/a/b")
        reply = compose_github_reply(
            [
                ActionResult("a/b", "star", True, "已 star"),
                ActionResult("a/b", "fork", False, "无法连接 GitHub", via_proxy=True),
            ]
        )
        self.assertIn("[成功] a/b：已 star", reply)
        self.assertIn("[失败] a/b：无法连接 GitHub（经代理）", reply)


if __name__ == "__main__":
    unittest.main()
