"""B 站按作品合并（Work Object Merge Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.bili_merge import merge_work_envelope, mention_fragment, work_item_id
from sourcehub.constants import GROUPING_WORK_OBJECT, WORK_ARTICLE, WORK_OPUS, WORK_VIDEO


def mention(kind, object_id, rpid, text, parent=None, root=None, title="作品", url="https://b23.tv/x"):
    return mention_fragment(
        kind=kind,
        object_id=object_id,
        title=title,
        url=url,
        body="简介或正文",
        trigger={"rpid": rpid, "text": text, "sender_id": "u1"},
        parent={"rpid": parent, "text": "父评"} if parent else None,
        root={"rpid": root, "text": "根评"} if root else None,
        received_at="2026-09-21T12:00:00Z",
        conversation_id="mid-1",
        event_id=rpid,
    )


class WorkMergeTests(unittest.TestCase):
    def test_item_id_uses_work_not_notification(self):
        self.assertEqual(work_item_id(WORK_VIDEO, "BV1xx"), "bilibili:video:BV1xx")
        self.assertEqual(work_item_id(WORK_ARTICLE, "123"), "bilibili:article:123")
        self.assertEqual(work_item_id(WORK_OPUS, "99"), "bilibili:opus:99")

    def test_two_mentions_on_same_video_become_one_item(self):
        first = mention(WORK_VIDEO, "BV1xx", "r1", "第一条评论")
        envelope = merge_work_envelope(None, first)
        second = mention(WORK_VIDEO, "BV1xx", "r2", "另一条评论", parent="p2", root="root2")
        merged = merge_work_envelope(envelope, second)
        self.assertEqual(merged.item_id, "bilibili:video:BV1xx")
        self.assertEqual(merged.grouping["type"], GROUPING_WORK_OBJECT)
        rpids = merged.grouping["member_event_ids"]
        self.assertEqual(rpids, ["r1", "r2"])
        texts = [node.text for node in merged.content if node.type == "text" or node.text]
        self.assertTrue(any("第一条评论" in (t or "") for t in texts))
        self.assertTrue(any("另一条评论" in (t or "") for t in texts))
        object_nodes = [node for node in merged.content if node.extra.get("role") == "object"]
        self.assertEqual(len(object_nodes), 1)

    def test_same_rpid_updates_instead_of_duplicating(self):
        first = mention(WORK_VIDEO, "BV1xx", "r1", "旧文")
        envelope = merge_work_envelope(None, first)
        updated = mention(WORK_VIDEO, "BV1xx", "r1", "新文")
        merged = merge_work_envelope(envelope, updated)
        self.assertEqual(merged.grouping["member_event_ids"], ["r1"])
        comment_nodes = [node for node in merged.content if node.extra.get("role") == "trigger"]
        self.assertEqual(len(comment_nodes), 1)
        self.assertEqual(comment_nodes[0].text, "新文")


if __name__ == "__main__":
    unittest.main()
