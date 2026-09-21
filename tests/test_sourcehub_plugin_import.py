"""AstrBot 以插件包加载，插件内必须能相对导入入库库。"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PARENT = ROOT / "integrations" / "astrbot"


class PluginImportTests(unittest.TestCase):
    def test_plugins_import_without_backend_src_on_path(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PLUGIN_PARENT)
        env.pop("PYTHONHOME", None)
        command = [
            sys.executable,
            "-c",
            "import astrbot_plugin_sourcehub_inspector.collect;"
            "import astrbot_plugin_sourcehub_bilibili.store",
        ]
        completed = subprocess.run(
            command,
            env=env,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=completed.stderr or completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
