import tempfile
import unittest
from pathlib import Path

from scripts.sync_vendor import sync_vendor


class SyncVendorTest(unittest.TestCase):
    def test_copies_engine_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "tools" / "astrbot_e2e"
            source.mkdir(parents=True)
            (source / "__init__.py").write_text("", encoding="utf-8")
            (source / "reports").mkdir()
            (source / "reports" / "secret.json").write_text("{}", encoding="utf-8")
            dest = tmp_path / "vendor" / "astrbot_e2e"
            manifest = sync_vendor(source, dest)
            self.assertTrue((dest / "__init__.py").exists())
            self.assertFalse((dest / "reports").exists())
            self.assertEqual(manifest["source"], str(source))
            self.assertIn("sha256", manifest)
