import json
import tempfile
import unittest
from pathlib import Path

from scripts.probe_env import build_profile


class ProbeEnvTest(unittest.TestCase):
    def test_builds_profile_with_injected_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            plugin = home / ".astrbot" / "data" / "plugins" / "demo_plugin"
            plugin.mkdir(parents=True)
            napcat = (
                home
                / "Library/Containers/com.tencent.qq/Data/Documents/napcat"
            )
            napcat.mkdir(parents=True)
            (napcat / "package.json").write_text(
                json.dumps({"name": "napcat", "version": "4.18.28"}),
                encoding="utf-8",
            )
            profile = build_profile(None, home)
        self.assertEqual(profile["schema_version"], 1)
        self.assertEqual(profile["napcat"]["version"], "4.18.28")
        self.assertIn("demo_plugin", profile["plugins"]["available"])
        self.assertIn("ports", profile)
        self.assertIn("config", profile)

    def test_config_info_does_not_leak_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = home / "config.json"
            config.write_text(
                json.dumps(
                    {
                        "test_root": str(home / "root"),
                        "bot": {"qq": "10001", "token": "secret-token"},
                        "sender": {"qq": "10002", "token": "secret-token"},
                        "webui": {"password": "secret-pass"},
                        "group_id": "123456789",
                    }
                ),
                encoding="utf-8",
            )
            profile = build_profile(config, home)
        text = json.dumps(profile, ensure_ascii=False)
        self.assertNotIn("secret-token", text)
        self.assertNotIn("secret-pass", text)
        self.assertEqual(profile["config"]["bot_qq"], "10001")
