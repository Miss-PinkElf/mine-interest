"""B 站存量重渲染工具（Rerender Tool Tests）。"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sourcehub.constants import GROUPING_WORK_OBJECT, SCHEMA_VERSION
from sourcehub.envelope import ContentNode, Envelope
from sourcehub.vault import Vault


class RerenderToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "archive"
        self.vault = self.root / "vault"
        self.record_path = self.archive / "123" / "items" / "1" / "record.json"
        self.record_path.parent.mkdir(parents=True)
        self.record_path.write_text(json.dumps({
            "notification": {"item": {"source_id": 77, "uri": "https://www.bilibili.com/read/cv99"}},
            "source_url": "https://www.bilibili.com/read/cv99",
            "objects": [{"title": "测试专栏", "content": "<p>结构化正文</p>"}],
            "comments": {"trigger": {"rpid": 77, "content": {"message": "@机器人"}}},
            "media": [],
            "attempted_at": "2026-09-28T00:00:00Z",
        }, ensure_ascii=False), encoding="utf-8")

    def run_tool(self, *extra):
        return subprocess.run([
            sys.executable, "tools/preview_bilibili_rerender.py",
            "--archive-root", str(self.archive), "--vault", str(self.vault), *extra,
        ], capture_output=True, text=True)

    def test_default_preview_does_not_write_vault(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("作品：1", result.stdout)
        self.assertFalse(self.vault.exists())

    def test_apply_backs_up_and_renders_source_body(self):
        backup = self.root / "backup"
        result = self.run_tool("--apply", "--backup-dir", str(backup))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((backup / "records" / "123" / "items" / "1" / "record.json").exists())
        outputs = list((self.vault / "items" / "bilibili").rglob("envelope.json"))
        self.assertEqual(len(outputs), 1)
        content = outputs[0].with_name("content.md").read_text(encoding="utf-8")
        self.assertIn("结构化正文", content)
        self.assertEqual(content.count("# 测试专栏"), 1)

    def test_preview_reports_source_picture_missing_from_media_list(self):
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        record["objects"][0]["content"] = "<p>正文</p><img src='https://i0.hdslb.com/missing.jpg'>"
        self.record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("已有媒体缺口：1", result.stdout)

    def test_rollback_restores_moved_item_directory(self):
        vault = Vault(self.vault, git_enabled=False)
        old = Envelope(
            schema_version=SCHEMA_VERSION, platform="bilibili", conversation_id="", item_id="bilibili:article:99",
            event_id="77", sender_id="", source_time=None, received_at="2026-09-28T00:00:00Z",
            content=[ContentNode(type="text", text="旧正文", extra={"role": "object", "kind": "article", "title": "旧标题", "url": "https://www.bilibili.com/read/cv99"})],
            attachments=[], gaps=[], grouping={"type": GROUPING_WORK_OBJECT},
        )
        vault.upsert(old, object_key="99")
        old_folder = vault.item_dir(old.item_id)
        backup = self.root / "backup"
        self.assertEqual(self.run_tool("--apply", "--backup-dir", str(backup)).returncode, 0)
        new_folder = Vault(self.vault, git_enabled=False).item_dir(old.item_id)
        self.assertNotEqual(old_folder, new_folder)
        self.assertFalse(old_folder.exists())
        result = self.run_tool("--rollback", str(backup))
        self.assertEqual(result.returncode, 0, result.stderr)
        restored = Vault(self.vault, git_enabled=False)
        self.assertEqual(restored.item_dir(old.item_id), old_folder)
        self.assertTrue(old_folder.exists())
        self.assertFalse(new_folder.exists())
        self.assertIn("旧正文", (old_folder / "content.md").read_text(encoding="utf-8"))

    def test_rollback_refuses_new_bilibili_item_after_apply(self):
        backup = self.root / "backup"
        self.assertEqual(self.run_tool("--apply", "--backup-dir", str(backup)).returncode, 0)
        new_item = self.vault / "items" / "bilibili" / "2026-09-29" / "video" / "new" / "content.md"
        new_item.parent.mkdir(parents=True)
        new_item.write_text("新采集条目", encoding="utf-8")
        result = self.run_tool("--rollback", str(backup))
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(new_item.exists())


if __name__ == "__main__":
    unittest.main()
