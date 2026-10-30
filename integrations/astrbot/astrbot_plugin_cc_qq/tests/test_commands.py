"""命令角色门禁、工作目录切换与基础模板的单元测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.commands.registry import command_allowed, will_run_agent
from astrbot_plugin_cc_qq.commands.session import help_text
from astrbot_plugin_cc_qq.constants import (
    CD_LIST_CURRENT_MARKER,
    CD_NOT_CONFIGURED_REPLY,
    CD_OUTSIDE_ROOTS_REPLY,
)
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

    def test_sync_commands_do_not_trigger_long_image(self):
        # /help 的回复可能超过 360 字，但它不是代理回复，必须保持文本。
        for name in ("/help", "/info", "/pwd", "/img", "/cd", "/approve"):
            self.assertFalse(will_run_agent((name, ""), "owner"), name)
        self.assertTrue(will_run_agent(None, "owner"))
        self.assertTrue(will_run_agent(("/cc", "hi"), "owner"))


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


class CdListCommandTest(unittest.TestCase):
    """`/cd list` 按配置顺序编号，`/cd <序号>` 复用同一份顺序。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.first = base / "mine-blog"
        self.second = base / "mine-interest"
        self.third = base / "person-config"
        for directory in (self.first, self.second, self.third):
            directory.mkdir()
        self.store = SessionStore(base / "data")
        self.config = {
            "allowed_work_dirs": [str(self.first), str(self.second), str(self.third)]
        }
        self.sessions = SessionManager(self.store, self.config)
        self.service = ConversationService(self.store, self.sessions, self.config)
        self.conversation = ConversationKey("p", ConversationKind.GROUP, "1")
        self.settings = SessionSettings(
            work_dir=str(self.first),
            agent_type="claude",
            role="admin",
            permission_profile="full",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_list_follows_configured_order(self):
        result = self.service._change_work_dir(self.conversation, self.settings, "list")
        self.assertIn(f"1. {resolve_path(self.first)}", result)
        self.assertIn(f"2. {resolve_path(self.second)}", result)
        self.assertIn(f"3. {resolve_path(self.third)}", result)
        self.assertLess(result.index("1. "), result.index("2. "))
        self.assertLess(result.index("2. "), result.index("3. "))

    def test_list_marks_current_work_dir(self):
        result = self.service._change_work_dir(self.conversation, self.settings, "list")
        current_line = next(
            line for line in result.splitlines() if str(resolve_path(self.first)) in line
        )
        self.assertIn(CD_LIST_CURRENT_MARKER, current_line)

    def test_list_keyword_is_case_insensitive(self):
        result = self.service._change_work_dir(self.conversation, self.settings, "LIST")
        self.assertIn("1. ", result)

    def test_index_switches_to_matching_root(self):
        result = self.service._change_work_dir(self.conversation, self.settings, "2")
        self.assertIn("已切换", result)
        self.assertEqual(
            self.store.work_dir_override(self.conversation),
            str(resolve_path(self.second)),
        )

    def test_index_out_of_range_is_rejected(self):
        for argument in ("0", "4", "99"):
            result = self.service._change_work_dir(
                self.conversation, self.settings, argument
            )
            self.assertIn("1-3", result)
            self.assertEqual(self.store.work_dir_override(self.conversation), "")

    def test_list_without_configured_roots_is_rejected(self):
        service = ConversationService(self.store, self.sessions, {})
        result = service._change_work_dir(self.conversation, self.settings, "list")
        self.assertEqual(result, CD_NOT_CONFIGURED_REPLY)

    def test_path_argument_still_works(self):
        result = self.service._change_work_dir(
            self.conversation, self.settings, str(self.third)
        )
        self.assertIn("已切换", result)
        self.assertEqual(
            self.store.work_dir_override(self.conversation),
            str(resolve_path(self.third)),
        )


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


class ImageCommandTest(unittest.TestCase):
    """`/img on|off` 只对 owner／管理员开放，状态按会话保存。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = SessionStore(Path(self.temp.name) / "data")
        self.config = {}
        self.sessions = SessionManager(self.store, self.config)
        self.service = ConversationService(self.store, self.sessions, self.config)
        self.conversation = ConversationKey("p", ConversationKind.GROUP, "img")

    def tearDown(self):
        self.temp.cleanup()

    def test_only_admin_can_use_img(self):
        self.assertTrue(command_allowed("admin", "/img"))
        self.assertTrue(command_allowed("owner", "/img"))
        self.assertFalse(command_allowed("member", "/img"))
        self.assertFalse(command_allowed("guest", "/img"))

    def test_status_defaults_to_enabled(self):
        result = self.service._toggle_image(self.conversation, "")
        self.assertIn("开启", result)
        self.assertIn("360", result)

    def test_off_persists_per_conversation(self):
        result = self.service._toggle_image(self.conversation, "off")
        self.assertIn("关闭", result)
        self.assertFalse(self.service.image_enabled(self.conversation))
        self.assertEqual(
            self.store.get_flag(self.conversation, "image_enabled"), "0"
        )

    def test_global_disable_is_respected_without_override(self):
        service = ConversationService(
            self.store, self.sessions, {"long_text_image_enabled": False}
        )
        self.assertFalse(service.image_enabled(self.conversation))

    def test_null_global_value_uses_default_enabled(self):
        service = ConversationService(
            self.store, self.sessions, {"long_text_image_enabled": None}
        )
        self.assertTrue(service.image_enabled(self.conversation))

    def test_invalid_argument_returns_usage(self):
        result = self.service._toggle_image(self.conversation, "maybe")
        self.assertIn("用法", result)


if __name__ == "__main__":
    unittest.main()
