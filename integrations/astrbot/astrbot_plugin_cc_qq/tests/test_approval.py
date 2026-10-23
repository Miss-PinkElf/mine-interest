"""审批服务与 PreToolUse hook 的单元测试。"""

import asyncio
import json
import logging
import os
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.approval import ApprovalBroker, approval_targets
from astrbot_plugin_cc_qq.storage import SessionStore

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = PLUGIN_ROOT / "hooks" / "approval_hook.py"
GUARD_HOOK_PATH = PLUGIN_ROOT / "hooks" / "guard_hook.py"
READONLY_HOOK_PATH = PLUGIN_ROOT / "hooks" / "readonly_hook.py"


def _payload(**overrides):
    payload = {
        "conversation_key": '["platform","group","1"]',
        "sender_id": "10001",
        "origin": "origin-1",
        "role": "member",
        "profile": "workspace",
        "tool_name": "Bash",
        "summary": "sudo rm -rf /tmp/x",
    }
    payload.update(overrides)
    return payload


class ApprovalTargetsTest(unittest.TestCase):
    def test_origin_first_then_unique_admin_origins(self):
        self.assertEqual(
            approval_targets("origin-a", ["origin-b", "origin-a", "", "origin-b"]),
            ["origin-a", "origin-b"],
        )
        self.assertEqual(approval_targets("", []), [])


class ApprovalBrokerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = SessionStore(Path(self.temp.name))
        self.logger = logging.getLogger("test-approval")
        self.messages = []

        async def notifier(origin, text):
            self.messages.append((origin, text))

        self.broker = ApprovalBroker(
            self.store,
            self.logger,
            {"danger_approval_enabled": True, "danger_approval_timeout_seconds": 300},
        )
        await self.broker.start(notifier)

    async def asyncTearDown(self):
        await self.broker.stop()
        self.temp.cleanup()

    async def test_approve_unblocks_hook_request(self):
        task = asyncio.create_task(self.broker.request(_payload()))
        await asyncio.sleep(0.05)
        self.assertEqual(self.broker.pending_count(), 1)
        self.assertEqual(len(self.messages), 1)
        approval_id = self.broker.pending_ids()[0]
        reply = self.broker.resolve(approval_id, True, "2844973553")
        approved, _ = await task
        self.assertTrue(approved)
        self.assertIn("已批准", reply)

    async def test_deny_unblocks_hook_request(self):
        task = asyncio.create_task(self.broker.request(_payload()))
        await asyncio.sleep(0.05)
        approval_id = self.broker.pending_ids()[0]
        self.broker.resolve(approval_id, False, "2844973553")
        approved, reason = await task
        self.assertFalse(approved)
        self.assertTrue(reason)

    async def test_timeout_defaults_to_deny(self):
        self.broker.timeout_seconds = 0.05
        approved, reason = await self.broker.request(_payload())
        self.assertFalse(approved)
        self.assertIn("超时", reason)
        events = self.store.recent_permission_events()
        self.assertTrue(any(event["decision"] == "timeout" for event in events))

    async def test_audit_records_approver(self):
        task = asyncio.create_task(self.broker.request(_payload()))
        await asyncio.sleep(0.05)
        approval_id = self.broker.pending_ids()[0]
        self.broker.resolve(approval_id, True, "2844973553")
        await task
        events = self.store.recent_permission_events()
        approved = [event for event in events if event["decision"] == "approved"]
        self.assertTrue(approved)
        self.assertEqual(approved[0]["approver_id"], "2844973553")


def _run_hook(event: dict, env: dict, script: Path = HOOK_PATH) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        env={**os.environ, **env},
        timeout=30,
    )


class ApprovalHookTest(unittest.TestCase):
    def _fake_broker(self, decision: str):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        received: list[dict] = []

        def serve():
            connection, _ = server.accept()
            line = connection.makefile("rb").readline()
            received.append(json.loads(line.decode("utf-8")))
            response = {"decision": decision, "reason": "test"}
            connection.sendall((json.dumps(response) + "\n").encode("utf-8"))
            connection.close()
            server.close()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        return port, received

    def _env(self, port: int) -> dict:
        return {
            "CC_QQ_APPROVAL_HOST": "127.0.0.1",
            "CC_QQ_APPROVAL_PORT": str(port),
            "CC_QQ_APPROVAL_TOKEN": "test-token",
            "CC_QQ_APPROVAL_TIMEOUT": "5",
            "CC_QQ_PERMISSION_PROFILE": "workspace",
            "CC_QQ_ROLE": "member",
            "CC_QQ_WORK_DIR": "/tmp/ccqq-hook",
            "CC_QQ_CONVERSATION_KEY": '["p","group","1"]',
            "CC_QQ_SENDER_ID": "10001",
            "CC_QQ_ORIGIN": "origin-1",
        }

    def test_dangerous_command_gets_allow_from_broker(self):
        port, received = self._fake_broker("allow")
        result = _run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}},
            self._env(port),
        )
        output = json.loads(result.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "allow"
        )
        self.assertEqual(received[0]["token"], "test-token")
        self.assertEqual(received[0]["tool_name"], "Bash")

    def test_dangerous_command_gets_deny_from_broker(self):
        port, _ = self._fake_broker("deny")
        result = _run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}},
            self._env(port),
        )
        output = json.loads(result.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def test_missing_broker_fails_closed(self):
        result = _run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}},
            {"CC_QQ_PERMISSION_PROFILE": "workspace", "CC_QQ_WORK_DIR": "/tmp/ccqq-hook"},
        )
        output = json.loads(result.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def test_safe_command_has_no_hook_output(self):
        result = _run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "ls -la"}},
            {"CC_QQ_PERMISSION_PROFILE": "workspace", "CC_QQ_WORK_DIR": "/tmp/ccqq-hook"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")


class ReadonlyHookTest(unittest.TestCase):
    ENV = {"CC_QQ_PERMISSION_PROFILE": "readonly", "CC_QQ_WORK_DIR": "/tmp/ccqq-readonly"}

    def _decision(self, event: dict) -> str:
        result = _run_hook(event, self.ENV, READONLY_HOOK_PATH)
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_allows_read_inside_workdir(self):
        self.assertEqual(
            self._decision(
                {"tool_name": "Read", "tool_input": {"file_path": "/tmp/ccqq-readonly/a.txt"}}
            ),
            "allow",
        )

    def test_denies_read_outside_workdir(self):
        for path in ("/etc/hosts", "~/.codex/auth.json", "/tmp/other/a.txt"):
            self.assertEqual(
                self._decision(
                    {"tool_name": "Read", "tool_input": {"file_path": path}}
                ),
                "deny",
                path,
            )

    def test_denies_write_and_bash(self):
        self.assertEqual(
            self._decision(
                {"tool_name": "Write", "tool_input": {"file_path": "/tmp/ccqq-readonly/a.txt"}}
            ),
            "deny",
        )
        self.assertEqual(
            self._decision(
                {"tool_name": "Bash", "tool_input": {"command": "ls"}}
            ),
            "deny",
        )


class GuardHookTest(unittest.TestCase):
    ENV = {"CC_QQ_PERMISSION_PROFILE": "full", "CC_QQ_WORK_DIR": "/tmp/ccqq-guard"}

    def _decision(self, event: dict) -> str:
        result = _run_hook(event, self.ENV, GUARD_HOOK_PATH)
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_allows_normal_write(self):
        self.assertEqual(
            self._decision(
                {"tool_name": "Write", "tool_input": {"file_path": "/tmp/ccqq-guard/ok.txt"}}
            ),
            "allow",
        )

    def test_denies_protected_paths(self):
        for path in ("~/.ssh/id_rsa", "/etc/passwd", "/System/x"):
            self.assertEqual(
                self._decision(
                    {"tool_name": "Write", "tool_input": {"file_path": path}}
                ),
                "deny",
                path,
            )

    def test_denies_critical_shell_commands(self):
        for command in ("sudo ls", "rm -rf /", "cat ~/.ssh/id_rsa"):
            self.assertEqual(
                self._decision(
                    {"tool_name": "Bash", "tool_input": {"command": command}}
                ),
                "deny",
                command,
            )

    def test_allows_normal_shell(self):
        self.assertEqual(
            self._decision({"tool_name": "Bash", "tool_input": {"command": "ls -la"}}),
            "allow",
        )


if __name__ == "__main__":
    unittest.main()
