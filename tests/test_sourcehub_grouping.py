"""QQ 成条与封套路径（Grouping Contract Tests）。"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from sourcehub.constants import (
    DEFAULT_SESSION_END,
    DEFAULT_SESSION_START,
    GAP_SESSION_END_MISSING,
    GROUPING_MERGED_FORWARD,
    GROUPING_SESSION_MARKERS,
    GROUPING_SINGLE,
)
from sourcehub.envelope import item_relpath
from sourcehub.grouping import GroupingEngine, IncomingMessage, text_node
from sourcehub.rules import default_qq_pack


def _now():
    return datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


def _msg(event_id, text, *, conv="g1", sender="u1", is_forward=False, nodes=None, received=None):
    stamp = (received or _now()).strftime("%Y-%m-%dT%H:%M:%SZ")
    return IncomingMessage(
        platform="qq",
        conversation_id=conv,
        event_id=event_id,
        sender_id=sender,
        source_time=stamp,
        received_at=stamp,
        text=text,
        nodes=nodes or [text_node(text)],
        is_forward=is_forward,
        raw={"message_id": event_id},
    )


class ItemPathTests(unittest.TestCase):
    def test_colon_item_id_becomes_nested_directory(self):
        self.assertEqual(item_relpath("bilibili:video:BV1xx"), "bilibili/video/BV1xx")
        self.assertEqual(item_relpath("qq:session:100"), "qq/session/100")


class SessionGroupingTests(unittest.TestCase):
    def setUp(self):
        self.engine = GroupingEngine(default_qq_pack())

    def test_session_markers_merge_middle_messages(self):
        now = _now()
        self.assertEqual(self.engine.ingest(_msg("1", DEFAULT_SESSION_START), now), [])
        self.assertEqual(self.engine.ingest(_msg("2", "第一句"), now), [])
        self.assertEqual(self.engine.ingest(_msg("3", "第二句"), now), [])
        done = self.engine.ingest(_msg("4", DEFAULT_SESSION_END), now)
        self.assertEqual(len(done), 1)
        envelope = done[0]
        self.assertEqual(envelope.item_id, "qq:session:1")
        self.assertEqual(envelope.grouping["type"], GROUPING_SESSION_MARKERS)
        self.assertEqual(envelope.grouping["member_event_ids"], ["2", "3"])
        texts = [node.text for node in envelope.content]
        self.assertEqual(texts, ["第一句", "第二句"])
        self.assertNotIn(DEFAULT_SESSION_START, texts)
        self.assertNotIn(DEFAULT_SESSION_END, texts)

    def test_spaced_and_halfwidth_punctuation_still_group_a_paragraph(self):
        now = _now()
        self.assertEqual(self.engine.ingest(_msg("1", ", , ,"), now), [])
        self.assertEqual(self.engine.ingest(_msg("2", "段落测试"), now), [])
        self.assertEqual(self.engine.ingest(_msg("3", "123"), now), [])
        self.assertEqual(self.engine.ingest(_msg("4", "喜欢你"), now), [])
        done = self.engine.ingest(_msg("5", "。 。 。"), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(
            [node.text for node in done[0].content],
            ["段落测试", "123", "喜欢你"],
        )

    def test_english_ellipsis_closes_session(self):
        now = _now()
        self.engine.ingest(_msg("1", ",,,"), now)
        self.engine.ingest(_msg("2", "一段"), now)
        done = self.engine.ingest(_msg("3", "..."), now)
        self.assertEqual(len(done), 1)
        self.assertEqual([node.text for node in done[0].content], ["一段"])

    def test_ellipsis_inside_sentence_is_not_end_marker(self):
        now = _now()
        self.engine.ingest(_msg("1", DEFAULT_SESSION_START), now)
        self.engine.ingest(_msg("2", "好的。。。"), now)
        self.assertEqual(self.engine.open_session_ids(), ["g1"])
        done = self.engine.ingest(_msg("3", DEFAULT_SESSION_END), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(
            [node.text for node in done[0].content],
            ["好的。。。"],
        )

    def test_idle_timeout_keeps_buffer_and_records_gap(self):
        now = _now()
        self.engine.ingest(_msg("1", DEFAULT_SESSION_START), now)
        self.engine.ingest(_msg("2", "未结束"), now)
        later = now + timedelta(seconds=1801)
        done = self.engine.flush_idle(later)
        self.assertEqual(len(done), 1)
        self.assertIn(GAP_SESSION_END_MISSING, done[0].gaps)
        self.assertEqual([node.text for node in done[0].content], ["未结束"])

    def test_new_start_closes_previous_session_with_gap(self):
        now = _now()
        self.engine.ingest(_msg("1", DEFAULT_SESSION_START), now)
        self.engine.ingest(_msg("2", "旧会话"), now)
        done = self.engine.ingest(_msg("3", DEFAULT_SESSION_START), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0].item_id, "qq:session:1")
        self.assertIn(GAP_SESSION_END_MISSING, done[0].gaps)

    def test_stray_end_marker_is_not_an_item(self):
        now = _now()
        self.assertEqual(self.engine.ingest(_msg("9", DEFAULT_SESSION_END), now), [])

    def test_plain_message_is_single_item(self):
        now = _now()
        done = self.engine.ingest(_msg("5", "单独一条"), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0].item_id, "qq:message:5")
        self.assertEqual(done[0].grouping["type"], GROUPING_SINGLE)

    def test_forward_outside_session_is_one_block(self):
        now = _now()
        done = self.engine.ingest(_msg("8", "聊天记录", is_forward=True), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0].item_id, "qq:forward:8")
        self.assertEqual(done[0].grouping["type"], GROUPING_MERGED_FORWARD)

    def test_forward_inside_session_is_child_not_new_item(self):
        now = _now()
        self.engine.ingest(_msg("1", DEFAULT_SESSION_START), now)
        self.assertEqual(self.engine.ingest(_msg("2", "聊天记录", is_forward=True), now), [])
        done = self.engine.ingest(_msg("3", DEFAULT_SESSION_END), now)
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0].grouping["member_event_ids"], ["2"])
        self.assertTrue(done[0].content[0].is_forward or done[0].content[0].type == "forward")

    def test_sessions_are_shared_across_senders_in_one_group(self):
        now = _now()
        self.engine.ingest(_msg("1", DEFAULT_SESSION_START, sender="a"), now)
        self.engine.ingest(_msg("2", "号A", sender="a"), now)
        self.engine.ingest(_msg("3", "号B", sender="b"), now)
        done = self.engine.ingest(_msg("4", DEFAULT_SESSION_END, sender="b"), now)
        self.assertEqual([node.text for node in done[0].content], ["号A", "号B"])


if __name__ == "__main__":
    unittest.main()
