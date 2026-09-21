"""QQ 消息解析（QQ Ingest Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.constants import GAP_EVENT_ID_MISSING, NODE_FORWARD, NODE_IMAGE, NODE_TEXT
from sourcehub.qq_ingest import parse_onebot_message


class QqIngestTests(unittest.TestCase):
    def test_text_and_image_segments_become_nodes(self):
        message = parse_onebot_message({
            "message_id": 42,
            "group_id": 100,
            "user_id": 7,
            "time": 1700000000,
            "message": [
                {"type": "text", "data": {"text": "hello"}},
                {"type": "image", "data": {"url": "https://img.example/a.jpg"}},
            ],
        })
        self.assertEqual(message.event_id, "42")
        self.assertEqual(message.conversation_id, "100")
        self.assertEqual(message.nodes[0].type, NODE_TEXT)
        self.assertEqual(message.nodes[0].text, "hello")
        self.assertEqual(message.nodes[1].type, NODE_IMAGE)
        self.assertEqual(message.nodes[1].url, "https://img.example/a.jpg")
        self.assertFalse(message.is_forward)

    def test_forward_segment_marks_block(self):
        message = parse_onebot_message({
            "message_id": "fwd-1",
            "group_id": "100",
            "user_id": "7",
            "message": [
                {"type": "forward", "data": {"id": "resid", "content": [
                    {"message": [{"type": "text", "data": {"text": "内层"}}]},
                ]}},
            ],
        })
        self.assertTrue(message.is_forward)
        self.assertEqual(message.nodes[0].type, NODE_FORWARD)
        self.assertEqual(message.nodes[0].children[0].text, "内层")

    def test_missing_message_id_is_gap_not_timestamp(self):
        message = parse_onebot_message({
            "group_id": "100",
            "user_id": "7",
            "time": 1700000000,
            "message": [{"type": "text", "data": {"text": "x"}}],
        })
        self.assertEqual(message.event_id, "")
        self.assertIn(GAP_EVENT_ID_MISSING, message.raw.get("gaps", []))


if __name__ == "__main__":
    unittest.main()
