"""执行回执与 `/goon` 取消可观测性的单元测试。"""

import tempfile
import unittest
from pathlib import Path

from astrbot_plugin_cc_qq.commands.registry import parse_command, will_run_agent
from astrbot_plugin_cc_qq.constants import (
    AGENT_INTERRUPTED_REPLY,
    CC_USAGE_REPLY,
    GOON_INTERRUPTED_PREFIX,
    NO_ACTIVE_SESSION_REPLY,
    NO_COMMAND_PERMISSION_REPLY,
)
from astrbot_plugin_cc_qq.contracts import (
    AgentEvent,
    AgentEventKind,
    AuthorizationDecision,
    ConversationKey,
    ConversationKind,
    IncomingMessage,
    SessionSettings,
)
from astrbot_plugin_cc_qq.service import ConversationService
from astrbot_plugin_cc_qq.sessions import SessionManager
from astrbot_plugin_cc_qq.storage import SessionStore


class _DoneAdapter:
    """立即返回固定文本的代理替身。"""

    agent_type = "claude"

    def __init__(self, text: str = "ok"):
        self.text = text

    async def execute(self, request):
        yield AgentEvent(AgentEventKind.DONE, self.text)


class WillRunAgentTest(unittest.TestCase):
    def test_plain_text_runs_agent(self):
        self.assertTrue(will_run_agent(parse_command("今天天气怎么样")))

    def test_agent_starting_commands(self):
        for text in ("/goon", "/cc 你好", "/new 初始消息", "/! 重跑"):
            self.assertTrue(will_run_agent(parse_command(text)), text)

    def test_commands_without_agent(self):
        for text in (
            "/help",
            "/info",
            "/pwd",
            "/cd list",
            "/cd 2",
            "/end",
            "/resume",
            "/initbase",
            "/approve 1",
            "/deny 1",
            "/new",
            "/!",
            "/cc",
        ):
            self.assertFalse(will_run_agent(parse_command(text)), text)

    def test_cc_without_argument_does_not_run_agent(self):
        self.assertFalse(will_run_agent(parse_command("/cc"), "owner"))

    def test_guest_cannot_trigger_agent_commands(self):
        for text in ("/goon", "/cc 你好", "/new 初始消息", "/! 重跑"):
            self.assertFalse(will_run_agent(parse_command(text), "guest"), text)

    def test_member_can_trigger_agent_commands(self):
        for text in ("/goon", "/cc 你好", "/new 初始消息", "/! 重跑"):
            self.assertTrue(will_run_agent(parse_command(text), "member"), text)

    def test_guest_plain_text_runs_agent(self):
        self.assertTrue(will_run_agent(None, "guest"))


class GoonCancellationTest(unittest.IsolatedAsyncioTestCase):
    def _build(self, temp: str):
        store = SessionStore(Path(temp) / "data")
        sessions = SessionManager(store, {}, data_dir=Path(temp) / "data")
        return store, sessions

    def _settings(self, temp: str) -> SessionSettings:
        return SessionSettings(
            work_dir=temp,
            agent_type="claude",
            role="owner",
            permission_profile="full",
            sender_id="1961618848",
            origin="origin-1",
        )

    async def test_cancelled_execution_returns_explicit_reply(self):
        """_execute 返回 None 时不能返回空串，否则会被判成 done 且不发送。"""
        with tempfile.TemporaryDirectory() as temp:
            store, sessions = self._build(temp)
            conversation = ConversationKey("p", ConversationKind.PRIVATE, "1961618848")
            record = store.create(conversation, self._settings(temp))
            store.set_agent_session_id(record.id, "session-1")

            async def cancelled(*args, **kwargs):
                return None

            sessions._execute = cancelled  # type: ignore[method-assign]

            reply = await sessions.goon(
                conversation, self._settings(temp), "继续", "m1"
            )

            self.assertEqual(reply, AGENT_INTERRUPTED_REPLY)
            self.assertTrue(reply)

    async def test_interrupted_prefix_when_previous_task_bumped(self):
        with tempfile.TemporaryDirectory() as temp:
            store, sessions = self._build(temp)
            conversation = ConversationKey("p", ConversationKind.PRIVATE, "1961618848")
            record = store.create(conversation, self._settings(temp))
            store.set_agent_session_id(record.id, "session-1")

            async def interrupted(conv):
                return True

            async def completed(*args, **kwargs):
                return "结果是 42"

            sessions.interrupt = interrupted  # type: ignore[method-assign]
            sessions._execute = completed  # type: ignore[method-assign]

            reply = await sessions.goon(
                conversation, self._settings(temp), "继续", "m1"
            )

            self.assertEqual(reply, f"{GOON_INTERRUPTED_PREFIX}结果是 42")

    async def test_no_prefix_when_nothing_was_running(self):
        with tempfile.TemporaryDirectory() as temp:
            store, sessions = self._build(temp)
            conversation = ConversationKey("p", ConversationKind.PRIVATE, "1961618848")
            record = store.create(conversation, self._settings(temp))
            store.set_agent_session_id(record.id, "session-1")

            async def interrupted(conv):
                return False

            async def completed(*args, **kwargs):
                return "结果是 42"

            sessions.interrupt = interrupted  # type: ignore[method-assign]
            sessions._execute = completed  # type: ignore[method-assign]

            reply = await sessions.goon(
                conversation, self._settings(temp), "继续", "m1"
            )

            self.assertEqual(reply, "结果是 42")


class ExecutionStartedCallbackTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = SessionStore(Path(self.temp.name) / "data")
        self.sessions = SessionManager(
            self.store, {}, data_dir=Path(self.temp.name) / "data"
        )
        self.sessions.adapters["claude"] = _DoneAdapter()
        self.service = ConversationService(self.store, self.sessions, {})
        self.conversation = ConversationKey("p", ConversationKind.PRIVATE, "1961618848")
        self.decision = AuthorizationDecision(
            allowed=True,
            role="owner",
            settings=SessionSettings(
                work_dir=self.temp.name,
                agent_type="claude",
                role="owner",
                permission_profile="full",
                sender_id="1961618848",
                origin="origin-1",
            ),
        )
        self.started = 0

    def tearDown(self):
        self.temp.cleanup()

    async def _on_started(self):
        self.started += 1

    def _message(self, text: str, message_id: str) -> IncomingMessage:
        return IncomingMessage(
            conversation=self.conversation,
            sender_id="1961618848",
            sender_name="owner",
            message_id=message_id,
            text=text,
            origin="origin-1",
        )

    def _guest_decision(self) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            role="guest",
            settings=SessionSettings(
                work_dir=self.temp.name,
                agent_type="claude",
                role="guest",
                permission_profile="readonly",
                sender_id="1961618848",
                origin="origin-1",
            ),
        )

    async def test_plain_text_triggers_callback(self):
        await self.service.handle(
            self._message("你好", "m1"), self.decision, on_started=self._on_started
        )
        self.assertEqual(self.started, 1)

    async def test_goon_triggers_callback(self):
        record = self.store.create(self.conversation, self.decision.settings)
        self.store.set_agent_session_id(record.id, "session-1")
        await self.service.handle(
            self._message("/goon", "m1"), self.decision, on_started=self._on_started
        )
        self.assertEqual(self.started, 1)

    async def test_sync_command_does_not_trigger_callback(self):
        await self.service.handle(
            self._message("/help", "m1"), self.decision, on_started=self._on_started
        )
        self.assertEqual(self.started, 0)

    async def test_cc_without_argument_does_not_trigger_callback(self):
        reply = await self.service.handle(
            self._message("/cc", "m1"), self.decision, on_started=self._on_started
        )
        self.assertEqual(self.started, 0)
        self.assertEqual(reply, CC_USAGE_REPLY)

    async def test_unauthorized_cc_does_not_trigger_callback(self):
        reply = await self.service.handle(
            self._message("/cc hi", "m1"),
            self._guest_decision(),
            on_started=self._on_started,
        )
        self.assertEqual(self.started, 0)
        self.assertEqual(reply, NO_COMMAND_PERMISSION_REPLY)

    async def test_unauthorized_goon_does_not_trigger_callback(self):
        reply = await self.service.handle(
            self._message("/goon", "m1"),
            self._guest_decision(),
            on_started=self._on_started,
        )
        self.assertEqual(self.started, 0)
        self.assertEqual(reply, NO_COMMAND_PERMISSION_REPLY)

    async def test_goon_without_session_does_not_trigger_callback(self):
        reply = await self.service.handle(
            self._message("/goon", "m1"), self.decision, on_started=self._on_started
        )
        self.assertEqual(self.started, 0)
        self.assertEqual(reply, NO_ACTIVE_SESSION_REPLY)

    async def test_duplicate_message_does_not_trigger_callback(self):
        first = self._message("你好", "same-id")
        await self.service.handle(first, self.decision, on_started=self._on_started)
        await self.service.handle(first, self.decision, on_started=self._on_started)
        self.assertEqual(self.started, 1)

    async def test_callback_absent_is_allowed(self):
        reply = await self.service.handle(self._message("你好", "m1"), self.decision)
        self.assertEqual(reply, "ok")


if __name__ == "__main__":
    unittest.main()
