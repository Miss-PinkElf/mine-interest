"""QQ 准入策略的单元测试。"""

import unittest

from astrbot_plugin_cc_qq.constants import (
    REASON_NOT_ALLOWED,
    REASON_OUT_OF_SCOPE,
)
from astrbot_plugin_cc_qq.contracts import ConversationKey, ConversationKind, IncomingMessage
from astrbot_plugin_cc_qq.policy import authorize


def _message(kind: ConversationKind, sender_id: str, *, mentions_bot: bool = False) -> IncomingMessage:
    conversation_id = sender_id if kind is ConversationKind.PRIVATE else "836229427"
    return IncomingMessage(
        conversation=ConversationKey("Test-01", kind, conversation_id),
        sender_id=sender_id,
        sender_name=sender_id,
        message_id="1",
        text="hi",
        origin="origin",
        mentions_bot=mentions_bot,
    )


PRIVATE_CONFIG = {
    "qq_platform_id": "Test-01",
    "private_enabled": True,
    "private_user_ids": ["1968401530"],
    "private_work_dir": "/tmp/cc-qq-private",
    "admin_qq_ids": ["2844973553"],
    "enabled_group_ids": ["836229427"],
    "group_rules_json": {
        "836229427": {
            "work_dir": "/tmp/cc-qq-group",
            "agent": "codex",
            "allowed_user_ids": ["2844973553"],
        }
    },
}


class PrivateAdmissionTest(unittest.TestCase):
    def test_whitelisted_private_is_allowed(self):
        decision = authorize(_message(ConversationKind.PRIVATE, "1968401530"), PRIVATE_CONFIG)
        self.assertTrue(decision.allowed)

    def test_non_whitelisted_private_is_silent_out_of_scope(self):
        decision = authorize(_message(ConversationKind.PRIVATE, "10001"), PRIVATE_CONFIG)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, REASON_OUT_OF_SCOPE)

    def test_disabled_private_is_out_of_scope(self):
        config = dict(PRIVATE_CONFIG)
        config["private_enabled"] = False
        decision = authorize(_message(ConversationKind.PRIVATE, "1968401530"), config)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, REASON_OUT_OF_SCOPE)

    def test_admin_private_without_whitelist_is_allowed(self):
        config = dict(PRIVATE_CONFIG)
        config["private_user_ids"] = []
        decision = authorize(_message(ConversationKind.PRIVATE, "2844973553"), config)
        self.assertTrue(decision.allowed)

    def test_group_non_whitelist_still_not_allowed(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "10001", mentions_bot=True),
            PRIVATE_CONFIG,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, REASON_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
