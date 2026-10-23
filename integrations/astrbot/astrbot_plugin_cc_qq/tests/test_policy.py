"""QQ 准入策略与每轮权限档位的单元测试。"""

import unittest

from astrbot_plugin_cc_qq.constants import REASON_OUT_OF_SCOPE
from astrbot_plugin_cc_qq.contracts import ConversationKey, ConversationKind, IncomingMessage
from astrbot_plugin_cc_qq.permissions import (
    PROFILE_FULL,
    PROFILE_READONLY,
    PROFILE_WORKSPACE,
    resolve_path,
)
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
    "owner_qq_id": "10000",
    "enabled_group_ids": ["836229427"],
    "allowed_work_dirs": ["/tmp/cc-qq-allowed"],
    "group_rules_json": {
        "836229427": {
            "work_dir": "/tmp/cc-qq-group",
            "agent": "codex",
            "allowed_user_ids": ["2844973553", "1968401530"],
        }
    },
}


class PrivateAdmissionTest(unittest.TestCase):
    def test_whitelisted_private_is_allowed(self):
        decision = authorize(_message(ConversationKind.PRIVATE, "1968401530"), PRIVATE_CONFIG)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.settings.permission_profile, PROFILE_WORKSPACE)

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
        self.assertEqual(decision.role, "admin")
        self.assertEqual(decision.settings.permission_profile, PROFILE_FULL)


class GroupAdmissionTest(unittest.TestCase):
    def test_group_non_whitelist_is_readonly_guest(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "10001", mentions_bot=True),
            PRIVATE_CONFIG,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.role, "guest")
        self.assertEqual(decision.settings.permission_profile, PROFILE_READONLY)

    def test_group_whitelist_is_workspace_member(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "1968401530", mentions_bot=True),
            PRIVATE_CONFIG,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.role, "member")
        self.assertEqual(decision.settings.permission_profile, PROFILE_WORKSPACE)

    def test_group_admin_is_full(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "2844973553", mentions_bot=True),
            PRIVATE_CONFIG,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.role, "admin")
        self.assertEqual(decision.settings.permission_profile, PROFILE_FULL)

    def test_group_rule_can_override_guest_profile(self):
        config = dict(PRIVATE_CONFIG)
        config["group_rules_json"] = {
            "836229427": {
                "work_dir": "/tmp/cc-qq-group",
                "allowed_user_ids": ["2844973553"],
                "guest_permission_profile": "workspace",
            }
        }
        decision = authorize(
            _message(ConversationKind.GROUP, "10001", mentions_bot=True), config
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.settings.permission_profile, PROFILE_WORKSPACE)

    def test_work_dir_override_inside_allowed_root(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "2844973553", mentions_bot=True),
            PRIVATE_CONFIG,
            work_dir_override="/tmp/cc-qq-allowed/project",
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(
            decision.settings.work_dir,
            str(resolve_path("/tmp/cc-qq-allowed/project")),
        )

    def test_work_dir_override_outside_allowed_root_is_ignored(self):
        decision = authorize(
            _message(ConversationKind.GROUP, "2844973553", mentions_bot=True),
            PRIVATE_CONFIG,
            work_dir_override="/etc",
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.settings.work_dir, "/tmp/cc-qq-group")


if __name__ == "__main__":
    unittest.main()
