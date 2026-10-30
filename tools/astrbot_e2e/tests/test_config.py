import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.config import ConfigError, load_config, mask_config, validate_config


def minimal_config(root: Path) -> dict:
    return {
        "test_root": str(root),
        "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "e2e-pass-123"},
        "astrbot": {
            "command": "astrbot",
            "reverse_ws_host": "127.0.0.1",
            "reverse_ws_port": 6198,
            "reverse_ws_token": "reverse-token",
            "plugins": ["astrbot_plugin_e2e_probe", "astrbot_plugin_cc_qq"],
            "startup_timeout_seconds": 120,
        },
        "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "bot-token"},
        "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "sender-token"},
        "group_id": "123456789",
        "judge": {"base_url": "", "api_key": "", "model": ""},
        "timeouts": {"message_seconds": 60, "reload_seconds": 120, "log_window_padding_seconds": 5},
    }


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        self.path = Path(self.tmp.name) / "config.local.json"

    def write(self, **overrides):
        cfg = minimal_config(self.root)
        cfg.update(overrides)
        self.path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        return cfg

    def test_accepts_minimal_config(self):
        self.write()
        cfg = load_config(self.path)
        self.assertEqual(cfg["group_id"], "123456789")
        self.assertEqual(cfg["test_root"], str(self.root.resolve()))

    def test_rejects_production_root(self):
        self.write(test_root=str(Path.home() / ".astrbot"))
        with self.assertRaisesRegex(ConfigError, "生产数据根"):
            load_config(self.path)

    def test_rejects_same_qq(self):
        cfg = minimal_config(self.root)
        cfg["sender"]["qq"] = cfg["bot"]["qq"]
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "必须不同"):
            load_config(self.path)

    def test_rejects_production_port(self):
        cfg = minimal_config(self.root)
        cfg["webui"]["port"] = 6185
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "生产端口冲突"):
            load_config(self.path)

    def test_masks_secrets(self):
        self.write()
        cfg = load_config(self.path)
        masked = mask_config(cfg)
        self.assertEqual(masked["webui"]["password"], "***")
        self.assertEqual(masked["bot"]["token"], "***")
        self.assertEqual(masked["sender"]["token"], "***")

    def test_rejects_missing_or_blank_test_root(self):
        cases = {
            "missing": lambda cfg: cfg.pop("test_root"),
            "blank": lambda cfg: cfg.update(test_root=""),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name):
                cfg = minimal_config(self.root)
                mutate(cfg)
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaises(ConfigError):
                    load_config(self.path)

    def test_rejects_missing_astrbot_command(self):
        cfg = minimal_config(self.root)
        cfg["astrbot"].pop("command")
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaises(ConfigError):
            load_config(self.path)

    def test_rejects_blank_qq(self):
        for side in ("bot", "sender"):
            with self.subTest(side=side):
                cfg = minimal_config(self.root)
                cfg[side]["qq"] = ""
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaises(ConfigError):
                    load_config(self.path)

    def test_rejects_non_numeric_group_id(self):
        self.write(group_id="group-123")
        with self.assertRaises(ConfigError):
            load_config(self.path)

    def test_rejects_missing_config_file(self):
        with self.assertRaises(ConfigError):
            load_config(self.path)

    def test_rejects_invalid_json(self):
        self.path.write_text("{not-json", encoding="utf-8")
        with self.assertRaises(ConfigError):
            load_config(self.path)

    def test_wraps_file_read_errors(self):
        with self.assertRaises(ConfigError):
            load_config(Path(self.tmp.name))
        self.path.write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(ConfigError):
            load_config(self.path)

    def test_rejects_production_ports_in_onebot_urls(self):
        cases = {"bot": 6185, "sender": 6199}
        for side, port in cases.items():
            with self.subTest(side=side, port=port):
                cfg = minimal_config(self.root)
                cfg[side]["onebot_ws"] = "ws://127.0.0.1:{}/onebot/v11/ws".format(port)
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaisesRegex(ConfigError, "生产端口冲突"):
                    load_config(self.path)

    def test_rejects_invalid_url_ports(self):
        for url in ("ws://127.0.0.1:abc/x", "ws://127.0.0.1:99999/x"):
            with self.subTest(url=url):
                cfg = minimal_config(self.root)
                cfg["bot"]["onebot_ws"] = url
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaises(ConfigError) as ctx:
                    load_config(self.path)
                self.assertIn("端口", str(ctx.exception))

    def test_rejects_url_without_port(self):
        cfg = minimal_config(self.root)
        cfg["sender"]["onebot_ws"] = "ws://127.0.0.1/onebot/v11/ws"
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "缺少端口"):
            load_config(self.path)

    def test_rejects_non_integer_ports(self):
        for value in (True, 6186.9):
            with self.subTest(value=value):
                cfg = minimal_config(self.root)
                cfg["webui"]["port"] = value
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaisesRegex(ConfigError, "整数端口"):
                    load_config(self.path)

    def test_rejects_non_object_sections(self):
        for key in ("webui", "astrbot", "bot", "sender"):
            with self.subTest(key=key):
                cfg = minimal_config(self.root)
                cfg[key] = ["not-a-dict"]
                self.path.write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaises(ConfigError):
                    load_config(self.path)

    def test_normalizes_int_identifiers(self):
        cfg = minimal_config(self.root)
        cfg["bot"]["qq"] = 10001
        cfg["sender"]["qq"] = 10002
        cfg["group_id"] = 123456789
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        loaded = load_config(self.path)
        self.assertEqual(loaded["bot"]["qq"], "10001")
        self.assertEqual(loaded["sender"]["qq"], "10002")
        self.assertEqual(loaded["group_id"], "123456789")

    def test_validate_config_expands_home(self):
        cfg = minimal_config(self.root)
        cfg["test_root"] = "~/.astrbot"
        with self.assertRaisesRegex(ConfigError, "生产数据根"):
            validate_config(cfg)

    def test_validate_config_normalizes_test_root(self):
        cfg = minimal_config(self.root)
        validate_config(cfg)
        self.assertEqual(cfg["test_root"], str(self.root.resolve()))

    def test_accepts_plugin_sources(self):
        self.write(plugin_sources={"demo": "~/plugins/demo"})
        cfg = load_config(self.path)
        self.assertTrue(cfg["plugin_sources"]["demo"].endswith("plugins/demo"))

    def test_rejects_non_object_plugin_sources(self):
        self.write(plugin_sources=["demo"])
        with self.assertRaisesRegex(ConfigError, "plugin_sources 必须是对象"):
            load_config(self.path)
