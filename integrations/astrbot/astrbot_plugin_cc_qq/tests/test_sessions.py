"""会话执行时的权限档位与环境注入测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.constants import (
    AGENT_ENV_ORIGIN,
    AGENT_ENV_PROFILE,
    AGENT_ENV_SENDER_ID,
)
from astrbot_plugin_cc_qq.contracts import (
    AgentEvent,
    AgentEventKind,
    ConversationKey,
    ConversationKind,
    SessionSettings,
)
from astrbot_plugin_cc_qq.sessions import SessionManager
from astrbot_plugin_cc_qq.storage import SessionStore


class _RecordingAdapter:
    agent_type = "claude"

    def __init__(self):
        self.request = None

    async def execute(self, request):
        self.request = request
        yield AgentEvent(AgentEventKind.DONE, "ok")


class SessionPermissionTest(unittest.IsolatedAsyncioTestCase):
    async def test_workspace_profile_propagates_to_agent_request(self):
        with tempfile.TemporaryDirectory() as temp:
            store = SessionStore(Path(temp) / "data")
            sessions = SessionManager(store, {}, data_dir=Path(temp) / "data")
            adapter = _RecordingAdapter()
            sessions.adapters["claude"] = adapter
            sessions.set_approval_env(
                {"CC_QQ_APPROVAL_HOST": "127.0.0.1", "CC_QQ_APPROVAL_PORT": "1234"}
            )
            conversation = ConversationKey("p", ConversationKind.GROUP, "1")
            settings = SessionSettings(
                work_dir=temp,
                agent_type="claude",
                role="member",
                permission_profile="workspace",
                sender_id="10001",
                origin="origin-1",
            )

            reply = await sessions.run(conversation, settings, "hi", "m1")

            self.assertEqual(reply, "ok")
            request = adapter.request
            self.assertEqual(request.permission_profile, "workspace")
            self.assertEqual(request.process_env[AGENT_ENV_PROFILE], "workspace")
            self.assertEqual(request.process_env[AGENT_ENV_SENDER_ID], "10001")
            self.assertEqual(request.process_env[AGENT_ENV_ORIGIN], "origin-1")
            self.assertEqual(request.process_env["CC_QQ_APPROVAL_PORT"], "1234")
            payload = json.loads(
                Path(request.claude_settings_path).read_text(encoding="utf-8")
            )
            self.assertTrue(payload["sandbox"]["enabled"])
            self.assertIn("hooks", payload)


if __name__ == "__main__":
    unittest.main()
