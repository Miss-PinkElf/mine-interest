"""Vault 落盘与本地 Git（Vault Persistence Tests）。"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from sourcehub.constants import CONTENT_FILE, ENVELOPE_FILE, GROUPING_SINGLE, SCHEMA_VERSION
from sourcehub.envelope import ContentNode, Envelope
from sourcehub.vault import Vault


def envelope(item_id="qq:message:5", text="单独一条"):
    return Envelope(
        schema_version=SCHEMA_VERSION,
        platform="qq",
        conversation_id="g1",
        item_id=item_id,
        event_id="5",
        sender_id="u1",
        source_time="2026-09-21T12:00:00Z",
        received_at="2026-09-21T12:00:00Z",
        content=[ContentNode(type="text", text=text)],
        attachments=[],
        gaps=[],
        grouping={"type": GROUPING_SINGLE, "member_event_ids": ["5"]},
    )


class VaultTests(unittest.TestCase):
    def test_upsert_writes_envelope_and_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder), git_enabled=False)
            vault.upsert(envelope())
            item = Path(folder) / "items" / "qq" / "2026-09-21" / "items" / "message-5"
            self.assertTrue((item / ENVELOPE_FILE).exists())
            self.assertTrue((item / CONTENT_FILE).exists())
            payload = json.loads((item / ENVELOPE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(payload["item_id"], "qq:message:5")
            self.assertIn("单独一条", (item / CONTENT_FILE).read_text(encoding="utf-8"))
            daily_index = Path(folder) / "items" / "qq" / "2026-09-21" / CONTENT_FILE
            self.assertIn("message-5", daily_index.read_text(encoding="utf-8"))

    def test_second_upsert_overwrites_same_item(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder), git_enabled=False)
            vault.upsert(envelope(text="旧"))
            vault.upsert(envelope(text="新"))
            text = (Path(folder) / "items" / "qq" / "2026-09-21" / "items" / "message-5" / CONTENT_FILE).read_text(encoding="utf-8")
            self.assertIn("新", text)
            self.assertNotIn("旧", text)

    def test_catalog_finds_item_by_object_key(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder), git_enabled=False)
            item = envelope(item_id="bilibili:video:BV1xx")
            item.platform = "bilibili"
            vault.upsert(item, object_key="BV1xx")
            self.assertEqual(vault.lookup("bilibili", "BV1xx"), "bilibili:video:BV1xx")

    def test_git_commit_includes_item_id_and_skips_private(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "private" / "events").mkdir(parents=True)
            (root / "private" / "events" / "secret.json").write_text("{}", encoding="utf-8")
            vault = Vault(root, git_enabled=True)
            vault.upsert(envelope())
            log = subprocess.check_output(["git", "-C", str(root), "log", "-1", "--oneline"], text=True)
            self.assertIn("qq:message:5", log)
            tracked = subprocess.check_output(["git", "-C", str(root), "ls-files"], text=True)
            self.assertNotIn("private/events/secret.json", tracked)
            self.assertIn("items/qq/2026-09-21/items/message-5/envelope.json", tracked)


if __name__ == "__main__":
    unittest.main()
