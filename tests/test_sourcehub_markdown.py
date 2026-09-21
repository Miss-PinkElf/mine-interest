"""原始资料 Markdown 投影（Content Projection Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.constants import GROUPING_WORK_OBJECT, SCHEMA_VERSION
from sourcehub.envelope import ContentNode, Envelope
from sourcehub.markdown import render_content_md


class MarkdownTests(unittest.TestCase):
    def test_renders_title_comments_gaps_and_relative_media(self):
        envelope = Envelope(
            schema_version=SCHEMA_VERSION,
            platform="bilibili",
            conversation_id="mid",
            item_id="bilibili:video:BV1xx",
            event_id="r1",
            sender_id="u1",
            source_time="2026-09-21T12:00:00Z",
            received_at="2026-09-21T12:00:00Z",
            content=[
                ContentNode(type="text", text="视频简介", extra={"role": "object", "url": "https://b23.tv/BV1xx", "title": "标题"}),
                ContentNode(type="text", text="@机器人 收藏", extra={"role": "trigger", "rpid": "r1"}),
                ContentNode(type="image", sha256="abc123", extra={"ext": ".jpg"}),
            ],
            attachments=[],
            gaps=["session_end_missing"],
            grouping={"type": GROUPING_WORK_OBJECT, "member_event_ids": ["r1"]},
        )
        markdown = render_content_md(envelope)
        self.assertIn("标题", markdown)
        self.assertIn("https://b23.tv/BV1xx", markdown)
        self.assertIn("@机器人 收藏", markdown)
        self.assertIn("session_end_missing", markdown)
        self.assertIn("](../../../../media/abc123.jpg)", markdown)


if __name__ == "__main__":
    unittest.main()
