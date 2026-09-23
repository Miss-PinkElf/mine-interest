"""独立资料发布仓库（Isolated Publish Repository）测试。"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from sourcehub.publish import Publisher, PublishError, verify_private_remote


class PublisherTests(unittest.TestCase):
    def test_private_check_requires_anonymous_404_and_ssh_access(self):
        opener = Mock()
        opener.open.side_effect = HTTPError("https://api.github.com/repos/owner/repo", 404, "Not Found", None, None)
        with patch("sourcehub.publish.urllib.request.build_opener", return_value=opener), patch(
            "sourcehub.publish.subprocess.run", return_value=Mock(returncode=0)
        ):
            self.assertTrue(verify_private_remote("git@github.com:owner/repo.git"))
        opener.open.side_effect = None
        with patch("sourcehub.publish.urllib.request.build_opener", return_value=opener):
            self.assertFalse(verify_private_remote("git@github.com:owner/repo.git"))

    def test_only_markdown_is_pushed_from_independent_history(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "sourcehub"
            source.mkdir()
            (source / "items/qq/2026-09-23").mkdir(parents=True)
            (source / "items/qq/2026-09-23/content.md").write_text("# 当天", encoding="utf-8")
            (source / "items/qq/2026-09-23/envelope.json").write_text("secret", encoding="utf-8")
            (source / "media").mkdir()
            (source / "media/image.png").write_bytes(b"media")
            (source / "spool").mkdir()
            remote = base / "remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            publisher = Publisher(source, base / "sourcehub-publish", str(remote), private_check=lambda: True)

            self.assertTrue(publisher.sync_once())
            files = subprocess.check_output(
                ["git", "--git-dir", str(remote), "ls-tree", "-r", "--name-only", "main"], text=True
            )
            self.assertIn("items/qq/2026-09-23/content.md", files)
            self.assertNotIn("envelope.json", files)
            self.assertNotIn("image.png", files)
            self.assertFalse((base / "sourcehub-publish/items/qq/2026-09-23/envelope.json").exists())

            self.assertFalse(publisher.sync_once())
            (source / "items/qq/2026-09-23/content.md").write_text("# 更新", encoding="utf-8")
            self.assertTrue(publisher.sync_once())

    def test_private_gate_blocks_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "sourcehub"
            (source / "items").mkdir(parents=True)
            with self.assertRaises(PublishError):
                Publisher(source, base / "publish", str(base / "remote.git"), private_check=lambda: False).sync_once()
            self.assertFalse((base / "publish").exists())

    def test_signed_url_is_redacted_without_changing_vault(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "sourcehub"
            (source / "items").mkdir(parents=True)
            (source / "items/content.md").write_text("https://example.test/a?rkey=secret", encoding="utf-8")
            allowed = Publisher(source, base / "publish", "unused", private_check=lambda: True)._allowed_files()
            self.assertEqual(allowed[Path("items/content.md")], "https://example.test/a")
            self.assertIn("rkey=secret", (source / "items/content.md").read_text(encoding="utf-8"))
            self.assertFalse((base / "publish").exists())
