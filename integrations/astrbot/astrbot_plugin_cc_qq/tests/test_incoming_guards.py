"""过期消息与空文本回复的单元测试。"""

import time
import unittest

from astrbot_plugin_cc_qq.constants import (
    DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS,
    EMPTY_MESSAGE_REPLY,
)
from astrbot_plugin_cc_qq.contracts import ConversationKind
from astrbot_plugin_cc_qq.platform.qq_events import (
    empty_text_reply,
    onebot_event_time,
    should_ignore_as_stale,
    stale_max_age_from_config,
)


class _Raw:
    def __init__(self, raw):
        self.raw_message = raw


class _Event:
    def __init__(self, raw):
        self.message_obj = _Raw(raw)


class IncomingGuardTest(unittest.TestCase):
    def test_private_empty_text_is_silent(self):
        self.assertIsNone(empty_text_reply(ConversationKind.PRIVATE))

    def test_group_empty_text_keeps_at_hint(self):
        self.assertEqual(empty_text_reply(ConversationKind.GROUP), EMPTY_MESSAGE_REPLY)

    def test_reads_onebot_time_from_raw_message(self):
        self.assertEqual(onebot_event_time(_Event({"time": 1_700_000_000})), 1_700_000_000)

    def test_missing_or_invalid_time_is_none(self):
        self.assertIsNone(onebot_event_time(_Event({})))
        self.assertIsNone(onebot_event_time(_Event({"time": "1700000000"})))
        self.assertIsNone(onebot_event_time(_Event({"time": True})))

    def test_old_message_is_stale(self):
        now = 1_700_000_000
        event_time = now - DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS - 1
        self.assertTrue(
            should_ignore_as_stale(event_time, now, DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS)
        )

    def test_recent_message_and_missing_time_stay(self):
        now = int(time.time())
        max_age = DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS
        self.assertFalse(should_ignore_as_stale(now - 5, now, max_age))
        self.assertFalse(should_ignore_as_stale(None, now, max_age))
        self.assertFalse(should_ignore_as_stale(now + 30, now, max_age))

    def test_configured_max_age_overrides_default(self):
        now = 1_700_000_000
        self.assertFalse(should_ignore_as_stale(now - 10, now, 30))
        self.assertTrue(should_ignore_as_stale(now - 31, now, 30))
        self.assertFalse(should_ignore_as_stale(now - 99999, now, 0))

    def test_invalid_config_falls_back_to_default(self):
        self.assertEqual(stale_max_age_from_config({}), DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS)
        self.assertEqual(
            stale_max_age_from_config({"stale_message_max_age_seconds": -1}),
            DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS,
        )
        self.assertEqual(
            stale_max_age_from_config({"stale_message_max_age_seconds": 45}),
            45,
        )
        self.assertEqual(
            stale_max_age_from_config({"stale_message_max_age_seconds": 0}),
            0,
        )

    def test_millisecond_timestamp_is_normalized(self):
        now = 1_700_000_000
        self.assertTrue(
            should_ignore_as_stale((now - 1000) * 1000, now, DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS)
        )


if __name__ == "__main__":
    unittest.main()
