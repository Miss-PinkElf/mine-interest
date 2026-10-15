"""原始资料 Markdown 投影（Content Projection Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.constants import GROUPING_SINGLE, GROUPING_WORK_OBJECT, SCHEMA_VERSION
from sourcehub.envelope import ContentNode, Envelope
from sourcehub.markdown import render_content_md, render_message_body_md


def qq_message(text: str, gaps: list[str] | None = None) -> Envelope:
    """单条普通 QQ 消息封套，用于校验正文与封套头部的切分。"""
    return Envelope(
        schema_version=SCHEMA_VERSION,
        platform="qq",
        conversation_id="g1",
        item_id="qq:message:5",
        event_id="5",
        sender_id="u1",
        source_time="2026-09-21T12:00:00Z",
        received_at="2026-09-21T12:00:00Z",
        content=[ContentNode(type="text", text=text)],
        attachments=[],
        gaps=gaps or [],
        grouping={"type": GROUPING_SINGLE, "member_event_ids": ["5"]},
    )


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
                ContentNode(type="text", text="上级", extra={"role": "parent", "rpid": "p1", "images": ["../../../../../media/abc123.jpg"]}),
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
        self.assertIn("](../../../../../media/abc123.jpg)", markdown)
        self.assertEqual(markdown.count("# 标题"), 1)
        self.assertIn("## 简介", markdown)
        self.assertNotIn("## 作品", markdown)

    def test_message_body_excludes_envelope_header(self):
        """正文投影只含消息本身，不带封套头部元信息，且保留多行。"""
        envelope = qq_message("第一行\n\n第二行")
        body = render_message_body_md(envelope)
        self.assertEqual(body, "第一行\n\n第二行")
        self.assertNotIn("平台（Platform）", body)
        self.assertNotIn("接收时间（Received At）", body)
        self.assertNotIn("# qq:message:5", body)

    def test_message_body_is_tail_of_full_markdown(self):
        """正文必须是整篇 Markdown 的尾部，二者不能各写一套。"""
        envelope = qq_message("第一行\n第二行")
        body = render_message_body_md(envelope)
        self.assertTrue(render_content_md(envelope).endswith(body + "\n"))

    def test_message_body_skips_gap_section(self):
        """带缺口时头部会多一节，正文起点不能被写死成固定行号。"""
        envelope = qq_message("只有正文", gaps=["session_end_missing"])
        self.assertEqual(render_message_body_md(envelope), "只有正文")
        self.assertIn("session_end_missing", render_content_md(envelope))


if __name__ == "__main__":
    unittest.main()
