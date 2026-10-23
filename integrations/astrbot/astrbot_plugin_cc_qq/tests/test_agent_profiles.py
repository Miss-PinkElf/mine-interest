"""代理参数与 Claude 策略文件的单元测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.agents.profiles import (
    build_claude_settings,
    claude_args,
    codex_args,
    ensure_claude_settings,
)
from astrbot_plugin_cc_qq.permissions import PROFILE_FULL, PROFILE_READONLY, PROFILE_WORKSPACE


class ClaudeArgsTest(unittest.TestCase):
    def test_readonly_uses_dont_ask_and_tool_allowlist(self):
        args = claude_args(PROFILE_READONLY, "", "", "session-id", "/tmp/policy.json", "")
        self.assertIn("dontAsk", args)
        self.assertIn("--tools", args)
        tools = args[args.index("--tools") + 1]
        self.assertIn("Read", tools)
        self.assertNotIn("Bash", tools)
        self.assertEqual(args[args.index("--setting-sources") + 1], "")

    def test_workspace_uses_accept_edits(self):
        args = claude_args(PROFILE_WORKSPACE, "model-x", "old-id", "new-id", "/tmp/p.json", "user")
        self.assertIn("acceptEdits", args)
        self.assertIn("--resume", args)
        self.assertIn("model-x", args)
        self.assertEqual(args[args.index("--setting-sources") + 1], "user")

    def test_full_uses_dont_ask_with_guard(self):
        args = claude_args(PROFILE_FULL, "", "", "new-id", "/tmp/guard.json", "")
        self.assertIn("dontAsk", args)
        self.assertNotIn("--tools", args)
        self.assertIn("--settings", args)


class CodexArgsTest(unittest.TestCase):
    def test_profiles_map_to_sandbox_modes(self):
        readonly = codex_args(PROFILE_READONLY, "", "", "/tmp/w")
        workspace = codex_args(PROFILE_WORKSPACE, "", "", "/tmp/w")
        full = codex_args(PROFILE_FULL, "", "", "/tmp/w")
        self.assertIn('default_permissions="ccqq-readonly"', readonly)
        self.assertIn('default_permissions="ccqq-workspace"', workspace)
        self.assertIn('sandbox_mode="danger-full-access"', full)
        self.assertIn('":workspace_roots"="read"', " ".join(readonly))
        self.assertIn('":workspace_roots"="write"', " ".join(workspace))
        self.assertIn("permissions.ccqq-workspace.network={enabled=false}", workspace)
        self.assertIn('approval_policy="never"', full)

    def test_resume_uses_thread_id_and_stdin(self):
        args = codex_args(PROFILE_WORKSPACE, "", "thread-1", "/tmp/w")
        self.assertIn("resume", args)
        self.assertIn("thread-1", args)
        self.assertEqual(args[-1], "-")


class ClaudeSettingsTest(unittest.TestCase):
    def test_workspace_settings_have_sandbox_and_hook(self):
        settings = build_claude_settings(
            PROFILE_WORKSPACE, Path("/tmp/hooks/approval_hook.py"), 300
        )
        self.assertTrue(settings["sandbox"]["enabled"])
        self.assertTrue(settings["sandbox"]["autoAllowBashIfSandboxed"])
        hook = settings["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertIn("approval_hook.py", hook["command"])
        self.assertEqual(hook["timeout"], 330)
        self.assertIn("deny", settings["permissions"])

    def test_readonly_installs_readonly_hook_without_sandbox(self):
        settings = build_claude_settings(PROFILE_READONLY, Path("/tmp/hooks/approval_hook.py"), 300)
        hook = settings["hooks"]["PreToolUse"][0]
        self.assertEqual(hook["matcher"], "")
        self.assertIn("readonly_hook.py", hook["hooks"][0]["command"])
        self.assertNotIn("sandbox", settings)

    def test_full_installs_guard_hook_without_sandbox(self):
        settings = build_claude_settings(PROFILE_FULL, Path("/tmp/hooks/approval_hook.py"), 300)
        hook = settings["hooks"]["PreToolUse"][0]
        self.assertEqual(hook["matcher"], "")
        self.assertIn("guard_hook.py", hook["hooks"][0]["command"])
        self.assertNotIn("sandbox", settings)

    def test_ensure_settings_writes_stable_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = ensure_claude_settings(
                Path(temp), PROFILE_FULL, Path("/tmp/hooks/approval_hook.py"), 300
            )
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertIn("permissions", payload)
            self.assertIn("hooks", payload)
            self.assertNotIn("token", Path(path).read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
