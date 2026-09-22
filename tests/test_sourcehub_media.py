"""媒体哈希与体积（Media Policy Tests）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sourcehub.constants import GAP_MEDIA_TOO_LARGE, NODE_FILE, SCHEMA_VERSION
from sourcehub.envelope import ContentNode, Envelope
from sourcehub.media import accept_media, hash_name, image_extension, persist_media_nodes
from sourcehub.vault import Vault

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff" + b"\x00" * 16


class MediaTests(unittest.TestCase):
    def test_png_magic_maps_to_png_extension(self):
        self.assertEqual(image_extension(PNG), ".png")
        self.assertEqual(image_extension(JPEG), ".jpg")

    def test_identical_bytes_share_hash_name(self):
        self.assertEqual(hash_name(PNG), hash_name(PNG))
        self.assertTrue(hash_name(PNG).endswith(".png"))

    def test_oversize_bytes_are_rejected_with_gap(self):
        data, name, gap = accept_media(PNG, max_bytes=8)
        self.assertIsNone(data)
        self.assertIsNone(name)
        self.assertEqual(gap, GAP_MEDIA_TOO_LARGE)

    def test_accepted_bytes_keep_content_and_name(self):
        data, name, gap = accept_media(PNG, max_bytes=1024)
        self.assertEqual(data, PNG)
        self.assertTrue(name.endswith(".png"))
        self.assertIsNone(gap)

    def test_file_node_uses_same_direct_media_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Vault(Path(folder), git_enabled=False)
            envelope = Envelope(
                schema_version=SCHEMA_VERSION, platform="qq", conversation_id="g",
                item_id="qq:message:1", event_id="1", sender_id="u", source_time=None,
                received_at="2026-09-21T12:00:00Z",
                content=[ContentNode(type=NODE_FILE, url="https://example.test/file")],
                attachments=[], gaps=[], grouping={},
            )
            persist_media_nodes(
                envelope, vault, 100 * 1024 * 1024,
                lambda *_: (b"GIF89a", "a.gif", None),
            )
            self.assertEqual(envelope.content[0].sha256, hash_name(b"GIF89a").split(".")[0])


if __name__ == "__main__":
    unittest.main()
