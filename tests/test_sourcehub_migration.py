"""历史 Vault（资料库）迁移预演测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sourcehub.migration import execute_migration, plan_migration
from sourcehub.vault import Vault
from tests.test_sourcehub_vault import envelope


class MigrationTests(unittest.TestCase):
    def test_plan_lists_legacy_item_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            vault = Vault(root, git_enabled=False)
            legacy = root / "items/qq/message/5"
            legacy.mkdir(parents=True)
            (legacy / "envelope.json").write_text(
                __import__("json").dumps(envelope().to_dict()), encoding="utf-8"
            )

            plan = plan_migration(vault)

            self.assertEqual(plan[0].source, legacy)
            self.assertEqual(plan[0].target, root / "items/qq/2026-09-21/message/单独一条-5")
            self.assertTrue(legacy.exists())

    def test_execute_moves_item_and_updates_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            vault = Vault(root, git_enabled=False)
            legacy = root / "items/qq/message/5"
            legacy.mkdir(parents=True)
            (legacy / "envelope.json").write_text(
                __import__("json").dumps(envelope().to_dict()), encoding="utf-8"
            )

            execute_migration(vault, plan_migration(vault))

            self.assertFalse(legacy.exists())
            self.assertTrue((root / "items/qq/2026-09-21/message/单独一条-5/envelope.json").exists())
            self.assertIsNotNone(vault.get("qq:message:5"))


if __name__ == "__main__":
    unittest.main()
