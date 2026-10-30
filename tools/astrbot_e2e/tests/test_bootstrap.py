import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.bootstrap import (
    patch_config,
    resolve_plugin_source,
    sync_plugins,
    write_cc_qq_config,
)


class BootstrapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        (self.root / "data").mkdir(parents=True)
        self.cfg = {
            "test_root": str(self.root),
            "webui": {"port": 6186, "username": "e2e", "password": "E2ePass123"},
            "astrbot": {
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": 6198,
                "reverse_ws_token": "reverse-token",
                "plugins": ["astrbot_plugin_e2e_probe"],
            },
            "bot": {"qq": "10001"},
            "sender": {"qq": "10002"},
            "group_id": "123456789",
        }

    def test_patch_config_sets_platform_and_ports(self):
        (self.root / "data" / "cmd_config.json").write_text(
            json.dumps({"dashboard": {}, "platform": []}), encoding="utf-8"
        )
        patch_config(self.cfg)
        data = json.loads((self.root / "data" / "cmd_config.json").read_text(encoding="utf-8"))
        self.assertEqual(data["dashboard"]["port"], 6186)
        self.assertEqual(data["platform"][0]["id"], "Test-E2E")
        self.assertTrue(data["platform"][0]["enable"])
        self.assertEqual(data["platform"][0]["ws_reverse_port"], 6198)
        self.assertEqual(data["platform"][0]["ws_reverse_host"], "127.0.0.1")
        self.assertEqual(data["platform"][0]["ws_reverse_token"], "reverse-token")
        self.assertEqual(data["plugin_set"], ["astrbot_plugin_e2e_probe"])
        self.assertTrue(data["disable_builtin_commands"])

    def test_patch_config_keeps_dashboard_credentials(self):
        (self.root / "data" / "cmd_config.json").write_text(
            json.dumps(
                {
                    "dashboard": {
                        "pbkdf2_password": "hash",
                        "jwt_secret": "secret",
                    },
                    "platform": [],
                }
            ),
            encoding="utf-8",
        )
        patch_config(self.cfg)
        data = json.loads((self.root / "data" / "cmd_config.json").read_text(encoding="utf-8"))
        self.assertEqual(data["dashboard"]["pbkdf2_password"], "hash")
        self.assertEqual(data["dashboard"]["jwt_secret"], "secret")
        self.assertEqual(data["dashboard"]["port"], 6186)

    def test_write_cc_qq_config_uses_test_group(self):
        write_cc_qq_config(self.cfg)
        path = self.root / "data" / "config" / "astrbot_plugin_cc_qq_config.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["qq_platform_id"], "Test-E2E")
        self.assertEqual(data["enabled_group_ids"], ["123456789"])
        self.assertEqual(data["owner_qq_id"], "10002")
        rules = json.loads(data["group_rules_json"])
        self.assertIn("123456789", rules)
        self.assertTrue(Path(rules["123456789"]["work_dir"]).exists())

    def test_write_cc_qq_config_can_disable(self):
        write_cc_qq_config(self.cfg, enabled=False)
        path = self.root / "data" / "config" / "astrbot_plugin_cc_qq_config.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["enabled_group_ids"], [])
        self.assertEqual(json.loads(data["group_rules_json"]), {})

    def test_sync_plugins_copies_without_tests(self):
        source = Path(self.tmp.name) / "repo" / "integrations" / "astrbot" / "demo_plugin"
        (source / "tests").mkdir(parents=True)
        (source / "__pycache__").mkdir()
        (source / "main.py").write_text("print('ok')", encoding="utf-8")
        (source / "tests" / "test_demo.py").write_text("x", encoding="utf-8")
        (source / "cached.pyc").write_text("x", encoding="utf-8")
        (source / "__pycache__" / "main.cpython-39.pyc").write_text("x", encoding="utf-8")
        sync_plugins(self.cfg, repo_root=Path(self.tmp.name) / "repo", plugins=["demo_plugin"])
        target = self.root / "data" / "plugins" / "demo_plugin"
        self.assertTrue((target / "main.py").exists())
        self.assertFalse((target / "tests").exists())
        self.assertFalse((target / "cached.pyc").exists())
        self.assertFalse((target / "__pycache__").exists())

    def test_sync_plugins_falls_back_to_fixtures(self):
        source = (
            Path(self.tmp.name)
            / "repo"
            / "tools"
            / "astrbot_e2e"
            / "fixtures"
            / "fixture_plugin"
        )
        source.mkdir(parents=True)
        (source / "main.py").write_text("print('fixture')", encoding="utf-8")
        sync_plugins(
            self.cfg,
            repo_root=Path(self.tmp.name) / "repo",
            plugins=["fixture_plugin"],
        )
        target = self.root / "data" / "plugins" / "fixture_plugin"
        self.assertTrue((target / "main.py").exists())


class ResolvePluginSourceTest(unittest.TestCase):
    def test_prefers_configured_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            configured = tmp_path / "custom-plugin"
            configured.mkdir()
            cfg = {"plugin_sources": {"demo": str(configured)}}
            source = resolve_plugin_source(cfg, tmp_path / "repo", "demo")
            self.assertEqual(source, configured)

    def test_falls_back_to_repo_integrations(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "repo" / "integrations" / "astrbot" / "demo"
            source_dir.mkdir(parents=True)
            source = resolve_plugin_source({}, tmp_path / "repo", "demo")
            self.assertEqual(source, source_dir)

    def test_raises_with_all_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "插件源目录不存在"):
                resolve_plugin_source({}, tmp_path / "repo", "missing")
