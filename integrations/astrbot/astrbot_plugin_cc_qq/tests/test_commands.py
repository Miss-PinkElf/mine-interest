"""命令角色门禁、工作目录切换与基础模板的单元测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.commands.registry import command_allowed
from astrbot_plugin_cc_qq.commands.session import help_text
from astrbot_plugin_cc_qq.constants import CD_OUTSIDE_ROOTS_REPLY
from astrbot_plugin_cc_qq.contracts import (
    ConversationKey,
    ConversationKind,
    SessionSettings,
)
from astrbot_plugin_cc_qq.permissions import CRITICAL_PATH_DENY_RULES, resolve_path
from astrbot_plugin_cc_qq.service import ConversationService
from astrbot_plugin_cc_qq.sessions import SessionManager
from astrbot_plugin_cc_qq.storage import SessionStore


class CommandRoleTest(unittest.TestCase):
    def test_guest_can_only_use_help_and_info(self):
        self.assertTrue(command_allowed("guest", "/help"))
        self.assertTrue(command_allowed("guest", "/info"))
        self.assertFalse(command_allowed("guest", "/new"))
        self.assertFalse(command_allowed("guest", "/cd"))

    def test_member_cannot_use_admin_commands(self):
        self.assertTrue(command_allowed("member", "/new"))
        self.assertFalse(command_allowed("member", "/cd"))
        self.assertFalse(command_allowed("member", "/initbase"))
        self.assertFalse(command_allowed("member", "/approve"))

    def test_admin_can_use_admin_commands(self):
        for name in ("/cd", "/initbase", "/approve", "/deny"):
            self.assertTrue(command_allowed("admin", name), name)

    def test_help_text_is_filtered_by_role(self):
        guest_help = help_text("guest")
        admin_help = help_text("admin")
        self.assertIn("/help", guest_help)
        self.assertNotIn("/cd", guest_help)
        self.assertIn("/cd", admin_help)


class WorkDirCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "root"
        self.root.mkdir()
        self.inside = self.root / "project"
        self.inside.mkdir()
        self.outside = Path(self.temp.name) / "outside"
        self.outside.mkdir()
        self.store = SessionStore(Path(self.temp.name) / "data")
        self.config = {"allowed_work_dirs": [str(self.root)]}
        self.sessions = SessionManager(self.store, self.config)
        self.service = ConversationService(self.store, self.sessions, self.config)
        self.conversation = ConversationKey("p", ConversationKind.GROUP, "1")
        self.settings = SessionSettings(
            work_dir=str(self.root),
            agent_type="claude",
            role="admin",
            permission_profile="full",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_cd_inside_allowed_root_persists_override(self):
        result = self.service._change_work_dir(
            self.conversation, self.settings, str(self.inside)
        )
        self.assertIn("已切换", result)
        self.assertEqual(
            self.store.work_dir_override(self.conversation),
            str(resolve_path(self.inside)),
        )

    def test_cd_outside_allowed_root_is_rejected(self):
        result = self.service._change_work_dir(
            self.conversation, self.settings, str(self.outside)
        )
        self.assertEqual(result, CD_OUTSIDE_ROOTS_REPLY)
        self.assertEqual(self.store.work_dir_override(self.conversation), "")

    def test_cd_without_configured_roots_is_rejected(self):
        service = ConversationService(self.store, self.sessions, {})
        result = service._change_work_dir(
            self.conversation, self.settings, str(self.inside)
        )
        self.assertIn("allowed_work_dirs", result)


class InitBaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp.name) / "work"
        self.work_dir.mkdir()
        store = SessionStore(Path(self.temp.name) / "data")
        sessions = SessionManager(store, {})
        self.service = ConversationService(store, sessions, {})
        self.settings = SessionSettings(
            work_dir=str(self.work_dir),
            agent_type="claude",
            role="admin",
            permission_profile="full",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_initbase_copies_templates_then_skips(self):
        first = self.service._init_base(self.settings)
        self.assertIn("新建", first)
        self.assertTrue((self.work_dir / "CLAUDE.md").is_file())
        self.assertTrue((self.work_dir / "AGENTS.md").is_file())
        self.assertTrue(
            (self.work_dir / ".claude" / "skills" / "ccqq-basics" / "SKILL.md").is_file()
        )
        self.assertTrue((self.work_dir / ".codex" / "config.toml").is_file())
        settings_payload = json.loads(
            (self.work_dir / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            settings_payload["permissions"]["deny"], list(CRITICAL_PATH_DENY_RULES)
        )
        self.assertTrue(settings_payload["sandbox"]["enabled"])

        second = self.service._init_base(self.settings)
        self.assertIn("跳过", second)


if __name__ == "__main__":
    unittest.main()
