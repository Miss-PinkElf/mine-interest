"""探针插件（Probe Plugin）静态检查测试。"""

import py_compile
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "astrbot_plugin_e2e_probe"


class ProbeFixtureTest(unittest.TestCase):
    def test_main_compiles(self):
        py_compile.compile(str(FIXTURE / "main.py"), doraise=True)

    def test_metadata_has_name(self):
        text = (FIXTURE / "metadata.yaml").read_text(encoding="utf-8")
        self.assertIn("name: astrbot_plugin_e2e_probe", text)

    def test_commands_are_present(self):
        text = (FIXTURE / "main.py").read_text(encoding="utf-8")
        for name in ("e2e_echo", "e2e_sleep", "e2e_log"):
            self.assertIn('@filter.command("{}")'.format(name), text)

    def test_sleep_invalid_reply_is_present(self):
        text = (FIXTURE / "main.py").read_text(encoding="utf-8")
        self.assertIn("e2e_sleep:invalid", text)


if __name__ == "__main__":
    unittest.main()
