"""按天目录与标题目录（Dated Title Path）测试。"""

from __future__ import annotations

import unittest

from sourcehub.envelope import ContentNode, Envelope
from sourcehub.paths import item_storage_path


def envelope(item_id: str, received_at: str, title: str = "") -> Envelope:
    return Envelope(
        schema_version="1", platform=item_id.split(":")[0], conversation_id="g",
        item_id=item_id, event_id="1", sender_id="u", source_time=None,
        received_at=received_at, content=[], attachments=[], gaps=[], grouping={},
        extra={"title": title},
    )


class StoragePathTests(unittest.TestCase):
    def test_qq_uses_shanghai_capture_day_and_item_kind(self):
        path = item_storage_path(envelope("qq:session:123", "2026-09-21T16:00:00Z"))
        self.assertEqual(path, "qq/2026-09-22/session/会话-123")

    def test_qq_title_comes_from_first_readable_text(self):
        item = envelope("qq:forward:456", "2026-09-21T16:00:00Z")
        item.content = [ContentNode(type="forward", children=[ContentNode(type="text", text="  一段转发内容 / 标题  ")])]
        self.assertEqual(item_storage_path(item), "qq/2026-09-22/forward/一段转发内容-标题-456")

    def test_qq_daily_item_stays_in_message_type_directory(self):
        item = envelope("qq:daily:group:2026-09-22:789", "2026-09-21T16:00:00Z")
        item.content = [ContentNode(type="text", text="今天的消息")]
        self.assertEqual(
            item_storage_path(item),
            "qq/2026-09-22/message/今天的消息-group-2026-09-22-789",
        )

    def test_bilibili_uses_clean_title_with_stable_id_suffix(self):
        path = item_storage_path(envelope(
            "bilibili:article:43979666", "2026-09-21T16:00:00Z", "标题 / 不可:用?",
        ))
        self.assertEqual(path, "bilibili/2026-09-22/article/标题-不可-用-43979666")
        self.assertTrue(path.endswith("-43979666"))

    def test_missing_capture_time_uses_explicit_unknown_day(self):
        path = item_storage_path(envelope("bilibili:video:BV1xx", "", "测试视频"))
        self.assertEqual(path, "bilibili/unknown/video/测试视频-BV1xx")


if __name__ == "__main__":
    unittest.main()
