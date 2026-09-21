"""B 站 record 映射到作品片段。"""

from __future__ import annotations

import unittest

import tempfile
from pathlib import Path

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import Store
from sourcehub.bili_ingest import record_to_fragment
from sourcehub.bili_merge import merge_work_envelope
from sourcehub.constants import CONTENT_FILE, WORK_VIDEO
from sourcehub.vault import Vault


class BiliIngestTests(unittest.TestCase):
    def test_video_record_uses_bvid_as_item(self):
        raw = {
            "source_url": "https://www.bilibili.com/video/BV1xx",
            "objects": [{"bvid": "BV1xx", "title": "标题", "desc": "简介"}],
            "comments": {
                "trigger": {"rpid": 11, "content": {"message": "@机器人"}, "mid": 1},
            },
            "notification": {"item": {"business_id": 1, "title": "标题"}},
        }
        fragment = record_to_fragment(raw)
        self.assertEqual(fragment["kind"], WORK_VIDEO)
        self.assertEqual(fragment["object_id"], "BV1xx")
        envelope = merge_work_envelope(None, fragment)
        self.assertEqual(envelope.item_id, "bilibili:video:BV1xx")

    def test_two_records_same_bvid_merge(self):
        def raw(rpid, text):
            return {
                "source_url": "https://www.bilibili.com/video/BV1xx",
                "objects": [{"bvid": "BV1xx", "title": "标题", "desc": "简介"}],
                "comments": {"trigger": {"rpid": rpid, "content": {"message": text}}},
                "notification": {"item": {"business_id": 1}},
            }
        first = merge_work_envelope(None, record_to_fragment(raw(1, "一")))
        merged = merge_work_envelope(first, record_to_fragment(raw(2, "二")))
        self.assertEqual(merged.grouping["member_event_ids"], ["1", "2"])

    def test_store_export_writes_vault_markdown(self):
        raw = {
            "source_url": "https://www.bilibili.com/video/BV1xx",
            "objects": [{"bvid": "BV1xx", "title": "标题", "desc": "简介"}],
            "comments": {"trigger": {"rpid": 11, "content": {"message": "@机器人"}}},
            "notification": {"item": {"business_id": 1, "title": "标题"}, "id": 1},
            "media": [],
        }
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder) / "vault", git_enabled=False)
            store = Store(Path(folder) / "plugin", vault=vault)
            item_dir = Path(folder) / "plugin" / "items" / "1"
            item_dir.mkdir(parents=True)
            store._export_vault(raw, item_dir)
            self.assertEqual(vault.lookup("bilibili", "BV1xx"), "bilibili:video:BV1xx")
            markdown = (
                Path(folder) / "vault" / "items" / "bilibili" / "video" / "BV1xx" / CONTENT_FILE
            ).read_text(encoding="utf-8")
            self.assertIn("简介", markdown)
            self.assertIn("@机器人", markdown)

    def test_complete_record_can_still_export_to_vault(self):
        raw = {
            "source_url": "https://www.bilibili.com/read/cv99",
            "objects": [{"title": "专栏标题", "summary": "摘要"}],
            "comments": {"trigger": {"rpid": 22, "content": {"message": "@专栏"}}},
            "notification": {"item": {"business_id": 12, "title": "专栏标题"}, "id": 2},
            "media": [],
            "status": "complete",
        }
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder) / "vault", git_enabled=False)
            store = Store(Path(folder) / "plugin", vault=vault)
            item_dir = Path(folder) / "plugin" / "items" / "2"
            item_dir.mkdir(parents=True)
            from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import write_json, RECORD_FILE
            write_json(item_dir / RECORD_FILE, raw)
            exported = store.export_existing()
            self.assertEqual(exported, 1)
            self.assertEqual(vault.lookup("bilibili", "99"), "bilibili:article:99")
            markdown = (
                Path(folder) / "vault" / "items" / "bilibili" / "article" / "99" / CONTENT_FILE
            ).read_text(encoding="utf-8")
            self.assertIn("专栏标题", markdown)
            self.assertIn("@专栏", markdown)


if __name__ == "__main__":
    unittest.main()
