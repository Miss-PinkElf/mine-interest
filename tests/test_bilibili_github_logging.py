"""B 站插件 GitHub 自动化日志守卫（Logging Guard）。

B 站插件不回复 QQ 消息，结果只能靠 AstrBot 日志和插件页查看。本测试确保：

1. 动作结果确实写入插件日志通道，并带 `[SourceHub Bilibili]` 前缀；
2. 检测到链接但自动化关闭时，会留下明确的跳过日志，而不是静默返回。
"""

from __future__ import annotations

import unittest

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.constants import LOG_PREFIX
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.content import Document
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.poller import (
    NOTIFICATION_TITLE_LOG_MAX_CHARS,
    Poller,
    notification_label,
)
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.sourcehub.github_actions import (
    ActionResult,
)

REPOSITORY_LINK = "https://github.com/owner/demo"


class RecordingLogger:
    def __init__(self) -> None:
        self.info_messages: list[str] = []
        self.warning_messages: list[str] = []

    def info(self, message: str, *args) -> None:
        self.info_messages.append(message % args if args else message)

    def warning(self, message: str, *args) -> None:
        self.warning_messages.append(message % args if args else message)


class FakeGithub:
    def __init__(self, results=None, error: Exception | None = None) -> None:
        self.results = results or []
        self.error = error
        self.calls: list[tuple[list[str], bool, str]] = []

    def handle(self, repositories, fork, source):
        self.calls.append((list(repositories), fork, source))
        if self.error is not None:
            raise self.error
        return self.results


def _document() -> Document:
    return Document(text=REPOSITORY_LINK)


def _notification() -> dict:
    return {"item": {"source_content": REPOSITORY_LINK}}


SAMPLE_NOTIFICATION = {
    "id": 1,
    "user": {"mid": 10086, "nickname": "测试用户"},
    "item": {"type": "reply", "business": "评论", "title": "一条测试标题", "source_content": "@bot"},
}


class FakeCollector:
    async def collect(self, notification):
        return {}, Document(text="")


class FakeStore:
    def __init__(self, pending) -> None:
        self._pending = pending
        self.saved: list[tuple] = []

    def pending(self):
        return self._pending

    async def save(self, notification, raw, doc, client):
        self.saved.append((notification, raw, doc))


class FakeScanStore:
    def __init__(self) -> None:
        self.received: list[dict] = []
        self.cursor_value = None

    def cursor(self):
        return None

    def receive(self, item):
        self.received.append(item)

    def save_cursor(self, value):
        self.cursor_value = value


class FakeScanClient:
    def __init__(self, items) -> None:
        self.items = items

    async def get(self, name, **params):
        return {"items": self.items, "cursor": {"is_end": True}}


class GithubAutomationLoggingTests(unittest.IsolatedAsyncioTestCase):
    async def test_action_results_are_logged_with_prefix(self):
        logger = RecordingLogger()
        github = FakeGithub([ActionResult("owner/demo", "star", True, "已 star")])
        poller = Poller(None, None, None, github=github, logger=logger)

        await poller._run_github(_notification(), {}, _document())

        self.assertEqual(github.calls, [(["owner/demo"], False, "bilibili")])
        self.assertTrue(
            any("GitHub 自动化开始" in message for message in logger.info_messages)
        )
        self.assertTrue(
            any("GitHub star owner/demo：已 star" in message for message in logger.info_messages)
        )
        self.assertTrue(
            all(message.startswith(LOG_PREFIX) for message in logger.info_messages)
        )

    async def test_disabled_automation_logs_skip_instead_of_silence(self):
        logger = RecordingLogger()
        poller = Poller(None, None, None, github=None, logger=logger)

        await poller._run_github(_notification(), {}, _document())

        self.assertEqual(len(logger.info_messages), 1)
        self.assertIn("GitHub 自动化未启用", logger.info_messages[0])
        self.assertTrue(logger.info_messages[0].startswith(LOG_PREFIX))

    async def test_handle_error_is_logged_as_warning(self):
        logger = RecordingLogger()
        github = FakeGithub(error=TypeError("boom"))
        poller = Poller(None, None, None, github=github, logger=logger)

        await poller._run_github(_notification(), {}, _document())

        self.assertTrue(
            any(
                "GitHub 自动化异常：TypeError：boom" in message
                for message in logger.warning_messages
            )
        )
        self.assertTrue(
            all(message.startswith(LOG_PREFIX) for message in logger.warning_messages)
        )


class BilibiliNotificationLoggingTests(unittest.IsolatedAsyncioTestCase):
    def test_notification_label_contains_business_user_and_title(self):
        self.assertEqual(
            notification_label(SAMPLE_NOTIFICATION),
            "评论｜测试用户｜一条测试标题",
        )

    def test_long_title_is_truncated(self):
        notification = {
            **SAMPLE_NOTIFICATION,
            "item": {**SAMPLE_NOTIFICATION["item"], "title": "长" * (NOTIFICATION_TITLE_LOG_MAX_CHARS + 5)},
        }
        label = notification_label(notification)
        self.assertTrue(label.endswith("…"))
        self.assertNotIn("长" * (NOTIFICATION_TITLE_LOG_MAX_CHARS + 1), label)

    async def test_process_logs_received_and_saved(self):
        logger = RecordingLogger()
        store = FakeStore([SAMPLE_NOTIFICATION])
        poller = Poller(None, FakeCollector(), store, logger=logger)

        await poller.process()

        self.assertEqual(len(store.saved), 1)
        expected = "评论｜测试用户｜一条测试标题"
        self.assertTrue(
            any(f"开始采集 B 站通知：{expected}" in message for message in logger.info_messages)
        )
        self.assertTrue(
            any(f"已保存 B 站条目：{expected}" in message for message in logger.info_messages)
        )

    async def test_scan_logs_received_count(self):
        logger = RecordingLogger()
        store = FakeScanStore()
        poller = Poller(FakeScanClient([SAMPLE_NOTIFICATION]), None, store, logger=logger)

        await poller.scan()

        self.assertEqual(store.received, [SAMPLE_NOTIFICATION])
        self.assertTrue(
            any("收到 1 条 B 站通知" in message for message in logger.info_messages)
        )


if __name__ == "__main__":
    unittest.main()
